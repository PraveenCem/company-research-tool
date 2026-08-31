import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
cse_id = os.getenv("GOOGLE_CSE_ID")

print("API key loaded:", bool(api_key))
print("CSE ID loaded:", bool(cse_id))

url = "https://www.googleapis.com/customsearch/v1"

params = {
    "key": api_key,
    "cx": cse_id,
    "q": "Microsoft recent news",
    "num": 5,
}

response = httpx.get(
    url,
    params=params,
    timeout=15,
)

print("\nStatus:", response.status_code)
print("\nResponse:")
print(response.text)