# A-MEM small-scope reproducibility report

Date: 13 November 2026. This is a short report draft for FTEC5660. The student's name,
student ID, GitHub link, and recorded presentation link still need to be added.

## Project and target

A-MEM constructs and evolves linked notes from a conversation, retrieves relevant
notes, and answers questions. The [paper's Table 1](https://arxiv.org/html/2502.12110v11)
reports LoCoMo question-answering F1 by category. This experiment tests a small,
explicit subset of that capability: can the repository build memories and answer
ten evidence-aligned LoCoMo questions? It then measures the effect of changing
retrieval count from `k=10` to `k=5`.

## Setup and scope

- Repository starting commit: `f9a173d`; experiment branch: `coursework/retrieval-k-study`.
- macOS 27.0.1, arm64, Python 3.11.9; dependencies installed from `requirements.txt`
  in `.venv` (including OpenAI SDK 3.50.0, PyTorch 2.15.0, and
  sentence-transformers 6.3.0).
- Dataset: `data/locomo10.json`, first conversation, sessions 1–2 (35 turns).
  `make_coursework_subset.py` selects original question indices
  0–6 and 82–84. All ten questions cite evidence in the selected sessions.
  Category counts: multi-hop 2, temporal 4, open-domain 1, single-hop 3.
- LLM: DeepSeek `deepseek-flash`, OpenAI-compatible endpoint
  `https://api.deepseek.com`, non-thinking mode, `max_tokens=1000`.
  Temperature is 0.7 for these categories. No category-5 question is included.
  The robust repository prompts were used without changing their text.
- Embeddings: deterministic 384-feature hashing encoder selected through
  `AMEM_EMBEDDING_BACKEND=hashing`. Hugging Face's `all-MiniLM-L6-v2` model
  could not be downloaded in this environment.
- Metrics: repository token-set F1 and exact match, with
  `AMEM_LIGHT_METRICS=1`. Each result is the mean over the same ten questions.
  Three repeated paired trials used the same memory cache and seed 42.
- The DeepSeek key is stored only in ignored `.env`; no key is in Git.

## Results

| Trial | k=10 F1 | k=5 F1 | Paired change | k=10 exact match | k=5 exact match |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 36.16% | 27.59% | -8.57 pp | 20% | 20% |
| 2 | 36.16% | 27.59% | -8.57 pp | 20% | 20% |
| 3 | 36.16% | 31.59% | -4.57 pp | 20% | 20% |
| Mean | **36.16%** | **28.92%** | **-7.24 pp** | **20%** | **20%** |
| Sample SD across trials | 0.00 pp | 2.31 pp | 2.31 pp | 0 pp | 0 pp |

All six runs evaluated the same ten questions. The second through sixth runs
loaded the memory cache created by trial 1. The outputs report no absorbed LLM
failures. The F1 decrease is a descriptive observation on this small subset,
not a statistical claim about all LoCoMo questions.

For context, Table 1 of the paper reports A-MEM with **GPT-4o-mini** at 27.02%
multi-hop F1, 45.85% temporal F1, 12.14% open-domain F1, and 44.65%
single-hop F1 on the full LoCoMo evaluation. Those are **not direct targets for
numeric replication** here: this run changes the LLM, embedding method,
dataset size, prompt format (robust plain-text script), and metric selection.
The paper also adjusts `k` for some categories, whereas this experiment uses
one `k` across all selected questions. See the paper's [implementation details
and Table 1](https://arxiv.org/html/2502.12110v11).

## Modification and interpretation

The isolated experimental change within each pair is `retrieve_k`: 10 versus
5. The repository's existing parameter is exposed in a short paired workflow.
`compare_retrieval_k.py` rejects comparisons with different questions,
references, model, dataset, evaluation settings, or absorbed LLM failures.
Dataset-content hashes separate memory caches, preventing a full-dataset cache
from contaminating this subset. The local hashing encoder and DeepSeek backend
are documented environment adaptations applied equally to both arms.

On these ten questions, retrieving fewer notes lowered mean F1 by 7.24
percentage points. Exact match did not change. This suggests that some useful
context was lost when `k` decreased, but the subset is too small to generalize.

## Debug diary and limits

1. The machine initially lacked repository dependencies and an LLM backend.
   A private `.env` was created and the DeepSeek connection was verified.
2. The original sentence-transformer download failed at Hugging Face.
   The evaluation was rerun with a local hashing encoder and only F1/exact
   match, and these changes were recorded as deviations from the paper.
3. The full first conversation has 419 turns; a fixed 35-turn, ten-question
   evidence-aligned subset kept API calls and runtime manageable.
4. The experiment did not reproduce the paper's full-table numbers or compare
   A-MEM with another memory system. Token usage and API cost were not logged.
   The submitted report should state these limits plainly.

## Reproduction and submission

Run the three commands in the README's **Small reproducibility experiment**
section after installing dependencies and configuring `.env`. The ignored
`results_coursework/` directory contains the six JSON outputs and paired
comparisons on this machine. The GitHub submission should be a student-owned
fork or repository with these commits and a clear README. A separate Zoom
recording of at most 15 minutes is also required by the assignment.
