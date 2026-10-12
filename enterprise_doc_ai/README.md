# Enterprise Document AI: evidence-first retrieval and evaluation

An independent AI Engineer portfolio case study inspired by publicly described enterprise AI requirements. It is NOT a component of the proprietary CMC C-Agent product, and uses ONLY fictional Alpha/Beta company documents.

## What is implemented

| AI engineering capability | Implementation | Boundaries |
| --- | --- | --- |
| Vietnamese/English retrieval | engine.py: unicode tokenization, BM25 and character n-grams | Local deterministic sparse baselines |
| Hybrid retrieval | Reciprocal Rank Fusion of word BM25 and char n-grams | No trained cross-encoder reranker |
| Optional real embeddings | Dependency-injected Encoder and OptionalSentenceEncoder | Requires model download; not measured in offline benchmark |
| Document access scopes | Tenant, role, effective-date and version filtering before ranking | Demo API does NOT authenticate requests |
| Document Intelligence | Local PDF/DOCX/text ingestion, structured invoice parsing with source/page/span | Regex baseline; optional local Tesseract OCR, not benchmarked |
| RAG evidence | GroundedQA returns verbatim excerpt with page/version/source | No LLM generation, claim-level faithfulness not established |
| Guarded agent workflow | Retrieve, prepare draft, independent approval | Zero external side effects, transient state |
| Evaluation | 80 labelled bilingual-oriented questions, ablations, retrieval metrics, abstention and isolation | Public synthetic fixture, NOT a blind/enterprise benchmark |
| Integration | CLI and optional FastAPI with OpenAPI docs | Demo API HTTP headers are NOT secure RBAC |
| CI | Linux and Windows / Python 3.11 and 3.12, recorded benchmark artifacts | No GPU needed; OCR and dense model quality not tested |

## Data

24 passages from two fictitious tenants and 80 manually authored questions: 64 answerable and 16 negative (unanswerable, forbidden role or other tenant). The corpus includes an outdated HR policy, a newer replacement, a two-page security policy, payroll access limits and a malicious prompt-injection string as untrusted document data. A public dev/test partition is provided for reproducibility, but is not a blinded holdout. No real CMC employee/customer document is included.

## Quick run from repository root

Python 3.11 or newer. All commands below run without an API key or GPU:

    python -m enterprise_doc_ai.cli search "Hồ sơ onboarding cần nộp ở đâu?"
    python -m enterprise_doc_ai.cli ask "PeopleHub nhận hồ sơ nhân sự thế nào?" --tenant alpha --roles employee
    python -m enterprise_doc_ai.cli ask "Bảng lương PayFlow" --tenant alpha --roles hr
    python -m enterprise_doc_ai.cli workflow "Chiết khấu trên mười phần trăm ai phê duyệt?" --tenant alpha --roles sales
    python -m enterprise_doc_ai.cli invoice enterprise_doc_ai/data/invoice_clean.txt
    python -m unittest discover -s enterprise_doc_ai/tests -v
    python -m enterprise_doc_ai.benchmark --split test --method all --k 3 --output enterprise_doc_ai_test.json

## Optional HTTP API

    python -m pip install -r enterprise_doc_ai/requirements-api.txt
    uvicorn enterprise_doc_ai.api:app --host 127.0.0.1 --port 8000

Visit http://127.0.0.1:8000/docs. Operations: /health, /ask, /invoice/extract, /workflow/prepare and /workflow/approve.

IMPORTANT: X-Demo-Tenant, X-Demo-Roles, X-Demo-Subject are untrusted caller-supplied TEST headers. No real login is implemented. Do not expose this demo to a public network or use real confidential information.

## Optional true semantic embedding and OCR adapters

    python -m pip install -r enterprise_doc_ai/requirements-semantic.txt
    python -m pip install -r enterprise_doc_ai/requirements-ocr.txt

OptionalSentenceEncoder loads a multilingual SentenceTransformer. The offline experiments do not use or evaluate it. The local OCR adapter uses PyMuPDF, PIL and pytesseract, requiring an installed Tesseract executable and Vietnamese language models. The default benchmarks do not evaluate OCR accuracy. Do not claim measured neural or OCR performance.

## Evaluation interpretation

Hit@3, Recall@3, MRR@3 and nDCG@3 rank labelled document FAMILIES, deduplicating pages. Negative abstention is measured from a conservative extractive support gate. Access leakage counts identify results violating the TRUSTED Principal's tenant and roles. Effective-date checks identify future policy exposures. Median latency reflects local runner hardware and excludes model downloads, external APIs, and OCR.

The experiments report retrieval and evidence routing, not generated answer truthfulness. Neither 100% toy ranking nor zero synthetic leakage would imply production readiness. Review the generated evaluation JSON in the Enterprise Document AI GitHub Actions artifact, especially negative-case failures. The test split is public and not independently blinded.

See docs/THREAT_MODEL.md for security gaps, and docs/INTERVIEW_GUIDE.md for interview explanations.

## Architecture

    synthetic corpus -> typed passage metadata -> tenant/role/date/version filter
                                                 |
                            +--------------------+-----------------+
                            |                                      |
                         word BM25                           character BM25
                            |                                      |
                            +--------------- RRF ------------------+
                                                 |
                                      source-linked top-k
                                                 |
                           +---------------------+---------------------+
                           |                                           |
                      GroundedQA                                 ReviewWorkflow
                      quote + source                    retrieve -> draft -> human approve
                           |                                           |
                          CLI/API                             no external execution

    sample invoices -> parser -> regex validated fields -> source/page/span -> needs_review
    80 labelled cases -> benchmarks -> ranking + abstention + isolation -> CI artifacts

## Not completed and not claimed

Real business authentication, signed roles, durable audit, encrypted storage, vector DB, cross-encoder reranker, human-reviewed Vietnamese benchmarks, claim-level citation entailment, real OCR test suite, network load test, monitoring/telemetry and production deployment remain future work.

This case study is an AI-assisted software engineering portfolio. The applicant should review, execute and understand all code before claiming personal implementation competence.
