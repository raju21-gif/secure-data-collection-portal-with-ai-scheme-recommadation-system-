import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    print("API Key not found.")
    exit(1)

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5173", # Recommended by OpenRouter
    "X-Title": "LocalDev"
}
# Testing Paid model with limits
payload = {
    "model": "deepseek/deepseek-r1",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 1000 # Limit so it fits in budget
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
