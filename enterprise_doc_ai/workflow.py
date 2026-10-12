"""Auditable multi-step, approval-gated workflow simulator.

This intentionally NEVER sends messages, performs payments, changes an HR record,
or reaches an external API. 'Approved' means ready for human execution.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import itertools
from .engine import EnterpriseIndex, Principal, GroundedQA, UNTRUSTED_INSTRUCTION

@dataclass
class Task:
    task_id: str
    requester: str
    tenant: str
    question: str
    state: str
    citations: list[dict]
    draft: str
    approver: str | None = None
    history: list[dict] = field(default_factory=list)

class ReviewWorkflow:
    def __init__(self, index: EnterpriseIndex):
        self.index = index
        self.tasks: dict[str, Task] = {}
        self._sequence = itertools.count(1)

    def prepare(self, question: str, principal: Principal, as_of: str = "2026-10-12") -> dict:
        # Workflow cannot bypass the grounded QA evidence/abstention gate.
        evidence = GroundedQA(self.index).answer(question, principal, as_of=as_of)
        if evidence["status"] != "evidence_found":
            return {"status": "blocked", "reason": evidence["reason"], "citations": []}
        hits = self.index.search(question, principal, as_of=as_of, k=3)
        first = hits[0].passage
        request_id = next(self._sequence)
        task_id = "review-" + hashlib.sha256(f"{principal.tenant}|{principal.subject}|{request_id}".encode()).hexdigest()[:14]
        draft = (f"DRAFT FOR HUMAN REVIEW ONLY\nRequest: {question[:500]}\n"
                 f"Evidence: {first.text[:500]}\nSource: {first.source} page {first.page}\n"
                 "No external action has been executed.")
        task = Task(task_id, principal.subject, principal.tenant, question, "pending_approval",
                    [h.to_dict() for h in hits], draft)
        task.history.append({"step": "retrieve", "sources": [h.passage.uid for h in hits]})
        task.history.append({"step": "prepare_draft", "approval_required": True})
        self.tasks[task_id] = task
        return self.inspect(task_id, principal)

    def _may_read_evidence(self, task: Task, principal: Principal) -> bool:
        docs = {p.uid: p for p in self.index.passages}
        return all(c["id"] in docs and docs[c["id"]].accessible(principal) for c in task.citations)

    def approve(self, task_id: str, principal: Principal) -> dict:
        task = self.tasks.get(task_id)
        if not task or task.tenant != principal.tenant:
            return {"status": "not_found"}
        if task.state != "pending_approval":
            return {"status": "rejected", "reason": "invalid_state"}
        if ("approver" not in principal.roles or principal.subject == task.requester
                or not self._may_read_evidence(task, principal)):
            return {"status": "rejected", "reason": "independent_approver_required"}
        task.state = "approved_for_manual_execution"
        task.approver = principal.subject
        task.history.append({"step": "human_approval", "by": principal.subject})
        return self.inspect(task_id, principal)

    def inspect(self, task_id: str, principal: Principal) -> dict:
        task = self.tasks.get(task_id)
        if not task or task.tenant != principal.tenant:
            return {"status": "not_found"}
        if not self._may_read_evidence(task, principal):
            return {"status": "not_found"}
        if principal.subject not in {task.requester, task.approver} and "approver" not in principal.roles:
            return {"status": "not_found"}
        return {"status": task.state, "task_id": task.task_id, "draft": task.draft,
                "citations": task.citations, "history": list(task.history),
                "external_actions_executed": 0}
