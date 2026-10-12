"""RetailOps AI: auditable read-only tools, retail policy RAG, pricing and receipt QA.

Synthetic store fixtures only. NOT used by, endorsed by or integrated into 7-Eleven.
No external AI calls, transaction mutations, payment or real customer data.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
import json
import math
import re
import statistics
import time

WORD = re.compile(r"[^\W_]+", re.UNICODE)
STOPS = frozenset({"the","and","for","with","are","what","how","does","can","to","of","in","is",
    "và","là","các","cho","được","của","một","ở","trong","như","thế","nào","có","không",
    "cần","phải","theo","để","tại","bao","nhiêu","những","khi","tôi","em","anh","chị"})
def tokenize(text: str) -> list[str]:
    return [v for v in WORD.findall(text.lower()) if v not in STOPS and len(v) > 1]

@dataclass(frozen=True)
class Principal:
    store: str
    role: str

@dataclass(frozen=True)
class Source:
    uid: str
    family: str
    title: str
    body: str
    store: str
    roles: tuple[str, ...]
    version: int
    effective: str
    page: int

    @classmethod
    def load(cls, item: dict) -> "Source":
        fields = {"uid","family","title","body","store","roles","version","effective","page"}
        if set(item) != fields:
            raise ValueError("Invalid source schema")
        if not all(isinstance(item[key],str) and item[key].strip() for key in ("uid","family","title","body","store","effective")):
            raise ValueError("Missing source text or scope")
        if not isinstance(item["roles"],list) or not item["roles"] or any(x not in ("staff","manager") for x in item["roles"]):
            raise ValueError("Invalid roles")
        if type(item["version"]) is not int or item["version"] <= 0 or type(item["page"]) is not int or item["page"] <= 0:
            raise ValueError("Invalid page/version")
        date.fromisoformat(item["effective"])
        return cls(**{**item,"roles":tuple(item["roles"])})

def load_sources(path: str | Path | None = None) -> list[Source]:
    path = Path(path or Path(__file__).parent/"data"/"policies.json")
    if path.is_symlink() or path.stat().st_size > 300000:
        raise ValueError("Refuse symlink or oversized policy file")
    docs = [Source.load(x) for x in json.loads(path.read_text(encoding="utf-8"))]
    if not docs or len({x.uid for x in docs}) != len(docs):
        raise ValueError("Empty corpus or duplicate ID")
    return docs

def _bm25(query: list[str], texts: list[list[str]]) -> list[float]:
    if not texts or not query: return [0.0]*len(texts)
    doc_freq=Counter(x for terms in texts for x in set(terms))
    n=len(texts); avg=sum(map(len,texts))/n or 1
    result=[]
    for words in texts:
        counts=Counter(words); value=0.0
        for term in set(query):
            tf=counts.get(term,0)
            if tf:
                idf=math.log1p((n-doc_freq[term]+0.5)/(doc_freq[term]+0.5))
                value+=idf*(tf*2.5)/(tf+1.5*(0.25+0.75*len(words)/avg))
        result.append(value)
    return result

def parse_receipt(text: str, source: str = "demo-receipt") -> dict:
    """Strict receipt field extraction with evidence span; never invent missing numbers."""
    fields={
       "receipt_id":r"(?im)^\s*(?:Mã hóa đơn|Receipt ID)\s*:\s*([A-Za-z0-9/-]{3,35})\s*$",
       "store_id":r"(?im)^\s*(?:Mã cửa hàng|Store ID)\s*:\s*([A-Z0-9-]{2,12})\s*$",
       "total_vnd":r"(?im)^\s*(?:Tổng cộng|Total VND)\s*:\s*([\d.]+)\s*(?:VND|VNĐ)?\s*$",
    }
    values={}; errors=[]
    for key,pattern in fields.items():
        found=list(re.finditer(pattern,text))
        if len(found)!=1:
            values[key]=None
            if len(found)>1: errors.append("ambiguous_"+key)
            continue
        match=found[0]; raw=match.group(1)
        val=raw
        if key=="total_vnd":
            if not re.fullmatch(r"\d{1,3}(?:\.\d{3})*|\d+",raw):
                errors.append("invalid_total");values[key]=None;continue
            val=int(raw.replace(".",""))
            if val<=0:
                errors.append("invalid_total");values[key]=None;continue
        values[key]={"value":val,"evidence":match.group(0).strip(),"source":source,"span":[match.start(),match.end()]}
    return {"status":"complete" if all(values.values()) and not errors else "needs_review",
            "fields":values,"errors":errors,"mode":"deterministic_extraction"}

class RetailService:
    def __init__(self, policies: list[Source] | None = None, fixture_path: str | Path | None = None):
        self.policies=list(load_sources() if policies is None else policies)
        path=Path(fixture_path or Path(__file__).parent/"data"/"store.json")
        if path.is_symlink() or path.stat().st_size>100000:
            raise ValueError("Invalid store snapshot")
        self.fixture=json.loads(path.read_text(encoding="utf-8"))
        self.allowed_tools=("policy_search","stock_lookup","price_quote","receipt_extract","handover_draft")

    def _visible(self, who: Principal, as_of: str) -> list[Source]:
        date.fromisoformat(as_of)
        if who.role not in ("staff","manager") or not re.fullmatch(r"[A-Z0-9-]{2,12}",who.store):
            return []
        eligible=[p for p in self.policies if p.store in (who.store,"*") and p.effective<=as_of]
        latest={}
        for p in eligible:
            key=(p.family,p.store)
            latest[key]=max(latest.get(key,("",0)),(p.effective,p.version))
        return [p for p in eligible if (p.effective,p.version)==latest[(p.family,p.store)]
                and (who.role in p.roles or (who.role=="manager" and "staff" in p.roles))]

    def policy_search(self, who: Principal, question: str, as_of: str="2026-10-12", k: int=3) -> dict:
        if not question.strip() or len(question)>1000 or not 1<=k<=10: raise ValueError("Invalid query")
        # Sensitive credential requests and cross-store ambiguous questions
        # must not fall through to loosely matched operational SOPs.
        if re.search(r"(?i)(mật khẩu|password|\\botp\\b|api[ -]?key|access[ -]?token)", question):
            return {"status":"abstained","evidence":[],"reason":"sensitive_credentials_not_in_knowledge_base",
                    "mode":"extractive_search_not_llm_answer"}
        requested_stores=set(re.findall(r"(?i)\\bHN[0-9]{2}\\b",question))
        if requested_stores and requested_stores!={who.store}:
            return {"status":"abstained","evidence":[],"reason":"ambiguous_or_foreign_store",
                    "mode":"extractive_search_not_llm_answer"}
        docs=self._visible(who,as_of)
        scores=_bm25(tokenize(question),[tokenize(d.title+" "+d.body) for d in docs])
        ranked=sorted(((docs[i],score) for i,score in enumerate(scores) if score>0),key=lambda x:(-x[1],x[0].uid))
        # Fail-closed relevance gate: shared generic words alone are not evidence.
        # Lexical coverage is a heuristic, NOT an entailment or calibrated confidence.
        query_terms=set(tokenize(question))
        sufficient=[]
        for doc,score in ranked:
            matched=query_terms.intersection(tokenize(doc.title+" "+doc.body))
            coverage=len(matched)/len(query_terms) if query_terms else 0.0
            if len(matched)>=min(2,len(query_terms)) and coverage>=0.40:
                sufficient.append((doc,score))
        ranked=sufficient[:k]
        evidence=[{"id":doc.uid,"family":doc.family,"title":doc.title,
                   "page":doc.page,"version":doc.version,"score":round(score,6),
                   "excerpt":doc.body[:450]} for doc,score in ranked]
        return {"status":"evidence_found" if evidence else "abstained",
                "evidence":evidence,"mode":"extractive_search_not_llm_answer"}

    def stock_lookup(self, who: Principal, sku: str) -> dict:
        if who.role not in ("staff","manager"):
            return {"status":"denied"}
        store=self.fixture["stock"].get(who.store)
        if store is None:return {"status":"unknown_store"}
        product=self.fixture["products"].get(sku.upper())
        if product is None:return {"status":"unknown_sku"}
        return {"status":"ok","sku":sku.upper(),"name":product["name"],
                "units_on_hand":store.get(sku.upper(),0),"store":who.store,
                "snapshot_date":self.fixture["snapshot_date"],"synthetic":True}

    def price_quote(self, who: Principal, sku: str, query_date: str, qty: int=1) -> dict:
        if who.role not in ("staff","manager"):return {"status":"denied"}
        date.fromisoformat(query_date)
        if type(qty) is not int or not 1<=qty<=100:raise ValueError("Quantity must be 1..100")
        store=self.fixture["stock"].get(who.store)
        if store is None:return {"status":"unknown_store"}
        stock=store.get(sku.upper(),0)
        item=self.fixture["products"].get(sku.upper())
        if item is None:return {"status":"unknown_sku"}
        if stock<qty:return {"status":"insufficient_stock","available":stock,"requested":qty}
        unit=Decimal(str(item["price_vnd"]))
        eligible=[p for p in self.fixture["promotions"] if p["sku"]==sku.upper()
                  and p["start"]<=query_date<=p["end"] and (p["store"]==who.store or p["store"]=="*")]
        if len(eligible)>1:return {"status":"needs_human_review","reason":"overlapping_promotions"}
        rate=Decimal(str(eligible[0]["discount_rate"])) if eligible else Decimal("0")
        if not Decimal("0")<=rate<Decimal("1"):raise ValueError("Invalid discount rate")
        gross=unit*qty
        net=gross*(1-rate)
        if net!=net.to_integral_value():return {"status":"needs_human_review","reason":"fractional_vnd"}
        return {"status":"quote","sku":sku.upper(),"quantity":qty,
                "gross_vnd":int(gross),"discount_rate":str(rate),
                "total_vnd":int(net),"promotion":eligible[0]["id"] if eligible else None,
                "snapshot_date":self.fixture["snapshot_date"],"synthetic":True,
                "notice":"Simulation, not a payment or live price"}

    def handover_draft(self, who: Principal, issues: list[str]) -> dict:
        if who.role not in ("staff","manager"):return {"status":"denied"}
        if not isinstance(issues,list) or len(issues)>12 or any(not isinstance(x,str) or len(x)>300 for x in issues):
            raise ValueError("Invalid handover")
        return {"status":"draft_only","store":who.store,"issues":[x.strip() for x in issues if x.strip()],
                "requires_manager_review":True,"external_mutations":0}

    def run_tool(self, tool: str, who: Principal, payload: dict) -> dict:
        if tool not in self.allowed_tools:
            return {"status":"denied","reason":"tool_not_allowed"}
        if tool=="policy_search":
            return self.policy_search(who,str(payload.get("question","")),str(payload.get("as_of","2026-10-12")))
        if tool=="stock_lookup":
            return self.stock_lookup(who,str(payload.get("sku","")))
        if tool=="price_quote":
            return self.price_quote(who,str(payload.get("sku","")),str(payload.get("date","2026-10-12")),payload.get("qty",1))
        if tool=="receipt_extract":
            if who.role not in ("staff","manager"):return {"status":"denied"}
            return parse_receipt(str(payload.get("text",""))[:5000])
        return self.handover_draft(who,payload.get("issues",[]))
