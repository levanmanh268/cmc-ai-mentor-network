"""Independent C-Agent-inspired document intelligence engineering case study.

Not affiliated with CMC's proprietary C-Agent implementation.
"""
from .engine import Principal, Passage, EnterpriseIndex, GroundedQA, load_corpus
from .workflow import ReviewWorkflow
from .extract import extract_invoice
__all__ = ["Principal", "Passage", "EnterpriseIndex", "GroundedQA", "load_corpus", "ReviewWorkflow", "extract_invoice"]
