import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    OPEN_API_KEY = os.getenv("OPEN_API_KEY")
    SERVICE_ACCOUNT_KEY_FILE = os.getenv("SERVICE_ACCOUNT_KEY_FILE")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
