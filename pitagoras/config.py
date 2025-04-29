# pitagoras/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base configuration
BASE_URL = os.getenv("API_BASE_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
DEFAULT_USER_EMAIL = os.getenv("DEFAULT_USER_EMAIL", "jcorona@epa.digital")

# API endpoints
ENDPOINTS = {
    "customers": f"{BASE_URL}/customers",
    "google_ads": f"{BASE_URL}/adwords/report",
    "facebook_ads": f"{BASE_URL}/facebook/report",
    "google_analytics": f"{BASE_URL}/analytics4/report",
}