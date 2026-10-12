"""Optional FastAPI demo.

IMPORTANT: X-Demo-Tenant and X-Demo-Roles are user-controlled test headers.
This is NOT authenticated RBAC. Bind to localhost for experimentation ONLY.
"""
from __future__ import annotations
from typing import Annotated
from fastapi import FastAPI, Header
from pydantic import BaseModel, Field
from .engine import EnterpriseIndex, Principal, GroundedQA, load_corpus
from .extract import extract_invoice
from .workflow import ReviewWorkflow

app = FastAPI(title="Enterprise Document AI | Independent Portfolio Demo", version="0.2.0")
index = EnterpriseIndex(load_corpus())
qa = GroundedQA(index)
workflow = ReviewWorkflow(index)

def demo_principal(
    x_demo_tenant: Annotated[str, Header(max_length=40)] = "alpha",
    x_demo_roles: Annotated[str, Header(max_length=100)] = "employee",
    x_demo_subject: Annotated[str, Header(max_length=80)] = "api-caller",
) -> Principal:
    return Principal(tenant=x_demo_tenant, roles=frozenset(x.strip() for x in x_demo_roles.split(",") if x.strip()), subject=x_demo_subject)

class Question(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    method: str = Field(default="hybrid", pattern="^(bm25|char|hybrid)$")

class InvoiceText(BaseModel):
    text: str = Field(max_length=20000)
    source: str = Field(default="manual-text", max_length=100)
    page: int = Field(default=1, ge=1, le=100)

class Approval(BaseModel):
    task_id: str = Field(max_length=100)

@app.get("/health")
def health():
    return {"status": "ok", "corpus_passages": len(index.passages),
            "auth": "UNAUTHENTICATED DEMO HEADERS", "llm_calls": 0}

@app.post("/ask")
def answer(payload: Question, x_demo_tenant: Annotated[str, Header()] = "alpha",
           x_demo_roles: Annotated[str, Header()] = "employee",
           x_demo_subject: Annotated[str, Header()] = "api-caller"):
    principal = demo_principal(x_demo_tenant, x_demo_roles, x_demo_subject)
    return qa.answer(payload.question, principal, payload.method)

@app.post("/invoice/extract")
def invoice(payload: InvoiceText):
    return extract_invoice(payload.text, payload.source, payload.page)

@app.post("/workflow/prepare")
def prepare(payload: Question, x_demo_tenant: Annotated[str, Header()] = "alpha",
            x_demo_roles: Annotated[str, Header()] = "employee",
            x_demo_subject: Annotated[str, Header()] = "api-caller"):
    return workflow.prepare(payload.question, demo_principal(x_demo_tenant, x_demo_roles, x_demo_subject))

@app.post("/workflow/approve")
def approve(payload: Approval, x_demo_tenant: Annotated[str, Header()] = "alpha",
            x_demo_roles: Annotated[str, Header()] = "employee",
            x_demo_subject: Annotated[str, Header()] = "api-caller"):
    return workflow.approve(payload.task_id, demo_principal(x_demo_tenant, x_demo_roles, x_demo_subject))
