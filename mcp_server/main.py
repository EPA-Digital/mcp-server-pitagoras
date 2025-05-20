#!/usr/bin/env python3
"""
Punto de entrada principal para el servidor MCP de Pitágoras.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from mcp.server.models import BaseModel

from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP, Context

from api.pitagoras import PitagorasClient
from utils.data_manager import DataManager
from tools.client_tools import extract_clients_data, mediums_and_accounts_selector
from tools.extraction_tools import (
    extract_google_ads_data,
    extract_facebook_ads_data,
    extract_google_analytics_data,
    get_google_ads_metadata,
    get_facebook_ads_metadata,
    get_google_analytics_metadata
)
from tools.analysis_tools import run_script, list_dataframes
from prompts.analysis_prompts import (
    exploratory_analysis_prompt,
    performance_comparison_prompt,
    optimization_recommendations_prompt
)

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verificar token de autenticación
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
if not AUTH_TOKEN:
    logger.warning("AUTH_TOKEN no está configurado en el archivo .env")

# Clase para el contexto de la aplicación
@dataclass
class AppContext:
    """Contexto de la aplicación para el servidor MCP."""
    data_manager: DataManager
    clients: List[Dict] = None
    selection: Dict = None
    selected_accounts: List[Dict] = None

# Gestor de ciclo de vida de la aplicación
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Gestiona el ciclo de vida de la aplicación.
    
    Args:
        server: Servidor FastMCP
        
    Yields:
        Contexto de la aplicación
    """
    logger.info("Iniciando servidor MCP de Pitágoras...")
    
    # Inicializar componentes
    data_manager = DataManager()
    
    try:
        # Proporcionar contexto a las herramientas
        yield AppContext(data_manager=data_manager)
    finally:
        # Limpieza al cerrar
        logger.info("Cerrando servidor MCP de Pitágoras...")

# Crear servidor FastMCP
mcp = FastMCP(
    "Pitágoras Analytics",
    lifespan=app_lifespan,
    dependencies=[
        "pandas",
        "numpy",
        "scipy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "statsmodels",
        "plotly",
        "httpx",
        "python-dotenv"
    ]
)

# Registrar recurso para los logs del análisis
@mcp.resource("analytics://logs")
def get_logs() -> str:
    """
    Obtiene los logs del análisis.
        
    Returns:
        Logs del análisis
    """
    logger.info("Obteniendo logs del análisis")
    
    data_manager = ctx.request_context.lifespan_context.data_manager
    return data_manager.get_logs()

# Registrar herramientas de cliente
@mcp.tool()
async def extract_clients_data(user_email: str, ctx: Context) -> str:
    """
    Extrae la lista de clientes disponibles para un usuario.
    
    Args:
        user_email: Email del usuario
        
    Returns:
        Lista de clientes en formato JSON
    """
    result = await extract_clients_data(user_email, ctx)
    return result[0].text if result and hasattr(result[0], 'text') else ""

@mcp.tool()
async def mediums_and_accounts_selector(client_id: str, medium: str, account_ids: List[str], ctx: Context) -> str:
    """
    Selecciona el medio y las cuentas para extraer datos.
    
    Args:
        client_id: ID del cliente
        medium: Medio para extraer datos (google_ads, facebook_ads, google_analytics)
        account_ids: Lista de IDs de cuentas
        
    Returns:
        Confirmación de selección
    """
    result = await mediums_and_accounts_selector(client_id, medium, account_ids, ctx)
    return result[0].text if result and hasattr(result[0], 'text') else ""

# Registrar herramientas de extracción
@mcp.tool()
async def extract_from_pitagoras(
    ctx: Context,
    platform: str,
    client_id: str,
    accounts: List[str],
    start_date: str,
    end_date: str,
    metrics: Optional[List[str]] = None,
    dimensions: Optional[List[str]] = None,
    segments: Optional[List[str]] = None,
    fields: Optional[List[str]] = None,
    resource: Optional[str] = "campaign",
    filters: Optional[Dict] = None,
    df_name: Optional[str] = None
) -> str:
    """
    Extrae datos de la API de Pitágoras.
    
    Args:
        platform: Plataforma (google_ads, facebook_ads, google_analytics)
        client_id: ID del cliente
        accounts: Lista de IDs de cuentas
        start_date: Fecha de inicio (formato YYYY-MM-DD)
        end_date: Fecha de fin (formato YYYY-MM-DD)
        metrics: Lista de métricas (requerido para Google Ads y Google Analytics)
        dimensions: Lista de dimensiones (requerido para Google Analytics)
        segments: Lista de segmentos (opcional para Google Ads)
        fields: Lista de campos (requerido para Facebook Ads)
        resource: Recurso para Google Ads (por defecto: campaign)
        filters: Filtros para Google Analytics
        df_name: Nombre para guardar el DataFrame en memoria
        
    Returns:
        Mensaje de confirmación con estadísticas del DataFrame resultante
    """
    logger.info(f"Extrayendo datos de {platform} para fechas: {start_date} a {end_date}")
    
    # Preparar herramienta según la plataforma
    if platform == "google_ads":
        if not metrics:
            return "Error: Se requieren métricas para extraer datos de Google Ads"
        
        # Usar seleccionador primero
        await mediums_and_accounts_selector(client_id, platform, accounts, ctx)
        
        # Extraer datos
        result = await extract_google_ads_data(
            metrics=metrics,
            resource=resource or "campaign",
            start_date=start_date,
            end_date=end_date,
            attributes=[{"resource_name": resource or "campaign", "fields": [f"{resource or 'campaign'}.id", f"{resource or 'campaign'}.name"]}] if not attributes else attributes,
            segments=segments or ["segments.date"],
            df_name=df_name,
            ctx=ctx
        )
    elif platform == "facebook_ads":
        if not fields:
            return "Error: Se requieren campos para extraer datos de Facebook Ads"
        
        # Usar seleccionador primero
        await mediums_and_accounts_selector(client_id, platform, accounts, ctx)
        
        # Extraer datos
        result = await extract_facebook_ads_data(
            fields=fields,
            start_date=start_date,
            end_date=end_date,
            df_name=df_name,
            ctx=ctx
        )
    elif platform == "google_analytics":
        if not metrics or not dimensions:
            return "Error: Se requieren métricas y dimensiones para extraer datos de Google Analytics"
        
        # Usar seleccionador primero
        await mediums_and_accounts_selector(client_id, platform, accounts, ctx)
        
        # Extraer datos
        result = await extract_google_analytics_data(
            dimensions=dimensions,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date,
            filters=filters,
            df_name=df_name,
            ctx=ctx
        )
    else:
        return f"Error: Plataforma no soportada: {platform}"
    
    return result[0].text if result and hasattr(result[0], 'text') else ""

