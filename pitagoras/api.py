# pitagoras/api.py
import httpx
import logging
from typing import Dict, List, Any, Optional

from .config import ENDPOINTS, AUTH_TOKEN, DEFAULT_USER_EMAIL

logger = logging.getLogger("pitagoras.api")


async def get_customers(user_email: str = DEFAULT_USER_EMAIL) -> List[Dict[str, Any]]:
    """Get list of customers for a specific user"""
    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN
            
        response = await client.post(
            ENDPOINTS["customers"],
            json={"user_email": user_email},
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Received {len(data.get('customers', []))} customers")
        return data.get("customers", [])


async def get_google_ads_report(
    accounts: List[Dict[str, str]],
    attributes: List[Dict[str, Any]],
    segments: List[str],
    metrics: List[str],
    resource: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """Get Google Ads report data"""
    payload = {
        "accounts": accounts,
        "attributes": attributes,
        "segments": segments,
        "metrics": metrics,
        "resource": resource,
        "start_date": start_date,
        "end_date": end_date
    }
    
    logger.info(f"Requesting Google Ads data with payload: {payload}")
    
    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN
            
        response = await client.post(
            ENDPOINTS["google_ads"],
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Received Google Ads data with {len(data.get('rows', []))} rows")
        return data


async def get_facebook_ads_report(
    customer_id: str,
    accounts: List[str],
    fields: List[str],
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """Get Facebook Ads report data"""
    parsed_accounts = [{"account_id": account_id, "name": f"Account {account_id}"} for account_id in accounts]
    
    payload = {
        "provider": "fb",
        "customer": customer_id,
        "query_name": "data_fb",
        "parsed_accounts": parsed_accounts,
        "accounts": accounts,
        "date_range": {
            "start": start_date,
            "end": end_date
        },
        "fields": fields
    }
    
    logger.info(f"Requesting Facebook Ads data with payload: {payload}")
    
    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN
            
        response = await client.post(
            ENDPOINTS["facebook_ads"],
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Received Facebook Ads data with {len(data.get('rows', []))} rows")
        return data


async def get_google_analytics_report(
    accounts: List[Dict[str, str]],
    dimensions: List[str],
    metrics: List[str],
    start_date: str,
    end_date: str,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get Google Analytics report data"""
    payload = {
        "accounts": accounts,
        "dimensions": dimensions,
        "metrics": metrics,
        "start_date": start_date,
        "end_date": end_date
    }
    
    if filters:
        payload["filters"] = filters
    
    logger.info(f"Requesting Google Analytics data with payload: {payload}")
    
    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN
            
        response = await client.post(
            ENDPOINTS["google_analytics"],
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Received Google Analytics data with {len(data.get('rows', []))} rows")
        return data