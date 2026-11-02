import json
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
latest = sorted(RESULTS_DIR.glob("run_*.jsonl"))[-1]
rows = [json.loads(line) for line in latest.read_text(encoding="utf-8").splitlines()]
print("Run file:", latest.name, "\n")

print("--- FAILURES ---")
for r in rows:
    if not r["correct"]:
        kind = "SERVER ERROR" if r["error"] else "WRONG OUTPUT"
        detail = r["error"] or r["output"]
        print(f"{r['model']} | {r['prompt_id']} | {kind}")
        print("   ", repr(detail)[:300])

print("\n--- SUMMARY PER MODEL ---")
by_model = defaultdict(list)
for r in rows:
    by_model[r["model"]].append(r)

for model, rs in by_model.items():
    answered = [r for r in rs if r["error"] is None]
    right = sum(r["correct"] for r in answered)
    avg_tokens = sum(r["total_tokens"] for r in answered) / len(answered) if answered else 0
    avg_lat = sum(r["latency_s"] for r in answered) / len(answered) if answered else 0
    print(f"{model:26} calls={len(rs)} errors={len(rs) - len(answered)} "
          f"correct={right}/{len(answered)} avg_tokens={avg_tokens:.0f} avg_latency={avg_lat:.1f}s")