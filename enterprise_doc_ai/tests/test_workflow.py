import unittest
from enterprise_doc_ai.engine import EnterpriseIndex, Principal, load_corpus
from enterprise_doc_ai.workflow import ReviewWorkflow

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.flow = ReviewWorkflow(EnterpriseIndex(load_corpus()))
        self.requester = Principal("alpha", frozenset({"sales"}), "sales-user")
        self.approver = Principal("alpha", frozenset({"approver"}), "team-lead")

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

if __name__ == "__main__":
    unittest.main()
