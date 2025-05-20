"""
Módulo de autenticación para el servidor MCP.
"""

import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logger = logging.getLogger(__name__)

# Token de autenticación desde variables de entorno
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

def get_auth_token() -> Optional[str]:
    """
    Obtiene el token de autenticación.
    
    Returns:
        Token de autenticación o None si no está configurado
    """
    if not AUTH_TOKEN:
        logger.warning("AUTH_TOKEN no está configurado en el archivo .env")
        return None
    return AUTH_TOKEN

def get_auth_headers() -> Dict[str, str]:
    """
    Obtiene los headers de autenticación para las peticiones a la API.
    
    Returns:
        Headers de autenticación
    """
    token = get_auth_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    } if token else {"Content-Type": "application/json"}

def validate_auth_token() -> bool:
    """
    Valida si el token de autenticación está configurado.
    
    Returns:
        True si el token está configurado, False en caso contrario
    """
    return AUTH_TOKEN is not None and len(AUTH_TOKEN) > 0