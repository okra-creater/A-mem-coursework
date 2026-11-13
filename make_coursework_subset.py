"""Create a small, evidence-aligned LoCoMo subset for the retrieval-k study."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "locomo10.json"
TARGET = ROOT / "results_coursework" / "subset.json"
QUESTION_INDICES = (0, 1, 2, 3, 4, 5, 6, 82, 83, 84)
SESSIONS = (1, 2)


def main():
    samples = json.loads(SOURCE.read_text(encoding="utf-8"))
    sample = samples[0]
    questions = [sample["qa"][index] for index in QUESTION_INDICES]
    allowed = ("D1:", "D2:")
    for index, question in zip(QUESTION_INDICES, questions):
        evidence = question.get("evidence", [])
        if not evidence or any(not str(item).startswith(allowed) for item in evidence):
            raise ValueError(f"Question {index} needs evidence outside selected sessions")
    conversation = {
        "speaker_a": sample["conversation"]["speaker_a"],
        "speaker_b": sample["conversation"]["speaker_b"],
    }
    for session in SESSIONS:
        name = f"session_{session}"
        conversation[name] = sample["conversation"][name]
        conversation[f"{name}_date_time"] = sample["conversation"][f"{name}_date_time"]
    subset = {**sample, "qa": questions, "conversation": conversation}
    TARGET.parent.mkdir(exist_ok=True)
    TARGET.write_text(json.dumps([subset], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    turns = sum(len(conversation[f"session_{session}"]) for session in SESSIONS)
    print(f"Wrote {TARGET}: {len(questions)} questions, {turns} turns, {len(SESSIONS)} sessions")


if __name__ == "__main__":
    main()
