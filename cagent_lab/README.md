# C-Agent Capability Lab

**AI Engineer Intern portfolio extension** for [CMC AI Mentor Network](../README.md).

A small, verifiable AI capability laboratory covering **document ingestion, RAG, retrieval benchmarks, real optional embeddings, guarded agent tools, optional LLM generation, and a FastAPI integration**. The source documents are *fictional evaluation fixtures*, never official CMC documentation. This is an independent module, not a claim that it is the enterprise C-Agent product.

## Feature to job-description mapping

| Requested C-Agent skill | Implemented artifact |
| --- | --- |
| RAG, retrieval, NLP | `core.py` BM25, TF-IDF, chunking, source-linked grounded extraction |
| Embeddings | `DenseIndex` and actual `SentenceTransformerEncoder` (optional install) |
| Prompt engineering / LLM | `llm.py` optional OpenAI API generation with untrusted-context prompt boundary |
| Document Intelligence | .md/.txt, optional .pdf/.docx parsing with a file-size limit |
| Agent capability | `SafeAgent` with explicit tool allowlist and no side effects |
| Evaluation | `evaluate.py`, 10 labelled synthetic questions, hit@k, MRR@k, nDCG@k and latency |
| Integration | FastAPI `/health`, `/query`, `/agent` plus offline CLI |
| Software quality | Stdlib unit tests, GitHub Actions |

## Run without API keys (Python 3.11+)

From the repository root:

```bash
python -m cagent_lab.cli "Where must API keys be stored?"
python -m cagent_lab.evaluate --method bm25 --k 3
python -m cagent_lab.evaluate --method tfidf --k 3
python -m unittest discover -s cagent_lab/tests -v
```

No GPU or cloud account is needed for these commands.

## Optional REST API

```bash
python -m pip install -r cagent_lab/requirements-api.txt
uvicorn cagent_lab.api:app --port 8000
```

Example: `curl -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d '{"question":"Where must API keys be stored?","k":3}'`. API documentation is served at `http://127.0.0.1:8000/docs`.

## Actual semantic embeddings (optional)

```bash
python -m pip install -r cagent_lab/requirements-embeddings.txt
python -c "from cagent_lab.core import *; from cagent_lab.evaluate import load_corpus; d=load_corpus('cagent_lab/data/knowledge'); i=DenseIndex(d,SentenceTransformerEncoder()); print(i.search('Where do we keep API keys?',3))"
```

The multilingual model downloads on first use. Embedding scores are distinct from BM25 scores. Do not compare raw scores across retrieval methods or assume the score threshold transfers.

## Experiment protocol

- Corpus: 3 **synthetic** English Markdown documents, chunks ~150 words with overlap.
- Eval set: 10 manually labelled questions, including one deliberately out-of-scope negative.
- Train/eval split: there is **no learned retriever training** in the sparse baseline; this toy set tests deterministic functionality only, **not production generalization**.
- Reported metrics: `hit_at_k`, `mrr_at_k`, `ndcg_at_k` on answerable queries only; `negative_abstention_accuracy` on out-of-scope questions; and median retrieval latency. Sparse retrieval filters common stopwords but can still be fooled by shared domain terms.
- Reproduce on the same machine and Python version; tiny latency readings vary with hardware. Evaluation output is generated from live execution, not manually fabricated.
- Important: keyword overlap can retrieve irrelevant passages for out-of-domain questions; zero hits does not guarantee semantic unanswerability. Retrieval metrics do not measure generated answer faithfulness. LLM outputs are marked `generated_unverified`.
- Add adversarial data, claim-level attribution, hybrid reranking, systematic latency percentiles, dataset versioning, privacy assessment and human evaluation before production.

## Architecture

```text
Synthetic docs --> chunk_text --> BM25 | TF-IDF | optional DenseIndex
                                     |
CLI / FastAPI / SafeAgent --> GroundedAssistant --> excerpt + source IDs
                                     |
                                evaluate.py
                                     |
                          JSON metrics, test suite, CI

Optional separate generation: retrieved hits --> llm.py --> OpenAI API
```

**Safety limitations:** No personal/company documents in this sample corpus. DOCX/PDF parsing is available via explicit local file API, but no arbitrary server file-system browsing endpoint is exposed. No cloud API request is made by the default CLI, FastAPI, tests or evaluator. Agent is intentionally a deterministic tool router, **not an autonomous multi-step planning agent**. Never describe extractive text as LLM-generated.

## Portfolio talking points

Explain (1) BM25 vs TF-IDF, (2) how real dense embeddings differ from lexical search, (3) why generated outputs need independent citation validation, (4) why a safe agent needs explicit action permissions, (5) what the benchmark does and does not demonstrate. This makes the implementation interview-auditable rather than a flashy mock.
