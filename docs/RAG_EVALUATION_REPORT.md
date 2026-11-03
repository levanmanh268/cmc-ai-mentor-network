# RAG Evaluation Report

**Dataset:** bundled 3-document Markdown demo corpus; 14 hand-authored questions (9 supported, 5 outside corpus).  
**Method:** deterministic TF-IDF retrieval and offline excerpts; no API key or network.  
**Command:** `python -m scripts.evaluate_rag`  
**Evaluation code:** `scripts/evaluate_rag.py`; protocol details in [RAG_EVALUATION.md](RAG_EVALUATION.md).

## Result captured in this working session

| Metric | Result | Definition |
| --- | ---: | --- |
| Retrieval Recall@3 | 9/9 (100%) | Supported cases whose expected source appears in top 3 |
| Citation correctness | 10/10 (100%) | Offline excerpt citation IDs mapped to the expected source |
| Answer correctness proxy | 9/9 (100%) | Pre-labeled evidence terms present in cited retrieved chunk text |
| Out-of-scope refusal | 5/5 (100%) | No source and `no-evidence` for unsupported prompts |

The evaluator originally surfaced an irrelevant document for one supported query (10/11 citation references correct at the prior threshold). The default TF-IDF minimum score was changed from `0.06` to `0.08`; rerunning this same small set retained 9/9 expected sources and removed that false-positive citation.

## Interpretation and limitations

- The answer score is an **evidence proxy**, not human grading of generated answers.
- No live LLM output was evaluated. Citation ID validity and source mapping do not establish claim-level entailment or factual correctness.
- Questions were authored against the same three demo documents, so results are in-sample and likely optimistic.
- Five negative questions do not characterize false refusal across synonyms, new vocabulary, or other languages.
- Prompt-injection tests inspect the prompt contract using a fake provider; no robustness guarantee follows.
- Treat metrics as a repeatable smoke benchmark, not a general accuracy claim or production SLA.

The exact local suite commit and runtime evidence are in [TEST_REPORT.md](TEST_REPORT.md). GitHub Actions has not run this uncommitted working tree.
