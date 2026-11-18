# SEC-01 | Security assets, CIA and risk assessment

**Project:** CMC AI Mentor Network. **Scope:** root Streamlit classroom application, not the independent portfolio lab APIs. **Date:** 2026-11-09. **Owner:** Lê Văn Mạnh. **Issue:** #169.

## Verified architecture and asset classification
| Asset | Exposure / storage | Sensitivity | CIA importance |
| --- | --- | --- | --- |
| Student name, year, field, goals, bio | Streamlit server session RAM, browser widget traffic | Personal data, moderate | C high, I moderate, A moderate |
| User's BYOK Groq API credential | Password widget, server RAM while session lives, provider SDK | Secret, high | C critical, I high |
| Server's optional GROQ_API_KEY | Environment variable; loaded by llm_client.py | Secret, high | C critical |
| General chat and RAG history | Session RAM; RAG context from repository docs | Potential personal/proprietary text | C high, I moderate |
| Matching/favorites | Per-session state; demo mentor repository from source | Low/medium; possible real names | I high, C moderate |
| Knowledge base Markdown | Public repository at knowledge_base/ | Public-demo content | I high, A moderate |
| Git commits / CI artifacts | Public GitHub history and logs | Exposure if secret inadvertently committed | C critical |
| Public Render deployment | Public internet, third-party hosting | Service availability; consent boundary | A high, C high if BYOK |
| Groq API and external processing | Third-party network processor | User prompts, retrieved snippets, optional profile fields | C high |

No account DB, auth service, password table, or durable user-record storage in the root prototype. Those assets must NOT be invented.

## Risk register
Likelihood and impact: Low/Medium/High, qualitative classroom estimates, not probabilistic measurements.

| ID | Asset / CIA | Threat and entry point | Likelihood | Impact | Priority | Mitigation and verification | Residual status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | BYOK/server API key, C | Key leaked in code, commit history, CI or exception | High due to historic exposure | High | P0 | `scripts/secret_guard.py` current HEAD; revoke/rotate previously exposed key (owner); private history scan; no raw keys in PR | Key revocation NOT VERIFIED |
| R02 | Prompt and personal content, C | User enables Groq and discloses personal data unknowingly | Medium | High | P0 | Explicit checkbox default off, security_controls.consented_client; privacy notice; do not log payloads | Provider retention review NOT VERIFIED |
| R03 | Retrieval quality, I | Malicious Markdown instructs model to ignore rules / forge citations | Medium | High | P1 | Separate untrusted context, validate citation membership, offline refusal; independent adversarial model assessment required | Live semantic defense NOT VERIFIED |
| R04 | Knowledge root, C/I | Symlink leads Markdown reader outside approved directory | Medium in local/editable environment | High | P0 | Reject symlinked knowledge root and linked files, tests/test_security_sprint.py | CI PR confirmation pending |
| R05 | App availability, A | Oversized query exhausts CPU/vectorizer or provider quota | Medium | Medium | P1 | Reject >4000 characters, provider/demo quota; provider-side auth/rate controls needed for public use | Server-level rate limiting ABSENT |
| R06 | Dynamic content, I | Markdown/HTML spoofed mentor name/source appears to be trusted UI | Medium | Medium | P1 | Escape untrusted inline Markdown labels, never enable unsafe_allow_html on user content | Browser XSS verification pending |
| R07 | Session data, C | Session/chat/history accidentally mixed across separate users | Low/Medium | High | P0 | Session-isolated state and reset tests; manual browser-context isolation needed | Manual cloud isolation NOT VERIFIED |
| R08 | Service deps, A/C | Vulnerable Python package or compromised dependency | Medium | High | P1 | pip-audit on exact main SHA after integration; pin tested bounds as feasible | Scan does not prove zero flaws |
| R09 | Project integrity, I | Unreviewed direct push to unprotected main | Medium | High | P0 | Branch protection, required checks, independent review, signed evidence | main protected=false at snapshot |
| R10 | Future shared user data, C/I | Persistent mentor creation without auth causes anonymous overwrite | Medium if feature added | High | P0 | Keep mentor drafts session scoped; require authz/DB design for shared writes, test browser isolation | Feature #165 / PR #168 pending |

## Treatment priority
P0: owner must remediate or formally accept with evidence before claiming a secure public multi-user product. P1: targeted controls and review before demo. P2: planned improvement. A red CI or new leaked secret is a release blocker. A security check passing is evidence only for that scope and SHA.

## References
- `SECURITY.md`; `docs/PRIVACY_DATAFLOW.md`; `docs/security/threat-model.md`.
- Issues #169, #171, #172, #173, #177, #180; prior #1 and #87.
- This is a risk assessment, NOT a penetration test or certification.
