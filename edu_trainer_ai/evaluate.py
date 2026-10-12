"""Reproducible education course retrieval evaluation (public synthetic questions)."""
from __future__ import annotations
from pathlib import Path
import json
import statistics
import time
from .core import EduService,Learner

def evaluate():
    cases=json.loads((Path(__file__).parent/"data"/"eval.json").read_text(encoding="utf-8"))
    svc=EduService()
    positives=[];negatives=[];errors=0;results=[];latencies=[]
    for case in cases:
        who=Learner(case["track"],case["role"])
        before=time.perf_counter()
        hits=svc.search(who,case["question"])["evidence"]
        latencies.append((time.perf_counter()-before)*1000)
        truth=case["gold"]; ids=[item["id"] for item in hits]
        if truth:
            rank=ids.index(truth)+1 if truth in ids else None
            positives.append((float(bool(rank)),1/rank if rank else 0))
        else:
            negatives.append(float(not hits))
        permitted={d.uid for d in svc._visible(who)}
        errors+=sum(item["id"] not in permitted for item in hits)
        results.append({"question":case["question"],"gold":truth,"hits":ids})
    return {"fixture":"fictional-public","cases":len(cases),
            "answerable":len(positives),"negative":len(negatives),
            "hit_at_3":round(statistics.mean(p[0] for p in positives),4) if positives else None,
            "mrr_at_3":round(statistics.mean(p[1] for p in positives),4) if positives else None,
            "zero_hit_negative_rate":round(statistics.mean(negatives),4) if negatives else None,
            "access_leakage_count":errors,"median_ms_local":round(statistics.median(latencies),4),
            "limitations":"Public small fixture; keyword baseline; no blind NLP or real student evaluation",
            "cases_detail":results}
def main():
    print(json.dumps(evaluate(),indent=2,ensure_ascii=False))
if __name__=="__main__":main()
