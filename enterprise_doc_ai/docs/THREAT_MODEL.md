# Threat model and limitations

This is a two-tenant synthetic offline simulation, NOT security-certified software.

## Trust boundaries

- Metadata includes tenant, role, source, page, version and effective date.
- Candidates are filtered by trusted Principal before term statistics and ranking.
- Document text is untrusted data. Pattern checks flag a few known prompt injections, but do not prove security.
- Workflow drafts require an independent human approval step, with no external action execution.
- Documents assigned to Alpha and Beta are fictional; no actual corporate information is stored.

## Known gaps

1. API has NO authentication. Caller-supplied X-Demo-Tenant and X-Demo-Roles can be forged. NEVER deploy publicly or present as secure enterprise RBAC.
2. In-memory audit history can disappear on process restart; no tamper-evident logs.
3. No real security key management, encryption, access policy service or network isolation.
4. Regex prompt-injection guard cannot detect novel, obfuscated or multilingual attacks.
5. Document relevance and source references do not prove answer entailment.
6. Optional OCR and PDF parsing need isolation, bounded resources and validation for malicious files.
7. Version metadata is self-reported by synthetic fixtures, not signed/verified.
8. An approver must also have permission for the referenced document; approval authority alone should not reveal it.
9. Synthetic public eval set risks optimistic retrieval scores and sampling bias.

Production path: verified OIDC sessions -> server-managed Principal -> document ACL enforcement -> encrypted vector/document store -> immutable provenance -> human adjudication -> trace and incident monitoring -> adversarial evaluations -> security review.

10. Remote LLM calls transmit authorized retrieved text to the configured external provider. Citation membership validation is insufficient for factual entailment or privacy certification. A real deployment requires an approved data processing agreement and stronger output verification.
