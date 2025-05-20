# pitagoras/config.py
import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("pitagoras-mcp")

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = "https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1"
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

if not AUTH_TOKEN:
    logger.warning("AUTH_TOKEN not found in environment variables")

# API endpoints
ENDPOINTS = {
    "customers": f"{API_BASE_URL}/customers",
    "google_ads": f"{API_BASE_URL}/adwords/report",
    "google_ads_metadata": f"{API_BASE_URL}/adwords/metrics",
    "facebook": f"{API_BASE_URL}/facebook/report",
    "facebook_metadata": f"{API_BASE_URL}/facebook/schema",
    "analytics4": f"{API_BASE_URL}/analytics4/report",
    "analytics4_metadata": f"{API_BASE_URL}/analytics4/metadata",
}

# Default headers for API requests
def get_headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": AUTH_TOKEN,
    }