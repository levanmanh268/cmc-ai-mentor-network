# Mentor ranking latency benchmark

Run the local CPU-only benchmark with:

```powershell
python -m scripts.benchmark_mentor_ranking
python -m pytest tests/test_mentor_ranking_benchmark.py -q
```

The script measures `get_top_matches(..., top_k=3)` once per mentor-pool size
for a first-call sample and then 100 warm samples. It reports cold milliseconds,
warm p50/p95/max, Python/platform/CPU metadata, and the pool sizes. The standard
p95 calculation is shared with `scripts.final_smoke_audit.py`.

The five-record pool uses the fictional demo mentors. Larger pools are
deterministic synthetic expansions made by repeating those five templates with
unique IDs and names. They help show how this implementation scales with pool
length, but they are not representative real-world data and should not be
presented as evidence about real mentor profiles.

## Local sample

Windows, Python 3.14.5, Intel64 Family 6 Model 186 Stepping 3, 12 logical CPUs;
five fictional templates; `top_k=3`; one first-call sample and 100 warm samples
for each pool:

| Pool size | First-call (ms) | Warm p50 (ms) | Warm p95 (ms) | Warm max (ms) |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 22.036 | 2.917 | 6.339 | 8.789 |
| 50 | 7.134 | 9.379 | 14.606 | 16.882 |
| 250 | 39.559 | 25.427 | 31.628 | 46.156 |
| 1,000 | 98.049 | 97.320 | 112.028 | 161.087 |

The pool sizes above 5 repeat fictional demo records. First-call timings vary
with interpreter/runtime state and should not be interpreted as strictly
increasing with pool size.

Cold means the first ranking request after Python imports and pool construction;
it does not include process startup or repository creation. These local
measurements omit Streamlit/browser time, concurrent load, network, external LLM
calls, and production data. They are descriptive samples, not an SLA or a
pass/fail threshold. Record actual output and environment before drawing
conclusions.
