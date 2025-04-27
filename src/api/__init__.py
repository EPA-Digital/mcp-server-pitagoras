"""
API para interactuar con Pitágoras.
"""

from api.client import PitagorasClient
from api.endpoints import (
    get_analytics_channel_report,
    get_analytics_hourly_report,
    get_analytics_report,
    get_customers,
    get_facebook_report,
    get_google_ads_report,
)

__all__ = [
    'PitagorasClient',
    'get_customers',
    'get_google_ads_report',
    'get_facebook_report',
    'get_analytics_report',
    'get_analytics_channel_report',
    'get_analytics_hourly_report',
]