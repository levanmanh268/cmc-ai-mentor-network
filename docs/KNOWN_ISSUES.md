# Known issues and unverified acceptance items

This list records known gaps; it does not assert the product is defect-free.

| ID | Severity | Finding / limitation | Current handling | Next action / owner |
| --- | --- | --- | --- | --- |
| KI-01 | High | A Groq API key was previously committed to public Git history (see `SECURITY.md`). | Secret was removed from current files; PR CI secret guard scans current tracked HEAD; Git-history scan and revocation are unverified. | Repository owner must confirm key revocation; consider history cleanup. |
| KI-02 | High | Live model resistance to document/question prompt injection is unverified. | System prompt treats retrieved context as untrusted; fake-client tests inspect prompt boundaries. | Run controlled adversarial evaluation with a safe test key and independent review. |
| KI-03 | Medium | RAG benchmark is 31 synthetic in-sample questions over 3 demo docs; independent reviewer-labeled set is pending. | Recall, source mapping, evidence-term proxy and refusal are printed by evaluator. | Build independently labeled, held-out set (at least 30 cases) with multi-source and multilingual examples. |
| KI-04 | Medium | Answer correctness proxy is not semantic correctness. | Reports state this limitation explicitly. | Have reviewers grade model answers with claim-level rubric if live quality is required. |
| KI-05 | Low | Previous `main` CI skipped 25 optional integration tests because API/document dependencies were absent. | All 25 are enumerated with reasons in `docs/TEST_REPORT.md`; current PR Linux/Windows CI installs `requirements-test.txt` and reports 0 skips. | Rerun after merge and verify zero skips on the exact `main` merge SHA (#80, #164). |
| KI-06 | Medium | Required checks for PR merge could not be verified. | GitHub rulesets query returned none; branch-protection endpoint denied access to this integration. | Repository admin must configure required `test`, `windows-local`, and other required checks. |
| KI-07 | Medium | No human UAT evidence exists for this revision. | Checklist is prepared and explicitly marks scenarios not run. | A student/teacher should execute and sign `docs/UAT_CHECKLIST.md`. |
| KI-08 | Low | Current benchmark is synthetic and single-process; no concurrent load, browser, cloud or provider latency. | Scaling and warm-latency scripts report environment and limits. | Agree a workload and SLA before interpreting capacity. |
| KI-09 | Low | Exact textbook chapter edition/content was not supplied for TASK-78. | General testing levels and methods are mapped in the handoff documents. | Attach the assigned chapter/edition for detailed alignment. |

Do not close dependent acceptance issues until the relevant owner supplies evidence.