@mcp.tool()
async def get_google_ads_metadata(resource_name: str, ctx: Context) -> str:
    """
    Obtiene metadatos de Google Ads.
    
    Args:
        resource_name: Nombre del recurso
        
    Returns:
        Metadatos disponibles
    """
    result = await get_google_ads_metadata(resource_name, ctx)
    return result[0].text if result and hasattr(result[0], 'text') else ""

@mcp.tool()
async def get_facebook_ads_metadata(ctx: Context) -> str:
    """
    Obtiene metadatos de Facebook Ads.
    
    Returns:
        Metadatos disponibles
    """
    result = await get_facebook_ads_metadata(ctx)
    return result[0].text if result and hasattr(result[0], 'text') else ""

@mcp.tool()
async def get_google_analytics_metadata(property_id: str, credential_email: str, ctx: Context) -> str:
    """
    Obtiene metadatos de Google Analytics.
    
    Args:
        property_id: ID de la propiedad
        credential_email: Email con credenciales
        
    Returns:
        Metadatos disponibles
    """
    result = await get_google_analytics_metadata(property_id, credential_email, ctx)
    return result[0].text if result and hasattr(result[0], 'text') else ""

# Registrar herramientas de análisis
@mcp.tool()
async def run_script(script: str, ctx: Context, save_to_memory: Optional[List[str]] = None) -> str:
    """
    Ejecuta un script de Python para análisis de datos.
    
    Args:
        script: Código Python a ejecutar
        save_to_memory: Lista de nombres de DataFrames a guardar en memoria
        
    Returns:
        Resultado de la ejecución del script
    """
    result = await run_script(script, save_to_memory, ctx)
    return result[0].text if result and hasattr(result[0], 'text') else ""

@mcp.tool()
async def list_dataframes(ctx: Context) -> str:
    """
    Lista los DataFrames disponibles en memoria.
    
    Returns:
        Lista de DataFrames disponibles
    """
    result = await list_dataframes(ctx)
    return result[0].text if result and hasattr(result[0], 'text') else ""

# Registrar prompts
@mcp.prompt()
async def analisis_exploratorio(
    contexto: str,
    plataforma: str,
    fecha_inicio: str,
    fecha_fin: str,
    metricas: str,
    ctx: Context
) -> List[BaseModel]:
    """
    Prompt para análisis exploratorio de datos.
    
    Args:
        contexto: Contexto del análisis
        plataforma: Plataforma analizada
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
        metricas: Métricas principales
        
    Returns:
        Plantilla de prompt para análisis exploratorio
    """
    return await exploratory_analysis_prompt(
        context=contexto,
        platform=plataforma,
        start_date=fecha_inicio,
        end_date=fecha_fin,
        metrics=metricas,
        ctx=ctx
    )

@mcp.prompt()
async def comparacion_rendimiento(
    plataformas: str,
    fecha_inicio: str,
    fecha_fin: str,
    metricas: str,
    ctx: Context
) -> List[BaseModel]:
    """
    Prompt para comparación de rendimiento entre plataformas.
    
    Args:
        plataformas: Plataformas a comparar
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
        metricas: Métricas a comparar
        
    Returns:
        Plantilla de prompt para comparación de rendimiento
    """
    return await performance_comparison_prompt(
        platforms=plataformas,
        start_date=fecha_inicio,
        end_date=fecha_fin,
        metrics=metricas,
        ctx=ctx
    )

@mcp.prompt()
async def recomendaciones_optimizacion(
    contexto: str,
    plataforma: str,
    fecha_inicio: str,
    fecha_fin: str,
    metricas: str,
    ctx: Context
) -> List[BaseModel]:
    """
    Prompt para recomendaciones de optimización.
    
    Args:
        contexto: Contexto del análisis
        plataforma: Plataforma analizada
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
        metricas: Métricas actuales
        
    Returns:
        Plantilla de prompt para recomendaciones de optimización
    """
    return await optimization_recommendations_prompt(
        context=contexto,
        platform=plataforma,
        start_date=fecha_inicio,
        end_date=fecha_fin,
        metrics=metricas,
        ctx=ctx
    )

def main():
    """Función principal para ejecutar el servidor."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()