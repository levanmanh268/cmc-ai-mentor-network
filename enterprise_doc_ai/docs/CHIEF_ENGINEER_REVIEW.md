# Chief Engineer Release Review | 12 October 2026

## Release verdict

ACCEPTABLE AS A LOCAL INTERVIEW PORTFOLIO DEMO after same-commit CI passes. NOT APPROVED FOR PRODUCTION DEPLOYMENT. Independent student case study, not CMC's proprietary product.

## Security and engineering findings

1. CRITICAL: Caller-controlled X-Demo-Tenant and X-Demo-Roles allowed impersonation. Mitigated for the local demo by HMAC-SHA256 short-lived bearer identity, validated issuer/audience, role and scope checks. The signing key never passes through an HTTP mint endpoint. Covered by test_auth.py and test_api.py. Residual: no OIDC, revocation registry, IAM enforcement, secure production deployment or audit persistence.
2. HIGH: Approval state could race and persist in unbounded RAM. Mitigated by process-local locking, TTL, bounded tasks, random IDs, independent approver and current-policy rechecks. Covered by test_workflow.py. Residual: no persistent, distributed, multi-worker workflow guarantee.
3. HIGH: Metadata and embedding values lacked strict validation. Mitigated with bounded typed corpus and nonfinite embedding rejection; tests in test_engine.py. Residual: document parsers still require production sandboxing.
4. HIGH: Citation IDs were checked for membership, NOT claim entailment. Outputs explicitly remain generated_unverified and the demo does not claim factual verification.
5. HIGH: Initial 80-case public fixture was too easy. Added a separate public 28-case adversarial suite with 10 positives and 18 negative or unauthorized cases. It is NOT a blinded scientific benchmark.
6. MEDIUM: Dense multilingual embeddings, neural OCR quality, vector persistence and LLM generation quality are NOT measured in the offline benchmark.
7. MEDIUM: No independent load, production deployment, cryptographic audit or real enterprise data evaluation.

## Recorded first adversarial results

Hybrid document-family Hit@3: 9/10 (90%).
Evidence accepted among 10 answerable questions: 0/10 (0%).
Correct abstention among 18 labelled negative questions: 18/18 (100%).
Constructed-principal access predicate violations: 0 observed.

Critical conclusion: 90% retrieval DOES NOT imply acceptable answers. A strict lexical support gate blocks bilingual paraphrases and fails all 10 positive challenges. Do not tune on the public challenge and call it a blind generalization result. Follow-up research: independently annotated Vietnamese cases, semantic retrieval and reranking, claim-level NLI/attribution and held-out calibration.

## Reproduction

From root with Python >= 3.11:

    python -m unittest discover -s enterprise_doc_ai/tests -v
    python -m enterprise_doc_ai.benchmark --split test --method all
    python -m enterprise_doc_ai.benchmark --suite stress --split test --method all
    python -m enterprise_doc_ai.cli invoice enterprise_doc_ai/data/invoice_clean.txt

For optional FastAPI: install enterprise_doc_ai/requirements-api.txt, set ENTERPRISE_DOC_AI_DEMO_SECRET to a unique >=32-byte secret, bind only to 127.0.0.1, and use operator-side token minting documented in README. The /ready endpoint must fail if signer not configured; all data routes require scopes. Default tests never call external LLM endpoints.

## Go/no-go checklist

Release only when (A) all 4 matrix jobs on Ubuntu/Windows Python 3.11/3.12 pass, (B) repository-wide CI passes, both on identical final commit, (C) security tests deny missing/forged tokens and unauthorized tenants, (D) benchmark artifact records both high false refusal and negative abstention, (E) README and threat model describe residual defects, (F) app is labelled local demo only.

## Suggested 90-second interview narrative

An enterprise AI assistant must respect document permissions before retrieval, carry source and version provenance and refuse unsupported claims. I built a demonstrator for access-scoped BM25 and char-trigram retrieval with reciprocal-rank fusion, reproducible synthetic evaluations, invoice extraction, and a review-gated workflow. An independent adversarial suite revealed a 90% retrieval hit rate but zero positive evidence acceptance from an overly conservative lexical gate. I have not hidden that defect. I would first measure real multilingual semantic retrieval and source entailment on a blind labelled set; then implement trusted OIDC roles, distributed state and telemetry before proposing production release.

AI assistance was used in implementation. Applicant must personally rerun and explain all components. GitHub CI is necessary evidence but can never prove zero defects or guarantee hiring.
