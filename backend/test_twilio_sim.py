import requests

url = "http://127.0.0.1:8000/whatsapp"
payload = {
    "From": "whatsapp:+917012402897",
    "Body": "I need loan for business"
}

try:
    print(f"Sending text: '{payload['Body']}' from {payload['From']}...")
    response = requests.post(url, data=payload)
    print("\n--- Server Response (TwiML) ---")
    print(response.text)
    print("-------------------------------")
except Exception as e:
    print(f"Error: {e}")
