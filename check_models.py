import os, requests
from dotenv import load_dotenv
load_dotenv()
key = os.getenv("TYPHOON_API_KEY")
r = requests.get("https://api.opentyphoon.ai/v1/models", headers={"Authorization": f"Bearer {key}"})
data = r.json()
print(data)
if isinstance(data, list):
    for m in data:
        print(m.get("id") if isinstance(m, dict) else m)
elif isinstance(data, dict):
    for m in data.get("data", []):
        print(m.get("id"))
