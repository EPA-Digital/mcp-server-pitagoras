"""
Herramientas para extraer datos de Pitágoras.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import json

from mcp.server.fastmcp import Context
from mcp.server.models import BaseModel
from api.pitagoras import PitagorasClient
from utils.data_manager import DataManager

# Configuración de logging
logger = logging.getLogger(__name__)

async def extract_google_ads_data(
    ctx: Context,
    metrics: List[str],
    resource: str,
    start_date: str,
    end_date: str,
    attributes: Optional[List[Dict]] = None,
    segments: Optional[List[str]] = None,
    df_name: Optional[str] = None
) -> List[BaseModel]:
    """
    Extrae datos de Google Ads.
    
    Args:
        metrics: Lista de métricas
        resource: Recurso a consultar
        start_date: Fecha de inicio (formato YYYY-MM-DD)
        end_date: Fecha de fin (formato YYYY-MM-DD)
        attributes: Lista de atributos a extraer
        segments: Lista de segmentos
        df_name: Nombre para el dataframe resultante
        ctx: Contexto de la petición
        
    Returns:
        Mensaje de confirmación
    """
    logger.info(f"Extrayendo datos de Google Ads para fechas: {start_date} a {end_date}")
    
    try:
        # Verificar si hay una selección de cuentas
        selected_accounts = getattr(ctx.request_context.lifespan_context, "selected_accounts", None)
        if not selected_accounts:
            error_msg = "No hay cuentas seleccionadas. Use primero mediums_and_accounts_selector."
            logger.error(error_msg)
            return [BaseModel(type="text", text=error_msg)]
        
        # Verificar que el medio seleccionado sea Google Ads
        selection = getattr(ctx.request_context.lifespan_context, "selection", {})
        if selection.get("medium") != "google_ads":
            error_msg = "El medio seleccionado no es Google Ads."
            logger.error(error_msg)
            return [BaseModel(type="text", text=error_msg)]
        
        # Preparar atributos si no se proporcionan
        if not attributes:
            attributes = [{"resource_name": resource, "fields": [f"{resource}.id", f"{resource}.name"]}]
        
        # Preparar segmentos si no se proporcionan
        if not segments:
            segments = ["segments.date"]
        
        # Crear cliente de Pitágoras
        pitagoras = PitagorasClient()
        
        # Extraer datos
        data = await pitagoras.extract_google_ads_data(
            accounts=selected_accounts,
            attributes=attributes,
            segments=segments,
            metrics=metrics,
            resource=resource,
            start_date=start_date,
            end_date=end_date
        )
        
        # Verificar si hay errores en la respuesta
        if "errors" in data and data["errors"]:
            error_list = "\n".join(data["errors"])
            ctx.warning(f"Se encontraron errores durante la extracción: {error_list}")
        
        # Convertir datos a DataFrame y almacenar
        data_manager = getattr(ctx.request_context.lifespan_context, "data_manager", DataManager())
        df_name_result = data_manager.convert_api_data_to_dataframe(data, df_name)
        
        # Guardar data_manager en el contexto si no existe
        if not hasattr(ctx.request_context.lifespan_context, "data_manager"):
            ctx.request_context.lifespan_context.data_manager = data_manager
        
        # Crear mensaje de respuesta
        rows_count = len(data.get("rows", []))
        columns = data.get("headers", [])
        
        response_text = (
            f"Datos extraídos correctamente:\n"
            f"Filas: {rows_count}\n"
            f"Columnas: {json.dumps(columns)}\n"
            f"DataFrame almacenado como: {df_name_result}\n\n"
            f"Puede analizar los datos usando la herramienta run_script."
        )
        
        return [BaseModel(type="text", text=response_text)]
    
    except Exception as e:
        logger.error(f"Error al extraer datos de Google Ads: {str(e)}")
        return [BaseModel(type="text", text=f"Error al extraer datos de Google Ads: {str(e)}")]

async def extract_facebook_ads_data(
    ctx: Context,
    fields: List[str],
    start_date: str,
    end_date: str,
    df_name: Optional[str] = None
) -> List[BaseModel]:
    """
    Extrae datos de Facebook Ads.
    
    Args:
        fields: Campos a extraer
        start_date: Fecha de inicio (formato YYYY-MM-DD)
        end_date: Fecha de fin (formato YYYY-MM-DD)
        df_name: Nombre para el dataframe resultante
        ctx: Contexto de la petición
        
    Returns:
        Mensaje de confirmación
    """
    logger.info(f"Extrayendo datos de Facebook Ads para fechas: {start_date} a {end_date}")
    
    try:
        # Verificar si hay una selección de cuentas
        selected_accounts = getattr(ctx.request_context.lifespan_context, "selected_accounts", None)
        if not selected_accounts:
            error_msg = "No hay cuentas seleccionadas. Use primero mediums_and_accounts_selector."
            logger.error(error_msg)
            return [BaseModel(type="text", text=error_msg)]
        
        # Verificar que el medio seleccionado sea Facebook Ads
        selection = getattr(ctx.request_context.lifespan_context, "selection", {})
        if selection.get("medium") != "facebook_ads":
            error_msg = "El medio seleccionado no es Facebook Ads."
            logger.error(error_msg)
            return [BaseModel(type="text", text=error_msg)]
        
        # Crear cliente de Pitágoras
        pitagoras = PitagorasClient()
        
        # Extraer datos
        data = await pitagoras.extract_facebook_ads_data(
            accounts=selected_accounts,
            fields=fields,
            start_date=start_date,
            end_date=end_date
        )
        
        # Verificar si hay errores en la respuesta
        if "errors" in data and data["errors"]:
            error_list = "\n".join(data["errors"])
            ctx.warning(f"Se encontraron errores durante la extracción: {error_list}")
        
        # Convertir datos a DataFrame y almacenar
        data_manager = getattr(ctx.request_context.lifespan_context, "data_manager", DataManager())
        df_name_result = data_manager.convert_api_data_to_dataframe(data, df_name)
        
        # Guardar data_manager en el contexto si no existe
        if not hasattr(ctx.request_context.lifespan_context, "data_manager"):
            ctx.request_context.lifespan_context.data_manager = data_manager
        
        # Crear mensaje de respuesta
        rows_count = len(data.get("rows", []))
        columns = data.get("headers", [])
        
        response_text = (
            f"Datos extraídos correctamente:\n"
            f"Filas: {rows_count}\n"
            f"Columnas: {json.dumps(columns)}\n"
            f"DataFrame almacenado como: {df_name_result}\n\n"
            f"Puede analizar los datos usando la herramienta run_script."
        )
        
        return [BaseModel(type="text", text=response_text)]
    
    except Exception as e:
        logger.error(f"Error al extraer datos de Facebook Ads: {str(e)}")
        return [BaseModel(type="text", text=f"Error al extraer datos de Facebook Ads: {str(e)}")]

async def extract_google_analytics_data(
    ctx: Context,
    dimensions: List[str],
    metrics: List[str],
    start_date: str,
    end_date: str,
    filters: Optional[Dict] = None,
    df_name: Optional[str] = None
) -> List[BaseModel]:
    """
    Extrae datos de Google Analytics.
    
    Args:
        dimensions: Dimensiones a extraer
        metrics: Métricas a extraer
        start_date: Fecha de inicio (formato YYYY-MM-DD)
        end_date: Fecha de fin (formato YYYY-MM-DD)
        filters: Filtros opcionales
        df_name: Nombre para el dataframe resultante
        ctx: Contexto de la petición
        
    Returns:
        Mensaje de confirmación
    """
    logger.info(f"Extrayendo datos de Google Analytics para fechas: {start_date} a {end_date}")
    
    try:
        # Verificar si hay una selección de cuentas
        selected_accounts = getattr(ctx.request_context.lifespan_context, "selected_accounts", None)
        if not selected_accounts:
            error_msg = "No hay cuentas seleccionadas. Use primero mediums_and_accounts_selector."
            logger.error(error_msg)
            return [BaseModel(type="text", text=error_msg)]
        
        # Verificar que el medio seleccionado sea Google Analytics
        selection = getattr(ctx.request_context.lifespan_context, "selection", {})
        if selection.get("medium") != "google_analytics":
            error_msg = "El medio seleccionado no es Google Analytics."
            logger.error(error_msg)
            return [BaseModel(type="text", text=error_msg)]
        
        # Crear cliente de Pitágoras
        pitagoras = PitagorasClient()
        
        # Extraer datos
        data = await pitagoras.extract_google_analytics_data(
            accounts=selected_accounts,
            dimensions=dimensions,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date,
            filters=filters
        )
        
        # Verificar si hay errores en la respuesta
        if "errors" in data and data["errors"]:
            error_list = "\n".join(data["errors"])
            ctx.warning(f"Se encontraron errores durante la extracción: {error_list}")
        
        # Convertir datos a DataFrame y almacenar
        data_manager = getattr(ctx.request_context.lifespan_context, "data_manager", DataManager())
        df_name_result = data_manager.convert_api_data_to_dataframe(data, df_name)
        
        # Guardar data_manager en el contexto si no existe
        if not hasattr(ctx.request_context.lifespan_context, "data_manager"):
            ctx.request_context.lifespan_context.data_manager = data_manager
        
        # Crear mensaje de respuesta
        rows_count = len(data.get("rows", []))
        columns = data.get("headers", [])
        
        response_text = (
            f"Datos extraídos correctamente:\n"
            f"Filas: {rows_count}\n"
            f"Columnas: {json.dumps(columns)}\n"
            f"DataFrame almacenado como: {df_name_result}\n\n"
            f"Puede analizar los datos usando la herramienta run_script."
        )
        
        return [BaseModel(type="text", text=response_text)]
    
    except Exception as e:
        logger.error(f"Error al extraer datos de Google Analytics: {str(e)}")
        return [BaseModel(type="text", text=f"Error al extraer datos de Google Analytics: {str(e)}")]

async def get_google_ads_metadata(
    resource_name: str,
    ctx: Context
) -> List[BaseModel]:
    """
    Obtiene metadatos de Google Ads.
    
    Args:
        resource_name: Nombre del recurso
        ctx: Contexto de la petición
        
    Returns:
        Metadatos disponibles
    """
    logger.info(f"Obteniendo metadatos de Google Ads para recurso: {resource_name}")
    
    try:
        # Crear cliente de Pitágoras
        pitagoras = PitagorasClient()
        
        # Obtener metadatos
        metrics = await pitagoras.get_google_ads_metadata(resource_name)
        
        # Respuesta
        response_text = (
            f"Métricas disponibles para {resource_name}:\n"
            f"{json.dumps(metrics, indent=2)}"
        )
        
        return [BaseModel(type="text", text=response_text)]
    
    except Exception as e:
        logger.error(f"Error al obtener metadatos de Google Ads: {str(e)}")
        return [BaseModel(type="text", text=f"Error al obtener metadatos de Google Ads: {str(e)}")]

async def get_facebook_ads_metadata(ctx: Context) -> List[BaseModel]:
    """
    Obtiene metadatos de Facebook Ads.
    
    Args:
        ctx: Contexto de la petición
        
    Returns:
        Metadatos disponibles
    """
    logger.info("Obteniendo metadatos de Facebook Ads")
    
    try:
        # Crear cliente de Pitágoras
        pitagoras = PitagorasClient()
        
        # Obtener metadatos
        metadata = await pitagoras.get_facebook_ads_metadata()
        
        # Respuesta
        response_text = (
            f"Campos disponibles para Facebook Ads:\n"
            f"{json.dumps(metadata.get('fields', []), indent=2)}"
        )
        
        return [BaseModel(type="text", text=response_text)]
    
    except Exception as e:
        logger.error(f"Error al obtener metadatos de Facebook Ads: {str(e)}")
        return [BaseModel(type="text", text=f"Error al obtener metadatos de Facebook Ads: {str(e)}")]

async def get_google_analytics_metadata(
    property_id: str,
    credential_email: str,
    ctx: Context
) -> List[BaseModel]:
    """
    Obtiene metadatos de Google Analytics.
    
    Args:
        property_id: ID de la propiedad
        credential_email: Email con credenciales
        ctx: Contexto de la petición
        
    Returns:
        Metadatos disponibles
    """
    logger.info(f"Obteniendo metadatos de Google Analytics para propiedad: {property_id}")
    
    try:
        # Crear cliente de Pitágoras
        pitagoras = PitagorasClient()
        
        # Obtener metadatos
        metadata = await pitagoras.get_google_analytics_metadata(property_id, credential_email)
        
        # Respuesta
        response_text = (
            f"Metadatos de Google Analytics para propiedad {property_id}:\n"
            f"Dimensiones:\n{json.dumps(metadata.get('dimensions', []), indent=2)}\n\n"
            f"Métricas:\n{json.dumps(metadata.get('metrics', []), indent=2)}"
        )
        
        return [BaseModel(type="text", text=response_text)]
    
    except Exception as e:
        logger.error(f"Error al obtener metadatos de Google Analytics: {str(e)}")
        return [BaseModel(type="text", text=f"Error al obtener metadatos de Google Analytics: {str(e)}")]