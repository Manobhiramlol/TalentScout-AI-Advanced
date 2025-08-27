import requests

api_key = "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"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
print(f"Status Code: {response.status_code}")