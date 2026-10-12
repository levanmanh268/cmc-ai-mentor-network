"""Local FastAPI integration with *signed demo tokens*, NOT production SSO.

The API does not trust tenant/role headers. A known locally-held signing secret
is required to issue short-lived demo identities. Do not publish this server.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from .auth import (
    AuthenticationError, SecurityConfigurationError, VerifiedIdentity,
    verify_local_token,
)
from .engine import EnterpriseIndex, GroundedQA, load_corpus
from .extract import extract_invoice
from .workflow import ReviewWorkflow

app = FastAPI(
    title="Enterprise Document AI | Local Signed-Identity Demo",
    version="0.3.0",
    description="No production SSO, no durable audit. Never publish to the internet.",
)
index = EnterpriseIndex(load_corpus())
qa = GroundedQA(index)
workflow = ReviewWorkflow(index)
bearer = HTTPBearer(auto_error=False)

async def signed_identity(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> VerifiedIdentity:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    try:
        return verify_local_token(credentials.credentials)
    except SecurityConfigurationError:
        raise HTTPException(503, "Demo identity service not configured") from None
    except AuthenticationError:
        raise HTTPException(401, "Invalid or expired bearer token", headers={"WWW-Authenticate": "Bearer"}) from None

def require(identity: VerifiedIdentity, scope: str) -> None:
    if scope not in identity.scopes:
        raise HTTPException(403, "Insufficient token scope")

@app.middleware("http")
async def prevent_cache(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

class Question(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    method: str = Field(default="hybrid", pattern="^(bm25|char|hybrid)$")

class InvoiceText(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    source: str = Field(default="local-demo-text", max_length=100)
    page: int = Field(default=1, ge=1, le=100)

class Approval(BaseModel):
    task_id: str = Field(min_length=1, max_length=100)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "corpus_passages": len(index.passages),
        "auth": "HMAC_SIGNED_LOCAL_DEMO_TOKENS_NOT_OIDC",
        "llm_calls": 0,
    }

@app.post("/ask")
def answer(payload: Question, identity: Annotated[VerifiedIdentity, Depends(signed_identity)]):
    require(identity, "read")
    return qa.answer(payload.question, identity.principal, payload.method)

@app.post("/invoice/extract")
def invoice(payload: InvoiceText, identity: Annotated[VerifiedIdentity, Depends(signed_identity)]):
    require(identity, "extract")
    if "finance" not in identity.principal.roles:
        raise HTTPException(403, "Finance role required for invoice extraction")
    return extract_invoice(payload.text, payload.source, payload.page)

@app.post("/workflow/prepare")
def prepare(payload: Question, identity: Annotated[VerifiedIdentity, Depends(signed_identity)]):
    require(identity, "review")
    return workflow.prepare(payload.question, identity.principal)

@app.post("/workflow/approve")
def approve(payload: Approval, identity: Annotated[VerifiedIdentity, Depends(signed_identity)]):
    require(identity, "approve")
    if "approver" not in identity.principal.roles:
        raise HTTPException(403, "Approver role required")
    return workflow.approve(payload.task_id, identity.principal)

@app.get("/workflow/{task_id}")
def inspect(task_id: str, identity: Annotated[VerifiedIdentity, Depends(signed_identity)]):
    require(identity, "review")
    return workflow.inspect(task_id, identity.principal)
