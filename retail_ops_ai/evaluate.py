"""Deterministic retrieval evaluation; no metric ever hard-coded."""
from __future__ import annotations
from pathlib import Path
import json
import statistics
import time
from .core import RetailService,Principal

def evaluate():
    svc=RetailService()
    cases=json.loads((Path(__file__).parent/"data"/"eval.json").read_text(encoding="utf-8"))
    positives=[]; negatives=[]; per_case=[]; leaks=0; times=[]
    for i,case in enumerate(cases):
        p=Principal(case["store"],case["role"])
        before=time.perf_counter()
        hits=svc.policy_search(p,case["question"],k=3)["evidence"]
        times.append((time.perf_counter()-before)*1000)
        expected=set(case["gold"])
        actual=[h["family"] for h in hits]
        if expected:
            rank=next((j+1 for j,name in enumerate(actual) if name in expected),None)
            positives.append((float(bool(rank)),1/rank if rank else 0))
        else:
            negatives.append(float(not hits))
        visible={s.uid for s in svc._visible(p,"2026-10-12")}
        leaks+=sum(1 for h in hits if h["id"] not in visible)
        per_case.append({"index":i,"expected":sorted(expected),"retrieved":actual,"hit":bool(expected.intersection(actual))})
    return {"fixture":"synthetic-public","total":len(cases),"answerable":len(positives),"negative":len(negatives),
            "hit_at_3":round(statistics.mean([x[0] for x in positives]),4) if positives else None,
            "mrr_at_3":round(statistics.mean([x[1] for x in positives]),4) if positives else None,
            "zero_hit_negative_rate":round(statistics.mean(negatives),4) if negatives else None,
            "access_leakage_count":leaks,"median_ms_local":round(statistics.median(times),4),
            "limitations":"Public handcrafted labels; retrieval only, not LLM factual accuracy",
            "per_case":per_case}
def main():
    print(json.dumps(evaluate(),indent=2,ensure_ascii=False))
if __name__=="__main__":main()
