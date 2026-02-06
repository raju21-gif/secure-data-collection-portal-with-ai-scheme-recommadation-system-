import requests
import json

try:
    response = requests.post('http://localhost:5000/recommend', json={'age': 25})
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
