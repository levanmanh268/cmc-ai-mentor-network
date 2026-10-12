"""Run the same retrieval pipeline without any API key or third-party packages."""
import argparse
import json
from pathlib import Path
from .core import BM25Index, TFIDFIndex, GroundedAssistant
from .evaluate import load_corpus

def main():
    p = argparse.ArgumentParser()
    p.add_argument("question", type=str)
    p.add_argument("--method", choices=["bm25", "tfidf"], default="bm25")
    args = p.parse_args()
    folder = Path(__file__).resolve().parent / "data" / "knowledge"
    docs = load_corpus(folder)
    index = BM25Index(docs) if args.method == "bm25" else TFIDFIndex(docs)
    print(json.dumps(GroundedAssistant(index).answer(args.question), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
