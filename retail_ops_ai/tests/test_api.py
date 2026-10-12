import unittest
from fastapi.testclient import TestClient
from retail_ops_ai.api import app

client=TestClient(app)
class RetailApiTests(unittest.TestCase):
    def test_health_demo(self):
        r=client.get("/health"); self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()["mode"],"synthetic_public_staff_only")
    def test_read_only_policy_and_stock(self):
        self.assertEqual(client.post("/policy/search",json={"question":"cập nhật giá POS khuyến mại"}).status_code,200)
        r=client.post("/stock",json={"sku":"DRK-002"})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()["units_on_hand"],8)
    def test_quote_calculation(self):
        r=client.post("/quote",json={"sku":"SNK-001","date":"2026-10-12","qty":2})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()["total_vnd"],27000)
    def test_invalid_schema(self):
        self.assertEqual(client.post("/quote",json={"sku":"SNK-001","date":"2026-10-12","qty":0}).status_code,422)
        self.assertEqual(client.post("/policy/search",json={"question":""}).status_code,422)
    def test_manager_document_never_exposed(self):
        r=client.post("/policy/search",json={"question":"quản lý báo cáo doanh thu lệch"})
        self.assertEqual(r.status_code,200)
        self.assertNotIn("policy-manager",[x["id"] for x in r.json()["evidence"]])
    def test_handover_is_draft(self):
        r=client.post("/handover/draft",json={"issues":["kiểm kho lại"]})
        self.assertEqual(r.json()["external_mutations"],0)
        self.assertEqual(r.json()["status"],"draft_only")
