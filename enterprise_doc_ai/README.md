# Enterprise Document AI: evidence-first retrieval and evaluation

An independent AI Engineer portfolio case study inspired by publicly described enterprise AI requirements. It is NOT a component of the proprietary CMC C-Agent product, and uses ONLY fictional Alpha/Beta company documents.

## What is implemented

| AI engineering capability | Implementation | Boundaries |
| --- | --- | --- |
| Vietnamese/English retrieval | engine.py: unicode tokenization, BM25 and character n-grams | Local deterministic sparse baselines |
| Hybrid retrieval | Reciprocal Rank Fusion of word BM25 and char n-grams | No trained cross-encoder reranker |
| Optional real embeddings | Dependency-injected Encoder and OptionalSentenceEncoder | Requires model download; not measured in offline benchmark |
| Document access scopes | Tenant, role, effective-date and version filtering before ranking | API now requires local HMAC-signed, short-lived bearer tokens; **not production OIDC** |
| Document Intelligence | Local PDF/DOCX/text ingestion, structured invoice parsing with source/page/span | Regex baseline; optional local Tesseract OCR, not benchmarked |
| RAG evidence | GroundedQA returns verbatim excerpts with page/version/source | Extractive mode; claim-level entailment not established |
| Optional LLM generation | llm.py: OpenAI-compatible opt-in adapter, mocked integration tests and citation ID validation | API credentials required for real inference; citations checked for membership, NOT factual entailment |
| Guarded agent workflow | Retrieve, prepare draft, independent approval | Zero external side effects, transient state |
| Evaluation | 80 labelled synthetic baseline questions plus a separate 28-case adversarial challenge set, ablations, retrieval metrics, abstention and isolation | Public synthetic fixture, NOT a blind/enterprise benchmark |
| Integration | CLI and optional FastAPI with OpenAPI docs | Local signed bearer identity and explicit scopes; **not production IAM** |
| CI | Linux and Windows / Python 3.11 and 3.12, recorded benchmark artifacts | No GPU needed; OCR and dense model quality not tested |

## Data

24 passages from two fictitious tenants and 80 manually authored baseline questions: 64 answerable and 16 negative (unanswerable, forbidden role or other tenant). The corpus includes an outdated HR policy, a newer replacement, a two-page security policy, payroll access limits and a malicious prompt-injection string as untrusted document data. A public dev/test partition is provided for reproducibility, but is not a blinded holdout. No real CMC employee/customer document is included.

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

**SECURITY CHANGE (Chief Engineer final review):** User-controlled `X-Demo-Tenant`, `X-Demo-Roles` and `X-Demo-Subject` are no longer accepted as identity. All sensitive endpoints require a locally signed, expiring HMAC-SHA256 bearer token. There is no HTTP mint endpoint. This is NOT OAuth/OIDC or a production identity provider and should be used on localhost with fictional documents only.

To run the API, generate a private signing key (minimum 32 bytes) locally and store it in the shell environment variable `ENTERPRISE_DOC_AI_DEMO_SECRET`. Do not commit it. Start `uvicorn enterprise_doc_ai.api:app --host 127.0.0.1 --port 8000`. Operator-side example for an authorized local demo user:

    python -m enterprise_doc_ai.auth mint --tenant alpha --subject alice --roles employee --scopes read --ttl 900

Send its output as an HTTP `Authorization: Bearer <token>` header to `/ask`. Invoice extraction additionally needs `finance` role and `extract` scope. Workflow drafting needs `review` scope; approval needs distinct `approver` role, `approve` scope and permission to read every cited document. `/health` confirms liveness, while `/ready` fails when the signing key is missing. Tokens expire within one hour; there is no revocation registry, OIDC or persistent audit. Do not expose the demo publicly.

## Opt-in LLM generation with citation membership checking

The module enterprise_doc_ai/llm.py provides OpenAIChatClient and CitationCheckedRAG. It first applies the same tenant/role and weak-evidence gates as offline retrieval, then sends only allowed retrieved evidence to the external model. It rejects responses claiming citation IDs outside that evidence set. It deliberately reports status generated_unverified, because citation membership is NOT proof that the answer is true. Network/model failures fail closed. Mock-LLM integration tests run without an API key; actual remote calls require OPENAI_API_KEY.

To try it only with explicitly permitted synthetic data and a configured API key:

    python -c "from enterprise_doc_ai.engine import *; from enterprise_doc_ai.llm import *; x=EnterpriseIndex(load_corpus()); print(CitationCheckedRAG(x,OpenAIChatClient()).ask('lưu trữ API key Secret Manager', Principal('alpha',frozenset({'employee'}))))"

Do not send sensitive real documents to an external service without data-processing authorization.

Read the [reproducible evaluation report](docs/EVALUATION_REPORT.md) for measured results and failure analysis.

## Optional true semantic embedding and OCR adapters

    python -m pip install -r enterprise_doc_ai/requirements-semantic.txt
    python -m pip install -r enterprise_doc_ai/requirements-ocr.txt

OptionalSentenceEncoder loads a multilingual SentenceTransformer. The offline experiments do not use or evaluate it. The local OCR adapter uses PyMuPDF, PIL and pytesseract, requiring an installed Tesseract executable and Vietnamese language models. The default benchmarks do not evaluate OCR accuracy. Do not claim measured neural or OCR performance.

## Evaluation and reproducibility evidence

The evaluation job checks Python 3.11 and 3.12 on Ubuntu and Windows, runs unit and HTTP tests, and produces a downloadable `enterprise_doc_ai_test.json` artifact. The **latest results must be read from the GitHub Actions artifact**, not inferred from README numbers. A good interview discussion compares retrieval success against the ability to abstain: a high Hit@3 cannot establish answer factuality, and aggressive abstention may reduce legitimate coverage.

Optional LLM generation is available in `llm.py` through an explicitly configured server-side API key. Its tests use mocked responses to validate citation membership and failure behavior. CI does **not** call a remote LLM; model quality has not been measured here.

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

Production OIDC authentication, durable audit, encrypted storage, vector DB, cross-encoder reranker, human-reviewed Vietnamese benchmarks, claim-level citation entailment, real OCR test suite, network load test, monitoring/telemetry and production deployment remain future work.

This case study is an AI-assisted software engineering portfolio. The applicant should review, execute and understand all code before claiming personal implementation competence.


## 28-case adversarial challenge (public, not blinded)

The added challenge is explicitly separate from the original 80-case baseline. It covers bilingual paraphrases, restricted roles, cross-tenant questions, prompt injection strings and out-of-domain requests. Reproduce using `python -m enterprise_doc_ai.benchmark --suite stress --split test --method all`. The first adversarial run had **90% Hybrid Hit@3 but 0% evidence-provided rate for 10 positives**, while abstaining on 18/18 negatives. Do not suppress this severe coverage failure: retrieval success and answerability are not synonymous. Improvements to semantic retrieval and evidence verification must be validated on an independent blind sample.
