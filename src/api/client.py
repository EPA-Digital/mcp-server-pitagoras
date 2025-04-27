"""
Cliente HTTP para realizar llamadas a la API de Pitágoras.
"""

import json
import logging
from typing import Any, Dict, Optional, Type, TypeVar

import httpx
from pydantic import BaseModel

from config import AUTH_TOKEN

# Configuración de logging
logger = logging.getLogger(__name__)

# Tipo genérico para los modelos de respuesta
T = TypeVar('T', bound=BaseModel)


class PitagorasClient:
    """Cliente para interactuar con la API de Pitágoras."""
    
    def __init__(self, auth_token: Optional[str] = None):
        """
        Inicializa el cliente HTTP para la API de Pitágoras.
        
        Args:
            auth_token: Token de autenticación para la API de Pitágoras.
                        Si no se proporciona, se usa el valor de AUTH_TOKEN.
        """
        self.auth_token = auth_token or AUTH_TOKEN
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.auth_token}" if self.auth_token else ""
        }
    
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None
    ) -> Any:
        """
        Realiza una solicitud HTTP a la API de Pitágoras.
        
        Args:
            method: Método HTTP (GET, POST, etc.).
            url: URL del endpoint.
            data: Datos para enviar en la solicitud (para POST, PUT, etc.).
            response_model: Modelo de Pydantic para validar y parsear la respuesta.
            
        Returns:
            La respuesta de la API, opcionalmente convertida al modelo especificado.
            
        Raises:
            httpx.HTTPStatusError: Si la solicitud falla con un código de estado HTTP de error.
            Exception: Para otros errores que puedan ocurrir durante la solicitud.
        """
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers, params=data)
                else:  # POST, PUT, etc.
                    json_data = json.dumps(data) if data else None
                    response = await client.request(
                        method=method, 
                        url=url, 
                        headers=self.headers, 
                        content=json_data
                    )
                
                # Verificar si la respuesta fue exitosa
                response.raise_for_status()
                
                # Obtener datos JSON de la respuesta
                response_data = response.json()
                
                # Si se especificó un modelo de respuesta, validar y convertir los datos
                if response_model:
                    return response_model.model_validate(response_data)
                
                return response_data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP: {e.response.status_code} en {url}")
            logger.error(f"Respuesta: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error al hacer la solicitud a {url}: {str(e)}")
            raise
    
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, response_model: Optional[Type[T]] = None) -> Any:
        """Realiza una solicitud GET."""
        return await self._make_request("GET", url, params, response_model)
    
    async def post(self, url: str, data: Dict[str, Any], response_model: Optional[Type[T]] = None) -> Any:
        """Realiza una solicitud POST."""
        return await self._make_request("POST", url, data, response_model)