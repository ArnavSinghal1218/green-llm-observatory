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
PROMPT_FILES = [ ROOT / "prompts" / "prompts.json",
                ROOT / "prompts" / "prompts_multilingual.json",
                ROOT / "prompts" / "prompts_hard.json",
                ROOT / "prompts" / "prompts_hard2.json",]

MODELS_FILE = ROOT / "config" / "models.json"
#RESULTS_DIR = ROOT / "results"
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", ROOT / "results"))
PROMPT_LIMIT = int(os.environ.get("PROMPT_LIMIT", "0"))

MAX_ATTEMPTS = 3
RETRYABLE_CODES = {429, 500, 503, 504}
HARNESS_VERSION = "1.8"
#REPEATS = 3
REPEATS = int(os.environ.get("REPEATS", "3"))
TEMPERATURE = 0

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"].strip(),
    http_options=types.HttpOptions(
        timeout=60000,
        retry_options=types.HttpRetryOptions(attempts=1),
    ),
)


def call_model(model, prompt):
    """Send one prompt, retrying temporary server errors with a growing pause."""
    t0 = time.time()
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        start = time.time()
        try:
            r = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=TEMPERATURE),
            )
            u = r.usage_metadata
            return {
                "output": (r.text or "").strip(),
                "latency_s": round(time.time() - start, 3),
                "total_latency_s": round(time.time() - t0, 3),
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
            code = getattr(e, "code", None)
            if attempt == MAX_ATTEMPTS or code not in RETRYABLE_CODES:
                break
            time.sleep(15 if code == 429 else 2 ** attempt)
        #except Exception as e:
        #    last_error = str(e)[:300]
        #    latency = round(time.time() - start, 3)
        #    if attempt == MAX_ATTEMPTS or not any(c in last_error for c in RETRYABLE):
        #        break
        #    time.sleep(2 ** attempt)
    return {
        "output": "",
        "latency_s": latency,
        "total_latency_s": round(time.time() - t0, 3),
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


def last_number(text):
    nums = re.findall(r"-?\d+(?:\.\d+)?", text)
    return nums[-1] if nums else None


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def check_answer(item, output):
    """Return (strict_correct, lenient_correct)."""
    kind = item["check"]
    if kind == "exact_match":
        strict = output.strip().strip(".").lower() == str(item["expected"]).lower()
        lenient = strict
        if not strict and is_number(str(item["expected"])):
            lenient = last_number(output) == str(item["expected"])
        return strict, lenient
    if kind == "max_words":
        ok = len(output.split()) <= item["expected"]
        return ok, ok
    if kind == "exact_words":
        ok = len(output.split()) == item["expected"]
        return ok, ok
    if kind == "regex_match":
        ok = re.fullmatch(item["expected"], output.strip()) is not None
        return ok, ok
    if kind == "json_equals":
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


#def check_answer(item, output):
#    """Return (strict_correct, lenient_correct)."""
#    if item["check"] == "exact_match":
#        ok = output.strip().strip(".").lower() == str(item["expected"]).lower()
#        return ok, ok
#    if item["check"] == "max_words":
#        ok = len(output.split()) <= item["expected"]
#        return ok, ok
#    if item["check"] == "regex_match":
#        ok = re.fullmatch(item["expected"], output.strip()) is not None
#        return ok, ok
#    if item["check"] == "json_equals":
#        try:
#            strict = json.loads(output) == item["expected"]
#        except json.JSONDecodeError:
#            strict = False
#        try:
#            lenient = parse_json_lenient(output) == item["expected"]
#        except json.JSONDecodeError:
#            lenient = False
#        return strict, lenient
#    return False, False


def main():
    # prompts = json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))
    prompts = []
    for pf in PROMPT_FILES:
        prompts += json.loads(pf.read_text(encoding="utf-8"))
    if PROMPT_LIMIT:
        prompts = prompts[:PROMPT_LIMIT]
    models = json.loads(MODELS_FILE.read_text(encoding="utf-8"))

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / f"run_{run_id}.jsonl"

    with out_path.open("w", encoding="utf-8") as f:
        for repeat in range(1, REPEATS + 1):
            for model in models:
                for item in prompts:
                    res = call_model(model, item["prompt"])
                    if res["error"] is None:
                        strict, lenient = check_answer(item, res["output"])
                    else:
                        strict, lenient = False, False
                    row = {
                        "run_id": run_id,
                        "repeat": repeat,
                        "temperature": TEMPERATURE,
                        "harness_version": HARNESS_VERSION,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "model": model,
                        "prompt_id": item["id"],
                        "category": item["category"],
                        "language": item.get("language", "en"),
                        "pair_id": item.get("pair_id", item["id"]),
                        "correct": strict,
                        "lenient_correct": lenient,
                        **res,
                    }
                    f.write(json.dumps(row) + "\n")
                    status = "OK  " if strict else ("FMT " if lenient else "FAIL")
                    print(f"r{repeat} {status} {model:26} {item['id']:9} "
                          f"{res['total_latency_s']:5.1f}s tokens={res['total_tokens']} "
                          f"attempts={res['attempts']} {res['error'] or ''}")
                    time.sleep(2)

    print(f"\nSaved: {out_path}")
    return out_path


if __name__ == "__main__":
    main()