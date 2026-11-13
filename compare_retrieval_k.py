"""Compare two paired A-MEM evaluation outputs from a retrieval-k experiment.

Usage: python3 compare_retrieval_k.py baseline.json modified.json
"""

import argparse
import json
import statistics
from pathlib import Path


METRICS = ("f1", "exact_match")


def load_run(path):
    with Path(path).open(encoding="utf-8") as handle:
        run = json.load(handle)
    required = ("model", "backend", "dataset", "ratio", "seed", "retrieve_k", "individual_results")
    missing = [key for key in required if key not in run]
    if missing:
        raise ValueError(f"{path}: missing metadata: {', '.join(missing)}")
    rows = {}
    for row in run["individual_results"]:
        key = (row["sample_id"], row["qa_index"])
        if key in rows:
            raise ValueError(f"{path}: duplicate question {key}")
        rows[key] = row
    if not rows:
        raise ValueError(f"{path}: no evaluated questions")
    if run.get("llm_failures"):
        raise ValueError(f"{path}: LLM failures occurred; inspect the run before comparison")
    return run, rows


def compare(base_path, changed_path):
    base, base_rows = load_run(base_path)
    changed, changed_rows = load_run(changed_path)
    controlled = ("model", "backend", "embedding_backend", "metric_set", "dataset", "ratio", "seed", "memory_scope",
                  "legacy_c5_reference", "refresh_index", "max_questions")
    differences = [key for key in controlled if base.get(key) != changed.get(key)]
    if differences:
        raise ValueError("Runs differ in controlled settings: " + ", ".join(differences))
    if base["retrieve_k"] == changed["retrieve_k"]:
        raise ValueError("retrieve_k did not change")
    if base_rows.keys() != changed_rows.keys():
        raise ValueError("Runs evaluated different questions")
    for key in base_rows:
        for field in ("question", "reference", "category"):
            if base_rows[key][field] != changed_rows[key][field]:
                raise ValueError(f"Question {key} differs in {field}")

    lines = [
        "# A-MEM retrieval-k comparison",
        "",
        f"- Model: {base['model']} ({base['backend']})",
        f"- Embedding backend: {base.get('embedding_backend', 'unspecified')}",
        f"- Metric set: {base.get('metric_set', 'unspecified')}",
        f"- Dataset: {base['dataset']}; ratio: {base['ratio']}; seed: {base['seed']}",
        f"- Paired questions: {len(base_rows)}",
        f"- Baseline k: {base['retrieve_k']}; modified k: {changed['retrieve_k']}",
        "",
        "| Metric | Baseline mean | Modified mean | Change |",
        "| --- | ---: | ---: | ---: |",
    ]
    for metric in METRICS:
        before = [float(base_rows[key]["metrics"][metric]) for key in sorted(base_rows)]
        after = [float(changed_rows[key]["metrics"][metric]) for key in sorted(base_rows)]
        before_mean, after_mean = statistics.mean(before), statistics.mean(after)
        lines.append(f"| {metric} | {before_mean:.4f} | {after_mean:.4f} | {after_mean-before_mean:+.4f} |")
    lines.extend([
        "",
        "These are subset results. Compare with paper values only when the model, dataset, evaluation",
        "protocol, and scoring definition match. Record repeated runs separately if using stochastic decoding.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", help="JSON result with the original retrieval k")
    parser.add_argument("modified", help="JSON result with the changed retrieval k")
    parser.add_argument("--output", help="Write the Markdown comparison to this path")
    args = parser.parse_args()
    report = compare(args.baseline, args.modified)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
