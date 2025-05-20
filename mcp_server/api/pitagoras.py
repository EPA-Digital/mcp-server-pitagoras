"""
Cliente API para Pitágoras.
Este módulo proporciona funciones para interactuar con la API de Pitágoras.
"""

import logging
import os
from typing import Dict, List, Optional, Any, Union
import json

import httpx
from dotenv import load_dotenv

load_dotenv()

# Configuración de logging
logger = logging.getLogger(__name__)

# Configuración de la API
API_URL = os.getenv("PITAGORAS_API_URL", "https://pitagoras-api-l6dmrzkz7a-uc.a.run.app")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

if not AUTH_TOKEN:
    logger.warning("AUTH_TOKEN no está configurado en el archivo .env")


class PitagorasClient:
    """Cliente para la API de Pitágoras."""

    def __init__(self, api_url: str = None, auth_token: str = None):
        """
        Inicializa el cliente de la API de Pitágoras.
        
        Args:
            api_url: URL base de la API de Pitágoras
            auth_token: Token de autenticación para la API
        """
        self.api_url = api_url or API_URL
        self.auth_token = auth_token or AUTH_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, method: str = "POST", data: Dict = None) -> Dict:
        """
        Realiza una petición a la API de Pitágoras.
        
        Args:
            endpoint: Endpoint de la API
            method: Método HTTP (GET, POST, etc.)
            data: Datos a enviar en la petición (solo para POST)
            
        Returns:
            Respuesta de la API como diccionario
            
        Raises:
            Exception: Si ocurre un error en la petición
        """
        url = f"{self.api_url}{endpoint}"
        logger.debug(f"Haciendo petición {method} a {url}")
        
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers, timeout=30.0)
                else:  # POST
                    logger.debug(f"Datos: {json.dumps(data, indent=2)}")
                    response = await client.post(url, headers=self.headers, json=data, timeout=30.0)
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Error en la petición HTTP: {e}")
            raise Exception(f"Error en la petición a Pitágoras: {e}")
        except httpx.RequestError as e:
            logger.error(f"Error en la petición: {e}")
            raise Exception(f"Error de conexión a Pitágoras: {e}")
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            raise Exception(f"Error inesperado: {e}")
    
    async def get_clients(self, user_email: str) -> List[Dict]:
        """
        Obtiene la lista de clientes disponibles para un usuario.
        
        Args:
            user_email: Email del usuario
            
        Returns:
            Lista de clientes disponibles
        """
        endpoint = "/api/v1/customers"
        data = {"user_email": user_email}
        
        response = await self._make_request(endpoint, "POST", data)
        return response.get("customers", [])
    
    async def extract_google_ads_data(
        self, 
        accounts: List[Dict],
        attributes: List[Dict],
        segments: List[str],
        metrics: List[str],
        resource: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Extrae datos de Google Ads.
        
        Args:
            accounts: Lista de cuentas
            attributes: Lista de atributos a extraer
            segments: Segmentos para la consulta
            metrics: Métricas a extraer
            resource: Recurso sobre el que consultar
            start_date: Fecha de inicio (formato YYYY-MM-DD)
            end_date: Fecha de fin (formato YYYY-MM-DD)
            
        Returns:
            Datos extraídos
        """
        endpoint = "/api/v1/adwords/report"
        data = {
            "accounts": accounts,
            "attributes": attributes,
            "segments": segments,
            "metrics": metrics,
            "resource": resource,
            "start_date": start_date,
            "end_date": end_date
        }
        
        return await self._make_request(endpoint, "POST", data)
    
    async def extract_facebook_ads_data(
        self, 
        accounts: List[Dict],
        fields: List[str],
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Extrae datos de Facebook Ads.
        
        Args:
            accounts: Lista de cuentas
            fields: Campos a extraer
            start_date: Fecha de inicio (formato YYYY-MM-DD)
            end_date: Fecha de fin (formato YYYY-MM-DD)
            
        Returns:
            Datos extraídos
        """
        endpoint = "/api/v1/facebook/report"
        data = {
            "accounts": accounts,
            "fields": fields,
            "start_date": start_date,
            "end_date": end_date
        }
        
        return await self._make_request(endpoint, "POST", data)
    
    async def extract_google_analytics_data(
        self, 
        accounts: List[Dict],
        dimensions: List[str],
        metrics: List[str],
        start_date: str,
        end_date: str,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Extrae datos de Google Analytics 4.
        
        Args:
            accounts: Lista de cuentas
            dimensions: Dimensiones a extraer
            metrics: Métricas a extraer
            start_date: Fecha de inicio (formato YYYY-MM-DD)
            end_date: Fecha de fin (formato YYYY-MM-DD)
            filters: Filtros opcionales para la consulta
            
        Returns:
            Datos extraídos
        """
        endpoint = "/api/v1/analytics4/report"
        data = {
            "accounts": accounts,
            "dimensions": dimensions,
            "metrics": metrics,
            "start_date": start_date,
            "end_date": end_date
        }
        
        if filters:
            data["filters"] = filters
        
        return await self._make_request(endpoint, "POST", data)
    
    async def get_google_analytics_metadata(
        self,
        property_id: str,
        credential_email: str
    ) -> Dict:
        """
        Obtiene metadatos de Google Analytics 4.
        
        Args:
            property_id: ID de la propiedad
            credential_email: Email con credenciales
            
        Returns:
            Metadatos de Google Analytics
        """
        endpoint = "/api/v1/analytics4/metadata"
        data = {
            "property_id": property_id,
            "credential_email": credential_email
        }
        
        return await self._make_request(endpoint, "POST", data)
    
    async def get_facebook_ads_metadata(self) -> Dict:
        """
        Obtiene metadatos de Facebook Ads.
        
        Returns:
            Metadatos de Facebook Ads
        """
        endpoint = "/api/v1/facebook/schema"
        return await self._make_request(endpoint, "GET")
    
    async def get_google_ads_metadata(self, resource_name: str) -> List[str]:
        """
        Obtiene metadatos de Google Ads.
        
        Args:
            resource_name: Nombre del recurso
            
        Returns:
            Metadatos de Google Ads
        """
        endpoint = f"/api/v1/adwords/metrics?resource_name={resource_name}"
        return await self._make_request(endpoint, "GET")