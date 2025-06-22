from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.getenv("GeminiKey")

client = genai.Client(api_key=google_api_key)

response = client.models.generate_content(
    model="Gemini 2.5 Flash-Lite Preview 06-17",
    contents="Explain how AI works in a few words",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
    ),
)

try:
    print("Response from Gemini API:")
    print(response.text)

except AttributeError:
    print("Response does not have a 'text' attribute. Here is the full response:")
    print(response)