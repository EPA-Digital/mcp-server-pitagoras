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
    "analytics4_metadata": f"{BASE_URL}/analytics4/metadata",
    "facebook_schema": f"{BASE_URL}/facebook/schema",
    "adwords_resources": f"{BASE_URL}/adwords/resources",
    "adwords_attributes": f"{BASE_URL}/adwords/attributes",
    "adwords_segments": f"{BASE_URL}/adwords/segments",
    "adwords_metrics": f"{BASE_URL}/adwords/metrics",
}
