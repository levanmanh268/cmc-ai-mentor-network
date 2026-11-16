# RetailOps AI Lab | Convenience-store Intelligence

**Independent portfolio project using fictional convenience-store policies, product data and receipts. Not built for, deployed at, approved by or integrated into 7-Eleven systems.**

## Alignment with CMC TS AI Engineer Intern

| JD capability | Implementation |
| --- | --- |
| RAG / retrieval | BM25 on versioned policies; access/store filtering before ranking; citations and extractive evidence |
| AI Agents | 5 deterministic allowlisted tools for information lookup, draft handover and price quotation |
| Document Intelligence | Text receipt extraction with evidence offsets; conflicting or absent fields trigger needs_review |
| Model/data evaluation | Fixed 14-query synthetic benchmark: Hit@3, MRR@3, zero-hit negative and access-leak counts |
| Integration | FastAPI read-only mock staff endpoints, JSON contract validation, unit and API tests |
| Security/privacy | Public synthetic HN01 staff only, no manager data via REST, no customer data or write operations |

## Local quickstart (Python 3.11+)

From repository root:

    python -m unittest discover -s retail_ops_ai/tests -v
    python -m retail_ops_ai.evaluate
    python -m pip install -r retail_ops_ai/requirements-api.txt
    uvicorn retail_ops_ai.api:app --host 127.0.0.1 --port 8011

Interactive API docs: http://127.0.0.1:8011/docs

## Architecture and data

    Synthetic SOP policies -> store/role/version filter -> BM25 -> evidence metadata
    Synthetic SKU/price/discount snapshot -> deterministic rule check -> quote (NO POS write)
    Mock receipt text -> regex/format checks -> receipt_id, store_id, total_vnd + source spans
    Tool router -> policy_search | stock_lookup | price_quote | receipt_extract | handover_draft
    Manual evaluation queries -> ranking metrics + no-cross-scope leakage regression -> CI

Data lives in data/policies.json, data/store.json and data/eval.json. No real store identities, receipts or business secrets appear in this repository.

## Scope and limitations

No Gemini/OpenAI call is required and the core is a deterministic lexical retrieval baseline, NOT a completed autonomous retail agent. Price quotes are synthetic, snapshots are not live POS values and no purchase or refund is ever executed. Role filtering within the engine assumes a trusted Principal; the public API exposes only a constant fictional staff identity and provides no production authentication. The 14-question fixture is public, small and not a claim of production accuracy.

**Important employment distinction:** this independent portfolio project is not a work deliverable from employment at 7-Eleven. It exists to show transferable engineering skills related to store operations and CMC TS's job description.
