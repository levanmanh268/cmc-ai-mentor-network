import unittest
from enterprise_doc_ai.engine import EnterpriseIndex, Principal, load_corpus
from enterprise_doc_ai.workflow import ReviewWorkflow

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.flow = ReviewWorkflow(EnterpriseIndex(load_corpus()))
        self.requester = Principal("alpha", frozenset({"sales"}), "sales-user")
        self.approver = Principal("alpha", frozenset({"approver", "sales"}), "team-lead")

    def test_segregation_of_duties(self):
        task = self.flow.prepare("Duyệt chiết khấu hơn mười phần trăm?", self.requester)
        self.assertEqual(task["status"], "pending_approval")
        ident = task["task_id"]
        self.assertEqual(self.flow.approve(ident, self.requester)["status"], "rejected")
        approved = self.flow.approve(ident, self.approver)
        self.assertEqual(approved["status"], "approved_for_manual_execution")
        self.assertEqual(approved["external_actions_executed"], 0)
        self.assertEqual(self.flow.approve(ident, self.approver)["status"], "rejected")
        self.assertEqual([h["step"] for h in approved["history"]], ["retrieve", "prepare_draft", "human_approval"])

    def test_cross_tenant_denied(self):
        task = self.flow.prepare("Bảng giá chiết khấu Alpha", self.requester)
        self.assertEqual(task["status"], "pending_approval")
        foreign = Principal("beta", frozenset({"approver"}), "beta-manager")
        self.assertEqual(self.flow.inspect(task["task_id"], foreign)["status"], "not_found")

    def test_no_evidence_and_injection_block(self):
        self.assertEqual(self.flow.prepare("tàu thăm dò vệ tinh sao Mộc", self.requester)["status"], "blocked")
        it = Principal("alpha", frozenset({"it"}), "it-user")
        self.assertEqual(self.flow.prepare("mẫu nhận diện prompt injection", it)["status"], "blocked")


    def test_approval_is_atomic_under_concurrency(self):
        from concurrent.futures import ThreadPoolExecutor
        task = self.flow.prepare("Duyệt chiết khấu hơn mười phần trăm?", self.requester)
        self.assertEqual(task["status"], "pending_approval")
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(
                lambda _: self.flow.approve(task["task_id"], self.approver), range(16)
            ))
        self.assertEqual(sum(r["status"] == "approved_for_manual_execution" for r in results), 1)
        record = self.flow.inspect(task["task_id"], self.approver)
        self.assertEqual(sum(h["step"] == "human_approval" for h in record["history"]), 1)

    def test_task_expiry_fails_closed(self):
        from unittest.mock import patch
        task = self.flow.prepare("Duyệt chiết khấu hơn mười phần trăm?", self.requester)
        self.assertEqual(task["status"], "pending_approval")
        with patch("enterprise_doc_ai.workflow.TASK_TTL_SECONDS", 0):
            self.assertEqual(self.flow.approve(task["task_id"], self.approver)["status"], "not_found")
            self.assertEqual(self.flow.inspect(task["task_id"], self.requester)["status"], "not_found")

    def test_capacity_control(self):
        from unittest.mock import patch
        with patch("enterprise_doc_ai.workflow.MAX_TASKS", 0):
            result = self.flow.prepare("Duyệt chiết khấu hơn mười phần trăm?", self.requester)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "workflow_capacity_exceeded")

    def test_stale_evidence_cannot_be_approved(self):
        from unittest.mock import patch
        task = self.flow.prepare("Duyệt chiết khấu hơn mười phần trăm?", self.requester)
        self.assertEqual(task["status"], "pending_approval")
        with patch.object(self.flow.index, "_visible", return_value=[]):
            self.assertEqual(self.flow.approve(task["task_id"], self.approver)["status"], "rejected")
            self.assertEqual(self.flow.inspect(task["task_id"], self.requester)["status"], "not_found")

    def test_historical_policy_blocked_for_actions(self):
        self.assertEqual(
            self.flow.prepare("Duyệt chiết khấu hơn mười phần trăm?", self.requester, as_of="2025-01-01")["reason"],
            "workflow_requires_current_policy",
        )

if __name__ == "__main__":
    unittest.main()
