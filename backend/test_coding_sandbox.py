import requests
import json

url = "http://127.0.0.1:8000/interview/submit"

payload = {
    "role": "Python Developer",
    "question": "Write a function to reverse a string.",
    "answer": "Here is my code.",
    "code": "def reverse_string(s):\n    return s[::-1]",
    "mode": "practice",
    "language": "English",
    "current_difficulty": 5
}

try:
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
    response = requests.post(url, json=payload)
    response.raise_for_status()
    print("Status Code:", response.status_code)
    data = response.json()
    print("Response Evaluation:")
    print(json.dumps(data.get("evaluation", {}), indent=2))
    
    if "evaluation" in data:
        print("\nTEST PASSED: received evaluation.")
    else:
        print("\nTEST FAILED: evaluation missing.")

except Exception as e:
    print(f"TEST FAILED: {e}")
    if hasattr(e, 'response') and e.response:
        print("Server Response:", e.response.text)
