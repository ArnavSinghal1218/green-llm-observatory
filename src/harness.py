import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_FILE = ROOT / "prompts" / "prompts.json"
MODELS_FILE = ROOT / "config" / "models.json"
RESULTS_DIR = ROOT / "results"

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(
        timeout=60000,
        retry_options=types.HttpRetryOptions(attempts=1),
    ),
)


def call_model(model, prompt):
    """Send one prompt to one model and measure what happened."""
    start = time.time()
    try:
        r = client.models.generate_content(model=model, contents=prompt)
        u = r.usage_metadata
        return {
            "output": (r.text or "").strip(),
            "latency_s": round(time.time() - start, 3),
            "input_tokens": u.prompt_token_count,
            "output_tokens": u.candidates_token_count,
            "thought_tokens": u.thoughts_token_count or 0,
            "total_tokens": u.total_token_count,
            "error": None,
        }
    except Exception as e:
        return {
            "output": "",
            "latency_s": round(time.time() - start, 3),
            "input_tokens": None,
            "output_tokens": None,
            "thought_tokens": None,
            "total_tokens": None,
            "error": str(e)[:300],
        }


def check_answer(item, output):
    """Return True if the model's output matches the expected answer."""
    if item["check"] == "exact_match":
        cleaned = output.strip().strip(".").lower()
        return cleaned == str(item["expected"]).lower()
    if item["check"] == "json_equals":
        try:
            return json.loads(output) == item["expected"]
        except json.JSONDecodeError:
            return False
    return False


def main():
    prompts = json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))
    models = json.loads(MODELS_FILE.read_text(encoding="utf-8"))

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / f"run_{run_id}.jsonl"

    with out_path.open("w", encoding="utf-8") as f:
        for model in models:
            for item in prompts:
                res = call_model(model, item["prompt"])
                correct = res["error"] is None and check_answer(item, res["output"])
                row = {
                    "run_id": run_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": model,
                    "prompt_id": item["id"],
                    "category": item["category"],
                    "correct": correct,
                    **res,
                }
                f.write(json.dumps(row) + "\n")
                status = "OK  " if correct else "FAIL"
                print(f"{status} {model:26} {item['id']:9} {res['latency_s']:5.1f}s "
                      f"tokens={res['total_tokens']} {res['error'] or ''}")
                time.sleep(2)  # be gentle with free-tier rate limits

    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()