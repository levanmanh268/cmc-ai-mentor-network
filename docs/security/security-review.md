# SEC-13 | Security sprint review and demonstration

**Issue:** #181. **Owner proposed:** Lê Hải Đăng. **Independent reviewer:** PENDING. **Result:** PARTIAL; release/security sign-off not issued.

## Scope
Audit current classroom root Streamlit app and introduce deterministic input/consent/Markdown safeguards with regressions. 13 teacher-defined issues #169-#181, 10 core + 3 extension. SEC-06, SEC-11 and SEC-13 are P2 optional. SEC-07/08 account-based controls are not applicable to the current no-auth product, yet account/DB expansion requires them.

## Changes in security sprint PR (proposed)
- Reject non-string/blank/oversized RAG input before retrieval and Groq provider calls.
- Reject symlinked KnowledgeBase root so local filesystem outside designated folder cannot be accidentally indexed.
- Use explicit True-only consent helper and escape dynamically formatted mentor/source Markdown labels.
- Add tests for invalid input, XSS/Markdown spoofing, consent, session isolation, fake secret patterns.
- Add CIA risk register, Mermaid threat model, auth applicability/access matrix, secret/transport decisions, privacy inventory and data controls.

## Safe before/after classroom demos (do not attack others)
1. **Symlinked knowledge root (SEC-03).** Before: the root symlink path can be traversed by file listing if directory target exists; earlier code only rejected per-file symlinks. After: test `test_sec03_symlinked_root_not_indexed_portable` asserts 0 indexed documents. Collect code diff and actual CI after PR.
2. **Markdown label injection (SEC-04).** Before: source/mentor labels were interpolated into dynamic `st.markdown` with unescaped metacharacters; this is UI spoofing risk, not proof of executable XSS in default Streamlit. After: use `safe_markdown_label` for inline values, test hostile label escaping. Browser DOM script execution is **NOT VERIFIED** until human test.
3. **Oversized input (SEC-03).** Before: KnowledgeBase.search did not validate type/length at Python boundary. After: 4000-character maximum and non-string denial before provider invocation, tested with fake provider. This does not replace network-level DoS throttling.

## Known residual risks
- Historic Groq key revoke/rotate remains **UNKNOWN**, owner must verify privately (#177).
- Public HTTPS/browser header/cookie characteristics not independently verified.
- Auth/account/RBAC/rate limiting not implemented. No shared mutable user database should be enabled anonymously.
- Live model prompt injection resistance and semantic hallucination are not established by offline tests (#83, #139).
- Human UAT, cross-browser isolation, external vendor retention and final independent review not done (#88, #180).
- main branch was unprotected (`protected=false` in snapshot), required-check governance remains #131.

## Review checklist / Definition of Done
- [ ] PR diff reviewed by a contributor other than author.
- [ ] All required Linux/Windows/Chromium CI jobs passed on exact commit and artifacts saved.
- [ ] At least 2 safe demos documented with real observed outputs and SHA; not just instructions.
- [ ] Critical vulnerabilities resolved or explicitly accepted with owner and rationale.
- [ ] Dependency audit on main after merge and exact SHA.
- [ ] Security test report updated to actual observed outputs and no false PASS.
- [ ] Issue closures reflect applicable criteria or explicit N/A decisions, not an invented feature.

## Verdict
This document is a *working review*, not certified secure or complete Security & Privacy acceptance. Record URLs, reviewer, date, findings and remaining limitations after PR integration.
