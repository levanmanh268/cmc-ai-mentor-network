import unittest
from retail_ops_ai.core import RetailService,Principal,parse_receipt,load_sources,Source

class RetailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svc=RetailService()
        cls.staff=Principal("HN01","staff")
        cls.manager=Principal("HN01","manager")

    def test_latest_price_policy_not_stale(self):
        hits=self.svc.policy_search(self.staff,"giá POS khuyến mại")["evidence"]
        self.assertTrue(hits)
        self.assertFalse(any(h["id"]=="policy-pricing-v1" for h in hits))

    def test_old_revision_access_at_old_date(self):
        res=self.svc.policy_search(self.staff,"giá giấy báo nội bộ",as_of="2026-02-01")
        self.assertIn("policy-pricing-v1",[x["id"] for x in res["evidence"]])

    def test_role_isolation(self):
        res=self.svc.policy_search(self.staff,"trưởng cửa hàng báo cáo doanh thu")["evidence"]
        self.assertTrue(all(x["id"]!="policy-manager" for x in res))
        own=self.svc.policy_search(self.manager,"lệch doanh thu trưởng cửa hàng")["evidence"]
        self.assertIn("policy-manager",[x["id"] for x in own])

    def test_store_isolation(self):
        hits=self.svc.policy_search(self.staff,"HN02 vệ sinh tủ mát")["evidence"]
        self.assertNotIn("policy-hn02",[x["id"] for x in hits])

    def test_price_with_discount_and_no_discount(self):
        quote=self.svc.price_quote(self.staff,"SNK-001","2026-10-12",2)
        self.assertEqual(quote["total_vnd"],27000)
        self.assertEqual(quote["discount_rate"],"0.10")
        later=self.svc.price_quote(self.staff,"SNK-001","2026-11-01",1)
        self.assertEqual(later["total_vnd"],15000)

    def test_store_specific_promotion(self):
        other=self.svc.price_quote(Principal("HN02","staff"),"SNK-001","2026-10-12")
        self.assertEqual(other["discount_rate"],"0")

    def test_stock_guard(self):
        self.assertEqual(self.svc.price_quote(self.staff,"MIL-003","2026-10-12")["status"],"insufficient_stock")
        self.assertEqual(self.svc.stock_lookup(self.staff,"DRK-002")["units_on_hand"],8)
        self.assertEqual(self.svc.stock_lookup(self.staff,"BOGUS")["status"],"unknown_sku")

    def test_invalid_qty_date(self):
        for qty in (0,-1,101,True):
            with self.subTest(qty=qty),self.assertRaises(ValueError):
                self.svc.price_quote(self.staff,"SNK-001","2026-10-12",qty)
        with self.assertRaises(ValueError):
            self.svc.price_quote(self.staff,"SNK-001","bad-date")

    def test_receipt_good_provenance(self):
        body="Mã hóa đơn: ABC-123\nMã cửa hàng: HN01\nTổng cộng: 27.000 VND"
        res=parse_receipt(body)
        self.assertEqual(res["status"],"complete")
        self.assertEqual(res["fields"]["total_vnd"]["value"],27000)
        for value in res["fields"].values():
            self.assertEqual(body[value["span"][0]:value["span"][1]].strip(),value["evidence"])

    def test_receipt_missing_and_ambiguous(self):
        incomplete=parse_receipt("Mã hóa đơn: ABC-123")
        self.assertEqual(incomplete["status"],"needs_review")
        duplicate=parse_receipt("Tổng cộng: 12.000\nTổng cộng: 22.000")
        self.assertIn("ambiguous_total_vnd",duplicate["errors"])

    def test_tool_allowlist_no_mutations(self):
        self.assertEqual(self.svc.run_tool("delete_sales",self.staff,{})["status"],"denied")
        draft=self.svc.run_tool("handover_draft",self.staff,{"issues":["kiểm kho"]})
        self.assertEqual(draft["external_mutations"],0)
        self.assertTrue(draft["requires_manager_review"])

    def test_irrelevant_or_sensitive_question_requires_evidence(self):
        cases=["Giá Bitcoin hôm nay là bao nhiêu?",
               "Mật khẩu tài khoản thu ngân cửa hàng là gì?"]
        for question in cases:
            with self.subTest(question=question):
                result=self.svc.policy_search(self.staff,question)
                self.assertEqual(result["status"],"abstained")
                self.assertEqual(result["evidence"],[])

    def test_handover_rejects_string_instead_of_issue_list(self):
        with self.assertRaises(ValueError):
            self.svc.handover_draft(self.staff,"không phải danh sách")

    def test_evaluation_access_isolation(self):
        from retail_ops_ai.evaluate import evaluate
        report=evaluate()
        self.assertEqual(report["access_leakage_count"],0)
        self.assertGreater(report["answerable"],5)

    def test_invalid_policy_schema(self):
        item={"uid":"x","family":"x","title":"X","body":"X","store":"*","roles":["admin"],
              "version":1,"effective":"2026-01-01","page":1}
        with self.assertRaises(ValueError):
            Source.load(item)

if __name__=="__main__":unittest.main()
