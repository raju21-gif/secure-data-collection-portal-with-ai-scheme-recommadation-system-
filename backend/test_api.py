import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

print(f"Testing API Key: {api_key[:10]}...{api_key[-4:] if api_key else 'None'}")

if not api_key:
    print("ERROR: No API Key found in .env")
    exit(1)

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "deepseek/deepseek-r1",
    "messages": [
        {"role": "user", "content": "Say hello"}
    ]
}

try:
    print("Sending request...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Connection Error: {e}")
