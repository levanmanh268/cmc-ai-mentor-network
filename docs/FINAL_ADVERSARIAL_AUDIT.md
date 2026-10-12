# Final adversarial release audit | 2026-10-13

## Scope and verdict

**Suitable as an independently developed local AI engineering portfolio demo after exact-head CI passes; NOT zero-defect certified or production-ready.** CI is a regression gate, not a mathematical proof that no bugs remain.

Audited modules: `model_pretraining_lab`, `model_posttraining_lab`, `cagent_lab`, `enterprise_doc_ai`, with previous CI evidence for `retail_ops_ai` and `edu_trainer_ai`. Related external repos (Làng Rim Nam AI Guard, Delta Travel, Tour Booking) have independent workflow histories; passing CI there does not establish complete end-to-end or live service correctness.

## Defect findings addressed in PR #48

| Category | Failure mode | Mitigation / regression |
| --- | --- | --- |
| Training numerical safety | Malformed/NaN gradient could partially mutate bigram parameters during loop | Prevalidate full gradient dimensions and finite next matrix BEFORE committing; unit tests confirm unchanged weights on error |
| Training data quality | Pre-training accepted mislabeled checkpoint objective/provenance; DPO preference loader accepted duplicate IDs or trivially identical choices | Strict checkpoint metadata, normalized prompt uniqueness, duplicate ID/choice rejection; negative tests |
| Training stability | SFT/DPO could accept NaN or invalid hyperparameters and invalid prompt sizes | Validate finite LR/beta, integer epoch counts, text bounds; numerical tests |
| Dense retrieval | C-Agent embedding vectors could have missing/ragged dimensions and silently score truncated vectors | Count/dimension/zero-norm/nonfinite fail-closed validation, regression tests |
| Enterprise RAG | Dense query encoder could emit NaN, Inf, missing or malformed vector | Validate query vector before cosine score, regression tests on authorized passages |

## Measured limitations that remain

- Original Enterprise Document AI public 80-case evaluation is synthetic; separate 28-case challenge showed high retrieval Hit@3 (9/10 positive) but extractive evidence acceptance 0/10 positive and 18/18 negative abstention. **Do not claim successful grounded QA on paraphrased queries**.
- Pre-training is a one-character-context BIGRAM language model, not a Transformer or pre-trained production LLM. Only the next-token objective, SGD loss mechanics and checkpoint lifecycle were demonstrated.
- Post-training SFT and DPO compute real objectives on a toy bigram and synthetic preferences; default DPO validation margin DECREASED from 3.59558 to 3.52396. No generalized alignment improvement was demonstrated.
- Real FUNiX or 7-Eleven private models, APIs or company data are NOT contained in this portfolio. The industry projects are independently built synthetic examples.
- The optional remote LLM, OCR and semantic embedding integrations have not been evaluated end-to-end against a representative blinded business dataset.
- The demo security boundaries are not enterprise IAM/SSO: no production OIDC, key lifecycle, tenant-isolated storage, audit persistence, multi-worker orchestration, adversarial red-team certification or pentest.
- Realtime upstream reliability, performance load testing, deployment secrets and compatibility with proprietary CMC services have NOT been established.

## Command-line smoke / reproducibility

    python -m pytest -q
    python -m unittest discover -s model_pretraining_lab/tests -v
    python -m unittest discover -s model_posttraining_lab/tests -v
    python -m unittest discover -s enterprise_doc_ai/tests -v
    python -m unittest discover -s cagent_lab/tests -v
    python -m unittest discover -s retail_ops_ai/tests -v
    python -m unittest discover -s edu_trainer_ai/tests -v
    python -m model_pretraining_lab.core --epochs 5 --output-dir artifacts/pretraining
    python -m model_posttraining_lab.core --pretrained artifacts/pretraining/tiny_pretrained.json --output-dir artifacts/posttraining

CI workflows under `.github/workflows/` run appropriate test subsets on Ubuntu and Windows. Exact-commit results are the acceptance source, not numbers copied from this document. To release to real users, establish threat model, independent QA labels, real identity provider and external integrations testing.

## Interview summary

Explain a defect found, its triggering input, its regression test and how a fix changes fail-closed behavior. Also explain what the tests **do not** prove. Claims of "100% bug-free" or "enterprise-grade security" are not justified by this audit.
