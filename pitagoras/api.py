# pitagoras/api.py
import json
import httpx
import logging
from typing import Dict, List, Any, Optional, Union

from .config import ENDPOINTS, get_headers, logger

class PitagorasAPI:
    """Client for interacting with the Pitagoras API."""
    
    @staticmethod
    async def get_customers(user_email: str) -> Dict[str, Any]:
        """Fetch customers and their accounts."""
        logger.info(f"Fetching customers for email: {user_email}")
        
        async with httpx.AsyncClient() as client:
            payload = {"user_email": user_email}
            logger.debug(f"Request payload: {json.dumps(payload)}")
            
            response = await client.post(
                ENDPOINTS["customers"],
                headers=get_headers(),
                json=payload,
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved {len(data.get('customers', []))} customers")
            return data
    
    @staticmethod
    async def get_google_ads_data(
        accounts: List[Dict[str, str]], 
        attributes: List[Dict[str, Any]],
        segments: List[str],
        metrics: List[str],
        resource: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Fetch Google Ads data."""
        logger.info(f"Fetching Google Ads data for {len(accounts)} accounts")
        
        # Create request payload
        payload = {
            "accounts": accounts,
            "attributes": attributes,
            "segments": segments,
            "metrics": metrics,
            "resource": resource,
            "start_date": start_date,
            "end_date": end_date
        }
        
        logger.debug(f"Google Ads request payload: {json.dumps(payload)}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ENDPOINTS["google_ads"],
                headers=get_headers(),
                json=payload,
                timeout=60.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Rename cost_micros to cost in headers
            if "headers" in data:
                data["headers"] = [
                    "cost" if h == "metrics.cost_micros" else h 
                    for h in data["headers"]
                ]
            
            logger.info(f"Retrieved {len(data.get('rows', []))} rows of Google Ads data")
            return data
    
    @staticmethod
    async def get_facebook_data(
        accounts: List[Dict[str, str]],
        fields: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Fetch Facebook Ads data."""
        logger.info(f"Fetching Facebook Ads data for {len(accounts)} accounts")
        
        # Create request payload
        payload = {
            "accounts": accounts,
            "fields": fields,
            "start_date": start_date,
            "end_date": end_date
        }
        
        logger.debug(f"Facebook Ads request payload: {json.dumps(payload)}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ENDPOINTS["facebook"],
                headers=get_headers(),
                json=payload,
                timeout=60.0
            )
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved {len(data.get('rows', []))} rows of Facebook Ads data")
            return data
    
    @staticmethod
    async def get_analytics_data(
        accounts: List[Dict[str, str]],
        dimensions: List[str],
        metrics: List[str],
        start_date: str,
        end_date: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fetch Google Analytics data."""
        logger.info(f"Fetching Google Analytics data for {len(accounts)} accounts")
        
        # Create request payload
        payload = {
            "accounts": accounts,
            "dimensions": dimensions,
            "metrics": metrics,
            "start_date": start_date,
            "end_date": end_date
        }
        
        # Add filters if provided
        if filters:
            payload["filters"] = filters
        
        logger.debug(f"Google Analytics request payload: {json.dumps(payload)}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ENDPOINTS["analytics4"],
                headers=get_headers(),
                json=payload,
                timeout=60.0
            )
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved {len(data.get('rows', []))} rows of Google Analytics data")
            return data
            
    @staticmethod
    async def get_google_ads_metadata(resource_name: str) -> List[str]:
        """Fetch Google Ads metadata."""
        logger.info(f"Fetching Google Ads metadata for resource: {resource_name}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ENDPOINTS['google_ads_metadata']}?resource_name={resource_name}",
                headers=get_headers(),
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved {len(data)} Google Ads metrics")
            return data
    
    @staticmethod
    async def get_facebook_metadata() -> Dict[str, Any]:
        """Fetch Facebook Ads metadata."""
        logger.info("Fetching Facebook Ads metadata")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                ENDPOINTS["facebook_metadata"],
                headers=get_headers(),
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved {len(data.get('fields', []))} Facebook Ads fields")
            return data
    
    @staticmethod
    async def get_analytics_metadata(
        property_id: str,
        credential_email: str
    ) -> Dict[str, Any]:
        """Fetch Google Analytics metadata."""
        logger.info(f"Fetching Google Analytics metadata for property: {property_id}")
        
        payload = {
            "property_id": property_id,
            "credential_email": credential_email
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ENDPOINTS["analytics4_metadata"],
                headers=get_headers(),
                json=payload,
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved {len(data.get('dimensions', []))} dimensions and {len(data.get('metrics', []))} metrics")
            return data