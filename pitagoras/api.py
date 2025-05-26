# pitagoras/api.py
import httpx
import logging
from datetime import datetime
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

async def search_customers(query: str, user_email: str = DEFAULT_USER_EMAIL) -> List[Dict[str, Any]]:
    """Return customers whose name or ID contains ``query``."""
    customers = await get_customers(user_email)
    query_lower = query.lower()
    filtered = [
        c
        for c in customers
        if query_lower in str(c.get("ID", "")).lower()
        or query_lower in c.get("name", "").lower()
    ]
    logger.info(
        f"Filtered customers by '{query}', found {len(filtered)} matches"
    )
    return filtered

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
    accounts: List[Dict[str, str]],
    fields: List[str],
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """Get Facebook Ads report data"""
    # El formato correcto del payload según el ejemplo actualizado
    payload = {
        "accounts": accounts,
        "fields": fields,
        "start_date": start_date,
        "end_date": end_date
    }
    
    logger.info(f"Requesting Facebook Ads data with payload: {payload}")
    
    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN
            logger.info(f"Using Authorization header: {AUTH_TOKEN[:5]}...")  # Log primeros 5 caracteres para debug
        else:
            logger.warning("No Authorization token found")
        
        try:
            logger.info(f"Sending request to: {ENDPOINTS['facebook_ads']}")
            response = await client.post(
                ENDPOINTS["facebook_ads"],
                json=payload,
                headers=headers,
                timeout=30.0  # Aumentar timeout
            )
            
            # Log de la respuesta para debug
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {response.headers}")
            
            # Intentar obtener el cuerpo de la respuesta incluso si el status code no es exitoso
            try:
                response_body = response.json()
                logger.info(f"Response body: {response_body}")
            except Exception as json_err:
                logger.warning(f"Couldn't parse response as JSON: {str(json_err)}")
                logger.info(f"Raw response: {response.text[:500]}...")  # Primeros 500 caracteres
            
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Received Facebook Ads data with {len(data.get('rows', []))} rows")
            return data
            
        except httpx.HTTPStatusError as e:
            # Capturar y registrar detalles del error
            error_body = None
            try:
                error_body = e.response.json()
            except:
                error_body = e.response.text if e.response.text else "No response body"
            
            logger.error(f"HTTP error {e.response.status_code} from Facebook API: {error_body}")
            
            # Re-lanzar la excepción con más información
            raise Exception(f"Error HTTP {e.response.status_code} de la API de Facebook: {error_body}") from e
            
        except httpx.RequestError as e:
            # Errores de red, timeout, etc.
            logger.error(f"Request error with Facebook API: {str(e)}")
            raise Exception(f"Error de conexión con la API de Facebook: {str(e)}") from e
            
        except Exception as e:
            # Capturar cualquier otro error
            logger.error(f"Unexpected error with Facebook API: {str(e)}", exc_info=True)
            raise Exception(f"Error inesperado con la API de Facebook: {str(e)}") from e

async def get_google_analytics_report(
    accounts: List[Dict[str, str]],
    dimensions: List[str],
    metrics: List[str],
    start_date: str,
    end_date: str,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get Google Analytics report data"""
    # Nos aseguramos que cada cuenta tenga los campos requeridos
    formatted_accounts = []
    for account in accounts:
        required_fields = ["account_id", "property_id", "name", "credential_email"]
        if all(field in account for field in required_fields):
            formatted_accounts.append(account)
        else:
            logger.warning(f"Cuenta de Google Analytics con formato incorrecto, se omitirá: {account}")
    
    if not formatted_accounts:
        raise ValueError("No se proporcionaron cuentas de Google Analytics con el formato correcto. Cada cuenta debe tener 'account_id', 'property_id', 'name' y 'credential_email'.")
    
    payload = {
        "accounts": formatted_accounts,
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
            logger.info(f"Using Authorization header: {AUTH_TOKEN[:5]}...")  # Log primeros 5 caracteres para debug
        else:
            logger.warning("No Authorization token found")
        
        try:
            logger.info(f"Sending request to: {ENDPOINTS['google_analytics']}")
            response = await client.post(
                ENDPOINTS["google_analytics"],
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            # Log de la respuesta para debug
            logger.info(f"Response status code: {response.status_code}")
            
            # Intentar obtener el cuerpo de la respuesta incluso si el status code no es exitoso
            try:
                response_body = response.json()
                logger.info(f"Response body preview: {str(response_body)[:500]}...")
            except Exception as json_err:
                logger.warning(f"Couldn't parse response as JSON: {str(json_err)}")
                logger.info(f"Raw response: {response.text[:500]}...")
            
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Received Google Analytics data with {len(data.get('rows', []))} rows")
            return data
            
        except httpx.HTTPStatusError as e:
            error_body = None
            try:
                error_body = e.response.json()
            except:
                error_body = e.response.text if e.response.text else "No response body"
            
            logger.error(f"HTTP error {e.response.status_code} from Google Analytics API: {error_body}")
            raise Exception(f"Error HTTP {e.response.status_code} de la API de Google Analytics: {error_body}") from e
            
        except Exception as e:
            logger.error(f"Unexpected error with Google Analytics API: {str(e)}", exc_info=True)
            raise Exception(f"Error con la API de Google Analytics: {str(e)}") from e


async def get_analytics4_metadata(
    property_id: str = "0", credential_email: str = "analytics@epa.digital"
) -> Dict[str, Any]:
    """Get available GA4 dimensions and metrics"""
    payload = {"property_id": property_id, "credential_email": credential_email}

    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN

        response = await client.post(
            ENDPOINTS["analytics4_metadata"], json=payload, headers=headers
        )
        response.raise_for_status()
        return response.json()


async def get_facebook_schema() -> Dict[str, Any]:
    """Get Facebook Ads available fields"""
    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN

        response = await client.get(ENDPOINTS["facebook_schema"], headers=headers)
        response.raise_for_status()
        return response.json()


async def get_adwords_resources() -> List[str]:
    """List available Google Ads resources"""
    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN

        response = await client.get(ENDPOINTS["adwords_resources"], headers=headers)
        response.raise_for_status()
        return response.json()


async def get_adwords_attributes(resource_name: str) -> List[str]:
    """Get Google Ads attributes for a resource"""
    params = {"resource_name": resource_name}
    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN

        response = await client.get(
            ENDPOINTS["adwords_attributes"], params=params, headers=headers
        )
        response.raise_for_status()
        return response.json()


async def get_adwords_segments(resource_name: str) -> List[str]:
    """Get Google Ads segments for a resource"""
    params = {"resource_name": resource_name}
    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN

        response = await client.get(
            ENDPOINTS["adwords_segments"], params=params, headers=headers
        )
        response.raise_for_status()
        return response.json()


async def get_adwords_metrics(resource_name: str) -> List[str]:
    """Get Google Ads metrics for a resource"""
    params = {"resource_name": resource_name}
    async with httpx.AsyncClient() as client:
        headers = {}
        if AUTH_TOKEN:
            headers["Authorization"] = AUTH_TOKEN

        response = await client.get(
            ENDPOINTS["adwords_metrics"], params=params, headers=headers
        )
        response.raise_for_status()
        return response.json()
