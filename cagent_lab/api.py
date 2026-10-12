"""Optional FastAPI adapter. Install requirements-api.txt; never enables remote LLM by default."""
from pathlib import Path
from .core import BM25Index, GroundedAssistant, SafeAgent, Document, chunk_text
from .evaluate import load_corpus

try:
    from fastapi import FastAPI
    from pydantic import BaseModel, Field
except ImportError as exc:
    raise RuntimeError("pip install -r cagent_lab/requirements-api.txt") from exc

base = Path(__file__).resolve().parent
documents = load_corpus(base / "data" / "knowledge")
assistant = GroundedAssistant(BM25Index(documents))
agent = SafeAgent(assistant)
app = FastAPI(title="C-Agent Capability Lab", version="0.1.0")

class Query(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    k: int = Field(default=3, ge=1, le=10)

class ToolCall(BaseModel):
    tool: str
    question: str = Field(default="", max_length=2000)

@app.get("/health")
def health():
    return {"status": "ok", "document_chunks": len(assistant.index.documents), "llm_enabled": False}

@app.post("/query")
def query(payload: Query):
    return assistant.answer(payload.question, payload.k)

@app.post("/agent")
def call_agent(payload: ToolCall):
    return agent.run(payload.tool, payload.question)
