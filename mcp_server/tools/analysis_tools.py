"""
Herramientas para análisis de datos.
"""

import logging
from typing import Dict, List, Optional, Any
import json

from mcp.server.fastmcp import Context
from mcp.server.models import BaseModel
from utils.data_manager import DataManager

# Configuración de logging
logger = logging.getLogger(__name__)

async def run_script(
    ctx: Context,
    script: str,
    save_to_memory: Optional[List[str]] = None
) -> List[BaseModel]:
    """
    Ejecuta un script de Python para análisis de datos.
    
    Args:
        script: Script de Python a ejecutar
        save_to_memory: Lista de nombres de variables a guardar como dataframes
        ctx: Contexto de la petición
        
    Returns:
        Resultado de la ejecución del script
    """
    logger.info("Ejecutando script de análisis")
    
    try:
        # Obtener el gestor de datos del contexto o crear uno nuevo
        data_manager = getattr(ctx.request_context.lifespan_context, "data_manager", None)
        if not data_manager:
            data_manager = DataManager()
            ctx.request_context.lifespan_context.data_manager = data_manager
        
        # Ejecutar script
        result = data_manager.run_script(script, save_to_memory)
        
        # Formatear resultado
        if not result:
            result = "Script ejecutado correctamente sin salida."
        
        # Obtener información sobre los dataframes guardados
        saved_dfs_info = ""
        if save_to_memory:
            dfs = data_manager.list_dataframes()
            saved_dfs = [df for df in dfs if df[0] in save_to_memory]
            if saved_dfs:
                saved_dfs_info = "\n\nDataFrames guardados:\n"
                for name, shape in saved_dfs:
                    saved_dfs_info += f"- {name}: {shape[0]} filas x {shape[1]} columnas\n"
        
        # Construir respuesta
        response_text = f"Resultado de la ejecución:\n\n{result}{saved_dfs_info}"
        
        return [BaseModel(type="text", text=response_text)]
    
    except Exception as e:
        logger.error(f"Error al ejecutar script: {str(e)}")
        return [BaseModel(type="text", text=f"Error al ejecutar script: {str(e)}")]

async def list_dataframes(ctx: Context) -> List[BaseModel]:
    """
    Lista los dataframes disponibles en memoria.
    
    Args:
        ctx: Contexto de la petición
        
    Returns:
        Lista de dataframes
    """
    logger.info("Listando dataframes disponibles")
    
    try:
        # Obtener el gestor de datos del contexto o crear uno nuevo
        data_manager = getattr(ctx.request_context.lifespan_context, "data_manager", None)
        if not data_manager:
            return [BaseModel(type="text", text="No hay dataframes disponibles. Extraiga datos primero.")]
        
        # Listar dataframes
        dfs = data_manager.list_dataframes()
        
        if not dfs:
            return [BaseModel(type="text", text="No hay dataframes disponibles.")]
        
        # Construir respuesta
        response_text = "DataFrames disponibles:\n\n"
        for name, shape in dfs:
            response_text += f"- {name}: {shape[0]} filas x {shape[1]} columnas\n"
        
        return [BaseModel(type="text", text=response_text)]
    
    except Exception as e:
        logger.error(f"Error al listar dataframes: {str(e)}")
        return [BaseModel(type="text", text=f"Error al listar dataframes: {str(e)}")]