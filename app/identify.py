import json
import requests
from app.config import Config

FIREBASE_API_KEY = Config.FIREBASE_API_KEY
rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


def sign_in_with_email_and_password(
    email: str, password: str, return_secure_token: bool = True
):
    payload = json.dumps(
        {"email": email, "password": password, "returnSecureToken": return_secure_token}
    )
    r = requests.post(rest_api_url, params={"key": FIREBASE_API_KEY}, data=payload)
    return r.json()
