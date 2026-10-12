# Interview guide for AI Engineer Intern

## Suggested 90-second explanation

I built an independent, offline-first enterprise document AI prototype, focused on measurable retrieval, evidence provenance and access scoping. Each passage has tenant, role, page, version and effective-date metadata. The core ranks only visible passages, compares word BM25, character BM25 and reciprocal rank fusion, and extracts short verbatim excerpts with citations rather than presenting unverified generated answers. It includes invoice field extraction with exact spans, a human approval-gated workflow, optional real embeddings/OCR, and FastAPI integration. I benchmarked methods on 80 published fictional questions. This is a study, NOT CMC proprietary software or real-world production accuracy.

## Likely follow-ups

1. Why BM25 versus char n-grams for Vietnamese? What happens without word segmentation?
2. What is reciprocal rank fusion? Explain sum of 1/(60+rank), only ranks with positive matching scores.
3. What can go wrong if access filtering occurs AFTER vector retrieval?
4. What is the difference between retrieval relevance, grounded citation and factual entailment?
5. Why are 80 public synthetic cases insufficient to validate an enterprise assistant? How would you build a blind real QA set?
6. How do invoice fields maintain source provenance? What happens with missing or two contradictory totals?
7. What does the workflow execute? It creates a draft and requires separate approval; external writes are DISABLED.
8. What is missing to ship securely? Verified authentication, tenant isolation at storage level, durable audit logs, real OCR QA and prompt attack testing.
9. How would you compare dense embeddings, hybrid retrieval and a cross-encoder on Vietnamese policy Q&A?
10. Which error cases would you show? The first negative where the model fails to abstain, and any ranker regression.

## Demonstrate intellectual ownership

Read and run every source module, reproduce the CI reports, then explain an observed failure and propose a measured change. The code was built with AI assistance; do not claim untested capabilities or take credit for work you cannot explain.

11. Explain the evidence-gate tradeoff: test-set negative abstention improved while some answerable cases were refused. A cautious enterprise assistant must expose that precision/coverage compromise.
12. If the LLM produces a made-up citation ID, the integration rejects its output. Why does valid citation membership still not guarantee factual correctness?

Technical results and reproduction: docs/EVALUATION_REPORT.md.
