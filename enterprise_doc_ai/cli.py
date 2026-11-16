"""Local CLI for inspection, retrieval, invoice extraction and review workflow."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .engine import EnterpriseIndex, GroundedQA, Principal, load_corpus
from .extract import extract_invoice, read_pages
from .workflow import ReviewWorkflow

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["ask", "search", "invoice", "workflow"])
    p.add_argument("text", help="question, or path to a local invoice")
    p.add_argument("--tenant", choices=["alpha", "beta"], default="alpha")
    p.add_argument("--roles", default="employee", help="comma-separated simulated user roles")
    p.add_argument("--method", choices=["hybrid", "bm25", "char"], default="hybrid")
    args = p.parse_args()
    principal = Principal(args.tenant, frozenset(x.strip() for x in args.roles.split(",") if x.strip()), "cli-user")
    if args.command == "invoice":
        contents = read_pages(args.text)
        answers = [extract_invoice(text, Path(args.text).name, page) for page, text in contents]
        result = {"extracted_pages": answers, "pages": len(answers)}
    else:
        index = EnterpriseIndex(load_corpus())
        if args.command == "ask":
            result = GroundedQA(index).answer(args.text, principal, args.method)
        elif args.command == "search":
            result = [h.to_dict() for h in index.search(args.text, principal, method=args.method)]
        else:
            result = ReviewWorkflow(index).prepare(args.text, principal)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
