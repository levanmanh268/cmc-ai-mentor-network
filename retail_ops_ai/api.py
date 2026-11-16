"""FastAPI read-only retail demo. Public endpoints expose synthetic staff data ONLY.

No user authentication and NO access to manager-only synthetic documents via HTTP.
Not intended for real store network or real customer data.
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from .core import RetailService, Principal

app=FastAPI(title="RetailOps AI Lab: Synthetic Store Intelligence",version="0.1.0")
service=RetailService()
PUBLIC_STAFF=Principal("HN01","staff")

class Ask(BaseModel):
    question:str=Field(min_length=3,max_length=1000)
class Stock(BaseModel):
    sku:str=Field(min_length=3,max_length=20)
class Quote(BaseModel):
    sku:str=Field(min_length=3,max_length=20)
    date:str=Field(default="2026-10-12",max_length=10)
    qty:int=Field(default=1,ge=1,le=100)
class Receipt(BaseModel):
    text:str=Field(min_length=1,max_length=5000)
class Handover(BaseModel):
    issues:list[str]=Field(default_factory=list,max_length=12)

@app.get("/health")
def health():
    return {"status":"ok","mode":"synthetic_public_staff_only","external_ai_calls":0}

@app.post("/policy/search")
def policy(payload:Ask):
    return service.policy_search(PUBLIC_STAFF,payload.question)

@app.post("/stock")
def stock(payload:Stock):
    return service.stock_lookup(PUBLIC_STAFF,payload.sku)

@app.post("/quote")
def quote(payload:Quote):
    return service.price_quote(PUBLIC_STAFF,payload.sku,payload.date,payload.qty)

@app.post("/receipt/extract")
def receipt(payload:Receipt):
    return service.run_tool("receipt_extract",PUBLIC_STAFF,{"text":payload.text})

@app.post("/handover/draft")
def handover(payload:Handover):
    return service.handover_draft(PUBLIC_STAFF,payload.issues)
