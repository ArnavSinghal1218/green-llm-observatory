import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(
        timeout=20000,  # give up after 20 seconds (milliseconds)
        retry_options=types.HttpRetryOptions(attempts=1),  # no silent retries
    ),
)

candidates = [
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemma-4-26b-a4b-it",
]

for name in candidates:
    start = time.time()
    try:
        r = client.models.generate_content(
            model=name,
            contents="Reply with the single word: ready",
        )
        secs = time.time() - start
        print(f"OK     {name:30} {secs:4.1f}s  -> {r.text.strip()[:40]}")
        print(f"       tokens: {r.usage_metadata}")
    except Exception as e:
        secs = time.time() - start
        print(f"FAILED {name:30} {secs:4.1f}s  -> {str(e)[:150]}")