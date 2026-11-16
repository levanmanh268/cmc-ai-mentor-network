"""Deterministic human-approval workflow simulator with bounded in-memory state.

Never executes outbound API calls, payments, email or record mutations.
Approvals are atomic within one process; restart loses ALL state. This is not
a durable enterprise workflow or a replacement for real identity and auditing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from threading import RLock
import secrets
import time

from .engine import EnterpriseIndex, Principal, GroundedQA

MAX_TASKS = 200
TASK_TTL_SECONDS = 3600

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
    created_at: float = field(default_factory=time.time)

class ReviewWorkflow:
    def __init__(self, index: EnterpriseIndex):
        self.index = index
        self.tasks: dict[str, Task] = {}
        self._lock = RLock()

    def _prune(self, now: float) -> None:
        for key in list(self.tasks):
            if now - self.tasks[key].created_at >= TASK_TTL_SECONDS:
                del self.tasks[key]

    def _may_read_evidence(self, task: Task, principal: Principal) -> bool:
        """Re-check active permissions/versions when reading or approving a task.

        This is still a synthetic in-process policy, NOT real IAM/DB row security.
        An old document that has since been replaced does not reappear.
        """
        current = date.today().isoformat()
        visible = {self.index.passages[i].uid for i in self.index._visible(principal, current)}
        return bool(task.citations) and all(c["id"] in visible for c in task.citations)

    def prepare(self, question: str, principal: Principal, as_of: str | None = None) -> dict:
        # Use current active policy for approval workflows, no caller-controlled historical time.
        today = date.today().isoformat()
        if as_of is not None and as_of != today:
            return {"status": "blocked", "reason": "workflow_requires_current_policy", "citations": []}
        gate = GroundedQA(self.index).answer(question, principal, as_of=today)
        if gate["status"] != "evidence_found":
            return {"status": "blocked", "reason": gate["reason"], "citations": []}
        hits = self.index.search(question, principal, as_of=today, k=3)
        top = hits[0].passage
        if len(question) > 1000:
            return {"status": "blocked", "reason": "question_too_long", "citations": []}
        with self._lock:
            now = time.time()
            self._prune(now)
            if len(self.tasks) >= MAX_TASKS:
                return {"status": "blocked", "reason": "workflow_capacity_exceeded", "citations": []}
            task_id = "review-" + secrets.token_urlsafe(18)
            task = Task(
                task_id=task_id,
                requester=principal.subject,
                tenant=principal.tenant,
                question=question,
                state="pending_approval",
                citations=[h.to_dict() for h in hits],
                draft=(
                    f"DRAFT FOR HUMAN REVIEW ONLY\nRequest: {question[:500]}\n"
                    f"Evidence: {top.text[:500]}\nSource: {top.source} page {top.page}\n"
                    "No external action has been executed."
                ),
                created_at=now,
            )
            task.history.append({"step": "retrieve", "sources": [h.passage.uid for h in hits]})
            task.history.append({"step": "prepare_draft", "approval_required": True})
            self.tasks[task_id] = task
            return self._serialize(task)

    @staticmethod
    def _serialize(task: Task) -> dict:
        return {
            "status": task.state,
            "task_id": task.task_id,
            "draft": task.draft,
            "citations": list(task.citations),
            "history": list(task.history),
            "external_actions_executed": 0,
        }

    def approve(self, task_id: str, principal: Principal) -> dict:
        with self._lock:
            self._prune(time.time())
            task = self.tasks.get(task_id)
            if task is None or task.tenant != principal.tenant:
                return {"status": "not_found"}
            if task.state != "pending_approval":
                return {"status": "rejected", "reason": "invalid_state"}
            if (
                "approver" not in principal.roles
                or principal.subject == task.requester
                or not self._may_read_evidence(task, principal)
            ):
                return {"status": "rejected", "reason": "independent_authorized_approver_required"}
            task.state = "approved_for_manual_execution"
            task.approver = principal.subject
            task.history.append({"step": "human_approval", "by": principal.subject})
            return self._serialize(task)

    def inspect(self, task_id: str, principal: Principal) -> dict:
        with self._lock:
            self._prune(time.time())
            task = self.tasks.get(task_id)
            if task is None or task.tenant != principal.tenant:
                return {"status": "not_found"}
            if not self._may_read_evidence(task, principal):
                return {"status": "not_found"}
            if principal.subject not in {task.requester, task.approver} and "approver" not in principal.roles:
                return {"status": "not_found"}
            return self._serialize(task)
