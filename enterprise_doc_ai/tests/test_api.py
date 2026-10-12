import unittest
try:
    from fastapi.testclient import TestClient
    from enterprise_doc_ai.api import app
    client = TestClient(app)
except ImportError:
    client = None

@unittest.skipIf(client is None, "Optional fastapi/httpx not installed")
class APITests(unittest.TestCase):
    def test_health_warns_no_auth(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("UNAUTHENTICATED", response.json()["auth"])
        self.assertEqual(response.json()["llm_calls"], 0)

    def test_ask_validation(self):
        self.assertEqual(client.post("/ask", json={"question":"ServiceDesk cấp quyền?"}).status_code, 200)
        self.assertEqual(client.post("/ask", json={"question":""}).status_code, 422)

    def test_invoice_api(self):
        r = client.post("/invoice/extract", json={"text":"Số hóa đơn: HD42\nNgày lập: 05/10/2026\nNhà cung cấp: Demo Ltd\nTổng thanh toán: 1.200.000 VND"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "complete")

if __name__ == "__main__":
    unittest.main()
