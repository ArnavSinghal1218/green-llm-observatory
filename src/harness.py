import json
import os
import re
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

MAX_ATTEMPTS = 3
RETRYABLE = ("429", "500", "503")

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(
        timeout=60000,
        retry_options=types.HttpRetryOptions(attempts=1),
    ),
)


def call_model(model, prompt):
    """Send one prompt, retrying temporary server errors with a growing pause."""
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
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
                "attempts": attempt,
                "error": None,
            }
        except Exception as e:
            last_error = str(e)[:300]
            latency = round(time.time() - start, 3)
            if attempt == MAX_ATTEMPTS or not any(c in last_error for c in RETRYABLE):
                break
            time.sleep(2 ** attempt)  # wait 2s, then 4s
    return {
        "output": "",
        "latency_s": latency,
        "input_tokens": None,
        "output_tokens": None,
        "thought_tokens": None,
        "total_tokens": None,
        "attempts": attempt,
        "error": last_error,
    }


def parse_json_lenient(text):
    """Strip code fences and unwrap a one-item list, then parse."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    data = json.loads(cleaned)
    if isinstance(data, list) and len(data) == 1:
        data = data[0]
    return data


def check_answer(item, output):
    """Return (strict_correct, lenient_correct)."""
    if item["check"] == "exact_match":
        ok = output.strip().strip(".").lower() == str(item["expected"]).lower()
        return ok, ok
    if item["check"] == "json_equals":
        try:
            strict = json.loads(output) == item["expected"]
        except json.JSONDecodeError:
            strict = False
        try:
            lenient = parse_json_lenient(output) == item["expected"]
        except json.JSONDecodeError:
            lenient = False
        return strict, lenient
    return False, False


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
                if res["error"] is None:
                    strict, lenient = check_answer(item, res["output"])
                else:
                    strict, lenient = False, False
                row = {
                    "run_id": run_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": model,
                    "prompt_id": item["id"],
                    "category": item["category"],
                    "correct": strict,
                    "lenient_correct": lenient,
                    **res,
                }
                f.write(json.dumps(row) + "\n")
                status = "OK  " if strict else ("FMT " if lenient else "FAIL")
                print(f"{status} {model:26} {item['id']:9} {res['latency_s']:5.1f}s "
                      f"tokens={res['total_tokens']} attempts={res['attempts']} "
                      f"{res['error'] or ''}")
                time.sleep(2)

    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()