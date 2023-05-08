import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    OPEN_API_KEY = os.getenv("OPEN_API_KEY")
