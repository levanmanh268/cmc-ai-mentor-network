# RAG Evaluation Report

**Dataset:** `nfr-09-v1`, 31 synthetic cases over three bundled demo Markdown documents (18 supported, 13 outside the corpus).  
**Run:** [CI run 41695395834](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/41695395834), tested code SHA `d50895c3c447fb1e667af02e338be261a9952c5d`.  
**Method:** deterministic TF-IDF retrieval and offline excerpts; no API key, network, or live LLM.  
**Command:** `python -m scripts.evaluate_rag`; protocol: [RAG_EVALUATION.md](RAG_EVALUATION.md).

| Metric | Result | Definition |
| --- | ---: | --- |
| Retrieval Recall@3 | 18/18 (100%) | Supported cases whose expected source appears in top three |
| Citation source mapping | 20/20 (100%) | Citation IDs map to retrieved sources, with the expected source cited for each positive case |
| Answer evidence-term proxy | 18/18 (100%) | Pre-labeled terms appear in cited retrieved excerpt text |
| No-evidence refusal | 13/13 | Unsupported prompts produce no source and `no-evidence` mode |

## Interpretation and limitations

- Cases are synthetic and written against the same three demo documents; there is no blind split or independent human labeling.
- Citation source mapping does not establish that a source entails the cited claim.
- The answer score is an evidence-term proxy, not semantic grading of generated answers.
- No live Groq output, general knowledge accuracy, hallucination rate, or production performance was measured.
- Prompt-injection tests verify prompt boundaries with fake clients; they do not prove adversarial robustness.

For the independent reviewer-labeled benchmark, see [#83](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/83). Multi-source citation regression tests are tracked in [#163](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/163).
