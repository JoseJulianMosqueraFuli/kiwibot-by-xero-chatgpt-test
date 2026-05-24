import json
import requests
from app.config import Config
from app.logging_config import get_logger

logger = get_logger(__name__)

FIREBASE_API_KEY = Config.FIREBASE_API_KEY
rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


def sign_in_with_email_and_password(
    email: str, password: str, return_secure_token: bool = True
) -> dict:
    payload = json.dumps(
        {"email": email, "password": password, "returnSecureToken": return_secure_token}
    )
    try:
        r = requests.post(rest_api_url, params={"key": FIREBASE_API_KEY}, data=payload)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Firebase authentication error: {e}")
        raise
