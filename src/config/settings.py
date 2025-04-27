"""
Configuración y carga de variables de entorno para el servidor MCP de Pitágoras.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

# API configuración
API_BASE_URL = os.getenv('API_BASE_URL', 'https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
DEFAULT_USER_EMAIL = os.getenv('DEFAULT_USER_EMAIL', 'jcorona@epa.digital')

# Endpoints
CUSTOMERS_ENDPOINT = f"{API_BASE_URL}/customers"
ADWORDS_REPORT_ENDPOINT = f"{API_BASE_URL}/adwords/report"
FACEBOOK_REPORT_ENDPOINT = f"{API_BASE_URL}/facebook/report"
ANALYTICS4_REPORT_ENDPOINT = f"{API_BASE_URL}/analytics4/report"

# Periodos de tiempo predefinidos
TIME_PERIODS = {
    'last_7_days': 7,
    'last_14_days': 14,
    'last_30_days': 30,
}

# Verificación de configuración
if not AUTH_TOKEN:
    import warnings
    warnings.warn(
        "AUTH_TOKEN no está configurado. Configúralo en el archivo .env o como variable de entorno."
    )