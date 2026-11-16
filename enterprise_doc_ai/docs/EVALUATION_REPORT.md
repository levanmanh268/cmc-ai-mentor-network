# Reproducible evaluation report, October 12, 2026

This report records **actual GitHub Actions outputs**, not predicted performance. Source code and reproducible commands are in the project root. The dataset is **synthetic, tiny and public**, and the test partition was observed during development; it is NOT an independent blind benchmark.

## Experiment

- Corpus: 24 manually written Vietnamese-language passage fixtures about 2 fictional tenants, including a policy revision and two-page document.
- QA: 80 human-authored fixture questions; development has 56 (48 answerable + 8 negative), test has 24 (16 answerable + 8 negative).
- Methods: word BM25, character trigram BM25, reciprocal-rank hybrid. Same small source corpus and same ACL/version filter.
- GroundedQA: extractive passage, not an LLM-generated answer, with conservative IDF-weighted query-term coverage gate set to 0.55. No API/network/GPU.
- Definition: Hit@3, MRR@3, nDCG@3 consider document-family relevance, NOT factual entailment or page-level answer precision.
- Negative abstention: fraction of explicitly labelled negative questions where the QA component declined to provide an excerpt.
- Access leakage count: how often any returned passage failed the constructed test Principal's role+tenant predicate. **At the time of these baseline results, the HTTP API was not authenticated.** The subsequent local-demo hardening uses HMAC-signed bearer tokens; this benchmark itself tests constructed Principal objects, not an enterprise IAM system.

## Recorded test metrics (16 positives, 8 negatives)

| Method | Hit@3 | MRR@3 | nDCG@3 | Evidence provided on positives | Negative abstention | Simulated access leakages |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BM25 | 100% | 96.88% | 97.69% | 81.25% | 100% (8/8) | 0 |
| Char BM25 | 100% | 96.88% | 97.69% | 81.25% | 100% (8/8) | 0 |
| Hybrid RRF | 100% | 96.88% | 97.69% | 81.25% | 100% (8/8) | 0 |

## Recorded dev metrics (48 positives, 8 negatives)

All three sparse methods reported Hit@3=100%, MRR@3=100%, nDCG@3=100%, evidence-provided rate 85.42% and negative abstention 100% (8/8), with zero simulated access leakages.

## Key error analysis and tradeoff

Before introducing the IDF-weighted evidence coverage gate, the hybrid method **refused only 25% of negative test cases (2/8)** despite a high Hit@3. This shows why retrieval accuracy alone is not a reliable answer-quality indicator.

After the evidence gate, the same test set showed **100% negative abstention (8/8)** while **81.25% of positive test cases were accepted (13/16)**. In other words, three labelled-answerable questions were conservatively refused. This is a sensitivity/specificity tradeoff, **not proof of zero hallucination**. The threshold was changed after prior aggregate test results had been viewed; therefore the test set is no longer truly held out. Do not use these numbers as scientific generalization evidence.

Notably, hybrid did not outperform pure BM25 on this particular easy synthetic corpus. Claiming improvement would be incorrect. Larger independent Vietnamese datasets, paraphrases, OCR documents, document-level entailment annotation and mixed adversarial cases are necessary.

## Engineering checks

GitHub Actions Linux and Windows / Python 3.11 and 3.12, 35 offline unit/API/mock-LLM tests on the evaluated commit. Checked source/citation handling, version cutover, role/tenant scoping, red-team sample strings, malformed invoices, audit approval workflows, and model-error fail-closed behavior. Optional semantic model weights, scanned OCR correctness and real external LLM outputs were NOT measured.

Re-run:

    python -m unittest discover -s enterprise_doc_ai/tests -v
    python -m enterprise_doc_ai.benchmark --split dev --method all --output enterprise_doc_ai_dev.json
    python -m enterprise_doc_ai.benchmark --split test --method all --output enterprise_doc_ai_test.json

The workflow uploads the JSON reports as artifacts. Latency depends on the host runner, and excludes external models, network and OCR.

## Next engineering experiments

1. Construct a truly blind, reviewer-annotated Vietnamese corpus of hundreds of diverse enterprise document queries with versioned labels and access metadata.
2. Measure multilingual sentence embeddings against BM25, hybrid and optional cross-encoder reranking with paired bootstrap uncertainty.
3. Evaluate scanned Vietnamese invoices with OCR character error rate and per-field extraction precision, recall and exact match.
4. Separate retrieval errors from generation faithfulness via claim-level source entailment and out-of-context guardrails.
5. Implement real OIDC identity, authenticated tenant scoping, audit persistence and pre-deployment security testing before hosting online.

The case study demonstrates applied AI engineering methodology, not enterprise deployment readiness.
