"""Deterministic enterprise retrieval with tenant/role filtering and source provenance.

No external AI service or GPU is needed. Security depends on trustworthy Principal
construction upstream; the demo REST API deliberately does NOT authenticate callers.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import json
import math
import re
import statistics
import unicodedata
from typing import Protocol

TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
STOPWORDS = {
    "a", "an", "the", "of", "for", "and", "or", "to", "in", "on", "is", "are",
    "what", "when", "which", "who", "where", "how", "with", "from", "should",
    "was", "were", "has", "have", "that", "this", "can", "do", "does",
    "và", "là", "của", "cho", "có", "không", "được", "những", "các", "một",
    "ở", "khi", "nào", "ai", "đâu", "như", "thế", "để", "trong", "với",
    "theo", "về", "tại", "đến", "bao", "nhiêu", "cần", "phải", "hay",
}
UNTRUSTED_INSTRUCTION = re.compile(
    r"(?i)(ignore (all )?(previous|prior) instructions|system prompt|"
    r"developer instruction|bỏ qua (mọi |tất cả )?(chỉ dẫn|hướng dẫn)|"
    r"tiết lộ (bí mật|mật khẩu)|send.*(?:api key|password))"
)

def tokens(text: str) -> list[str]:
    clean = unicodedata.normalize("NFKC", text).lower()
    return [t for t in TOKEN.findall(clean) if t not in STOPWORDS and len(t) > 1]

def char_ngrams(text: str, n: int = 3) -> list[str]:
    normal = " ".join(tokens(text))
    return [normal[i:i + n] for i in range(max(0, len(normal) - n + 1))] if len(normal) >= n else []

@dataclass(frozen=True)
class Principal:
    tenant: str
    roles: frozenset[str]
    subject: str = "demo"

@dataclass(frozen=True)
class Passage:
    uid: str
    family: str
    title: str
    text: str
    tenant: str
    roles: tuple[str, ...]
    source: str
    page: int
    version: int
    effective: str
    kind: str = "policy"

    @classmethod
    def from_dict(cls, payload: dict) -> "Passage":
        mandatory = {"uid", "family", "title", "text", "tenant", "roles",
                     "source", "page", "version", "effective"}
        if not isinstance(payload, dict):
            raise ValueError("Passage must be a JSON object")
        missing = mandatory - set(payload)
        if missing:
            raise ValueError(f"Missing fields: {sorted(missing)}")
        unknown = set(payload) - (mandatory | {"kind"})
        if unknown:
            raise ValueError(f"Unsupported metadata fields: {sorted(unknown)}")
        for name in ("uid", "family", "title", "text", "tenant", "source", "effective"):
            value = payload[name]
            if not isinstance(value, str) or not value.strip() or len(value) > (20000 if name == "text" else 500):
                raise ValueError(f"Invalid {name}")
        for name in ("page", "version"):
            if type(payload[name]) is not int or payload[name] < 1:
                raise ValueError(f"{name} must be a positive integer")
        roles = payload["roles"]
        if not isinstance(roles, (list, tuple)) or not roles or any(
            not isinstance(role, str) or not role.strip() or len(role) > 80 for role in roles
        ) or len(set(roles)) != len(roles):
            raise ValueError("roles must be a nonempty, duplicate-free string list")
        if "kind" in payload and (not isinstance(payload["kind"], str) or not payload["kind"].strip()):
            raise ValueError("Invalid document kind")
        date.fromisoformat(payload["effective"])
        return cls(**{**payload, "roles": tuple(roles)})

    def accessible(self, principal: Principal) -> bool:
        return self.tenant == principal.tenant and bool(principal.roles.intersection(self.roles))

def load_corpus(path: str | Path | None = None) -> list[Passage]:
    if path is None:
        path = Path(__file__).parent / "data" / "corpus.jsonl"
    source = Path(path)
    if not source.is_file() or source.is_symlink() or source.stat().st_size > 8_000_000:
        raise ValueError("Missing or oversized corpus, or symlink rejected")
    passages = [Passage.from_dict(json.loads(line)) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not passages or len(passages) > 10000:
        raise ValueError("Corpus must contain 1 to 10,000 passages")
    ids = [p.uid for p in passages]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate passage identifiers")
    return passages

@dataclass(frozen=True)
class Result:
    passage: Passage
    score: float
    method: str

    def to_dict(self) -> dict:
        p = self.passage
        return {
            "id": p.uid, "source": p.source, "page": p.page, "title": p.title,
            "version": p.version, "effective": p.effective, "score": round(self.score, 6),
            "method": self.method,
        }

class Encoder(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]: ...

class OptionalSentenceEncoder:
    """Real semantic encoder. Explicit opt-in; may download model weights."""
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Embedding dimensions differ")
    na = math.sqrt(sum(v * v for v in a)) or 1.0
    nb = math.sqrt(sum(v * v for v in b)) or 1.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)

class EnterpriseIndex:
    """RBAC/tenant predicate runs *before* retrieval and reranking.

    Only the latest effective document per (tenant, family) is searchable.
    Role membership is supplied by a trusted caller in real deployments;
    request-header roles in demo API are NOT a security control.
    """
    def __init__(self, passages: list[Passage], encoder: Encoder | None = None):
        self.passages = list(passages)
        self.encoder = encoder
        self._dense_vectors: list[list[float]] | None = None
        if encoder and passages:
            self._dense_vectors = encoder.encode([p.text for p in passages])
            if len(self._dense_vectors) != len(passages):
                raise ValueError("Embedding count mismatches corpus")
            dimensions = {len(vec) for vec in self._dense_vectors}
            if len(dimensions) != 1 or 0 in dimensions or any(
                not math.isfinite(float(value))
                for vec in self._dense_vectors for value in vec
            ):
                raise ValueError("Embedding dimensions and finite values required")
        self._tf = [Counter(tokens(p.title + " " + p.text)) for p in self.passages]
        self._grams = [Counter(char_ngrams(p.title + " " + p.text)) for p in self.passages]

    def _visible(self, principal: Principal, as_of: str) -> list[int]:
        date.fromisoformat(as_of)
        # Select active version BEFORE permission filtering: a revoked policy
        # must not make an outdated, more permissive version reappear.
        eligible = [i for i, p in enumerate(self.passages) if p.tenant == principal.tenant and p.effective <= as_of]
        latest: dict[tuple[str, str], tuple[str, int]] = {}
        for i in eligible:
            p = self.passages[i]
            key = (p.tenant, p.family)
            latest[key] = max(latest.get(key, ("", 0)), (p.effective, p.version))
        # All pages from active version remain independently citable.
        return [i for i in eligible if
                (self.passages[i].effective, self.passages[i].version) ==
                latest[(self.passages[i].tenant, self.passages[i].family)]
                and self.passages[i].accessible(principal)]

    @staticmethod
    def _bm25(query: list[str], documents: list[Counter], k1: float = 1.5, b: float = 0.75) -> list[float]:
        if not documents or not query:
            return [0.0] * len(documents)
        df = Counter(t for doc in documents for t in doc)
        n = len(documents)
        avg = sum(sum(d.values()) for d in documents) / max(n, 1)
        scored = []
        for doc in documents:
            length = sum(doc.values())
            score = 0.0
            for term in set(query):
                tf = doc[term]
                if not tf:
                    continue
                idf = math.log1p((n - df[term] + 0.5) / (df[term] + 0.5))
                score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * length / max(avg, 1)))
            scored.append(score)
        return scored

    def search(
        self, question: str, principal: Principal, method: str = "hybrid",
        k: int = 5, as_of: str = "2026-10-12", candidate_pool: int = 30,
    ) -> list[Result]:
        if k < 1 or k > 50 or candidate_pool < k:
            raise ValueError("Invalid k/candidate_pool")
        if method not in {"bm25", "char", "hybrid", "dense", "hybrid_dense"}:
            raise ValueError("Unknown retrieval method")
        if method in {"dense", "hybrid_dense"} and not self.encoder:
            raise ValueError("Dense method requires optional real embedding encoder")
        visible = self._visible(principal, as_of)
        if not visible:
            return []
        query = tokens(question)
        if not query:
            return []
        sparse = self._bm25(query, [self._tf[i] for i in visible])
        grams = self._bm25(char_ngrams(question), [self._grams[i] for i in visible])
        dense = None
        if method in {"dense", "hybrid_dense"}:
            qvec = self.encoder.encode([question])[0]
            dense = [_cosine(qvec, self._dense_vectors[i]) for i in visible]
        components = []
        if method in {"bm25", "hybrid", "hybrid_dense"}:
            components.append(("bm25", sparse))
        if method in {"char", "hybrid", "hybrid_dense"}:
            components.append(("char", grams))
        if dense is not None:
            components.append(("dense", dense))
        if len(components) == 1:
            name, scores = components[0]
            candidates = [(visible[pos], score) for pos, score in enumerate(scores) if score > 0]
            candidates.sort(key=lambda item: (-item[1], self.passages[item[0]].uid))
            return [Result(self.passages[i], score, name) for i, score in candidates[:k]]
        # Reciprocal Rank Fusion across independent rankers, excluding zero-score matches.
        fused = defaultdict(float)
        for _, scores in components:
            ranks = sorted(
                ((visible[pos], value) for pos, value in enumerate(scores) if value > 0),
                key=lambda pair: (-pair[1], self.passages[pair[0]].uid),
            )[:candidate_pool]
            for rank, (idx, _) in enumerate(ranks, start=1):
                fused[idx] += 1 / (60 + rank)
        ranked = sorted(fused.items(), key=lambda pair: (-pair[1], self.passages[pair[0]].uid))
        return [Result(self.passages[i], score, method) for i, score in ranked[:k]]

class GroundedQA:
    """Extractive baseline. All answers remain verbatim data snippets, not generative claims."""
    def __init__(self, index: EnterpriseIndex):
        self.index = index

    def answer(self, question: str, principal: Principal, method: str = "hybrid", as_of: str = "2026-10-12") -> dict:
        hits = self.index.search(question, principal, method=method, as_of=as_of, k=3)
        if not hits:
            return {"status": "abstained", "answer": None, "citations": [], "reason": "no_evidence", "mode": "extractive"}
        top = hits[0].passage
        qterms = set(tokens(question))
        evidence_terms = set(tokens(top.title + " " + top.text))
        # Support is a lexical coverage heuristic, NEVER calibrated probability.
        # Compute IDF on only documents this trusted principal can read.
        authorized = [self.index.passages[i] for i in self.index._visible(principal, as_of)]
        df = Counter(t for p in authorized for t in set(tokens(p.title + " " + p.text)))
        n = len(authorized)
        weight = lambda term: math.log((n + 1) / (df.get(term, 0) + 1)) + 1.0
        total = sum(weight(t) for t in qterms)
        coverage = sum(weight(t) for t in qterms.intersection(evidence_terms)) / total if total else 0
        # Fixed engineering baseline threshold: analyze errors on the dev split.
        if len(qterms.intersection(evidence_terms)) < min(2, len(qterms)) or coverage < 0.55:
            return {"status": "abstained", "answer": None, "citations": [],
                    "reason": "weak_lexical_support", "lexical_coverage": round(coverage, 4), "mode": "extractive"}
        if UNTRUSTED_INSTRUCTION.search(top.text):
            return {"status": "abstained", "answer": None, "citations": [hits[0].to_dict()],
                    "reason": "suspicious_document_content", "mode": "extractive"}
        # This response deliberately does not claim answer-level entailment.
        excerpt = top.text[:700]
        return {"status": "evidence_found", "answer": excerpt, "citations": [h.to_dict() for h in hits],
                "reason": "extracted_snippet_not_entailed", "mode": "extractive",
                "verbatim_source": top.uid, "lexical_coverage": round(coverage, 4)}
