import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # reads the .env file

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"],
                      http_options=types.HttpOptions(timeout=30000), # 30 seconds, in milliseconds
                      )

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",  # check AI Studio for a current model name
    contents="In one sentence, what is carbon intensity of electricity?",
)

print(response.text)
print(response.usage_metadata)