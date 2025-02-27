import secrets
import os

api_key = secrets.token_urlsafe(32)  # Generates a 32-byte secure key

API_KEY = os.environ.get("API_KEY")
if API_KEY is None:
    with open(".env", "a") as f:
        f.write(f"API_KEY={api_key}\n")
else:
    print("API key already exists.")