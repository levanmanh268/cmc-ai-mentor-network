"""HTTP security regression suite: signatures, scopes, identity spoofing, workflow."""
import os
import unittest
from unittest.mock import patch

try:
    from fastapi.testclient import TestClient
    from enterprise_doc_ai.api import app
    from enterprise_doc_ai.auth import SECRET_ENV, mint_local_token
    client = TestClient(app)
except ImportError:
    client = None

KEY = "integration-security-key-" + "b" * 48

@unittest.skipIf(client is None, "Optional FastAPI/httpx not installed")
class APITests(unittest.TestCase):
    def setUp(self):
        self.patch = patch.dict(os.environ, {SECRET_ENV: KEY})
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def token(self, tenant="alpha", subject="alice", roles=None, scopes=None):
        return mint_local_token(tenant, subject, roles or ["employee"], scopes or ["read"])

    def headers(self, **kwargs):
        return {"Authorization": "Bearer " + self.token(**kwargs)}

    def test_health_reports_explicit_auth_limits(self):
        r = client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertIn("SIGNED_LOCAL_DEMO", r.json()["auth"])
        self.assertEqual(r.json()["llm_calls"], 0)
        self.assertEqual(r.headers.get("Cache-Control"), "no-store")

    def test_all_data_routes_require_auth(self):
        for method, path, body in [
            ("post", "/ask", {"question": "ServiceDesk"}),
            ("post", "/invoice/extract", {"text": "demo"}),
            ("post", "/workflow/prepare", {"question": "ServiceDesk"}),
            ("post", "/workflow/approve", {"task_id": "nonexistent"}),
            ("get", "/workflow/nonexistent", None),
        ]:
            with self.subTest(path=path):
                r = getattr(client, method)(path, **({"json": body} if body is not None else {}))
                self.assertEqual(r.status_code, 401)

    def test_invalid_bearer_is_rejected(self):
        r = client.post("/ask", headers={"Authorization": "Bearer forged.jwt.token"}, json={"question": "ServiceDesk"})
        self.assertEqual(r.status_code, 401)

    def test_misconfigured_secret_denies_access(self):
        hdr = self.headers()
        with patch.dict(os.environ, {SECRET_ENV: ""}):
            r = client.post("/ask", headers=hdr, json={"question": "ServiceDesk"})
            self.assertEqual(r.status_code, 503)

    def test_question_validation_and_permissions(self):
        hdr = self.headers()
        self.assertEqual(client.post("/ask", headers=hdr, json={"question": "ServiceDesk cấp quyền?"}).status_code, 200)
        self.assertEqual(client.post("/ask", headers=hdr, json={"question": ""}).status_code, 422)
        no_read = self.headers(scopes=["review"])
        self.assertEqual(client.post("/ask", headers=no_read, json={"question": "ServiceDesk"}).status_code, 403)

    def test_ignores_spoofed_role_and_tenant_headers(self):
        beta = self.headers(tenant="beta", subject="beta-guest")
        beta.update({"X-Demo-Tenant": "alpha", "X-Demo-Roles": "hr,finance,approver"})
        result = client.post("/ask", headers=beta, json={"question": "Bảng lương PayFlow bảng lương nội bộ"})
        self.assertEqual(result.status_code, 200)
        citations = result.json()["citations"]
        self.assertTrue(all(not c["id"].startswith("alpha-") for c in citations))
        self.assertNotIn("PayFlow", result.json().get("answer") or "")

    def test_cannot_read_restricted_payroll_as_employee(self):
        employee = self.headers()
        result = client.post("/ask", headers=employee, json={"question": "bảng lương PayFlow nhân sự"})
        self.assertEqual(result.status_code, 200)
        self.assertTrue(all(c["id"] != "alpha-hr-payroll-2026-p1" for c in result.json()["citations"]))

    def test_invoice_requires_scope_and_finance_role(self):
        payload = {"text": "Số hóa đơn: HD42\nNgày lập: 05/10/2026\nNhà cung cấp: Demo Ltd\nTổng thanh toán: 1.200.000 VND"}
        self.assertEqual(client.post("/invoice/extract", headers=self.headers(), json=payload).status_code, 403)
        no_role = self.headers(scopes=["extract"])
        self.assertEqual(client.post("/invoice/extract", headers=no_role, json=payload).status_code, 403)
        finance = self.headers(roles=["finance"], scopes=["extract"])
        r = client.post("/invoice/extract", headers=finance, json=payload)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "complete")

    def test_workflow_separate_signer_identities_and_scopes(self):
        requester = self.headers(subject="requester", roles=["sales"], scopes=["review"])
        draft = client.post("/workflow/prepare", headers=requester, json={
            "question": "Duyệt chiết khấu hơn mười phần trăm?",
        })
        self.assertEqual(draft.status_code, 200)
        self.assertEqual(draft.json()["status"], "pending_approval")
        task = draft.json()["task_id"]
        fake = self.headers(subject="requester", roles=["sales"], scopes=["approve"])
        self.assertEqual(client.post("/workflow/approve", headers=fake, json={"task_id": task}).status_code, 403)
        reviewer = self.headers(subject="reviewer", roles=["sales", "approver"], scopes=["approve", "review"])
        approval = client.post("/workflow/approve", headers=reviewer, json={"task_id": task})
        self.assertEqual(approval.status_code, 200)
        self.assertEqual(approval.json()["status"], "approved_for_manual_execution")
        self.assertEqual(approval.json()["external_actions_executed"], 0)
        self.assertEqual(client.get("/workflow/" + task, headers=reviewer).status_code, 200)
        beta = self.headers(tenant="beta", subject="beta-reviewer", roles=["sales", "approver"], scopes=["review"])
        self.assertEqual(client.get("/workflow/" + task, headers=beta).json()["status"], "not_found")

    def test_cross_tenant_cannot_approve_even_with_approver_role(self):
        requester = self.headers(subject="sales-two", roles=["sales"], scopes=["review"])
        draft = client.post("/workflow/prepare", headers=requester, json={
            "question": "Duyệt chiết khấu hơn mười phần trăm?",
        }).json()
        token = self.headers(tenant="beta", subject="beta-lead", roles=["approver", "sales"], scopes=["approve"])
        r = client.post("/workflow/approve", headers=token, json={"task_id": draft["task_id"]})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "not_found")

if __name__ == "__main__":
    unittest.main()
