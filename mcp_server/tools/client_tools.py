"""
Herramientas para gestionar clientes y cuentas.
"""

import logging
from typing import Dict, List, Optional, Any
import json

from mcp.server.fastmcp import Context
from mcp.server.models import BaseModel
from api.pitagoras import PitagorasClient

# Configuración de logging
logger = logging.getLogger(__name__)

async def extract_clients_data(user_email: str, ctx: Context) -> List[BaseModel]:
    """
    Extrae la lista de clientes disponibles para un usuario.
    
    Args:
        user_email: Email del usuario
        ctx: Contexto de la petición
        
    Returns:
        Lista de clientes en formato JSON
    """
    logger.info(f"Extrayendo clientes para el usuario: {user_email}")
    
    try:
        # Crear cliente de Pitágoras
        pitagoras = PitagorasClient()
        
        # Obtener clientes
        clients = await pitagoras.get_clients(user_email)
        
        if not clients:
            logger.warning(f"No se encontraron clientes para el usuario: {user_email}")
            return [BaseModel(type="text", text="No se encontraron clientes para este usuario")]
        
        # Guardar clientes en el contexto para futuras referencias
        ctx.request_context.lifespan_context.clients = clients
        
        # Formatear respuesta para mostrar de forma amigable
        formatted_clients = []
        for client in clients:
            formatted_accounts = []
            for account in client.get("accounts", []):
                formatted_account = {
                    "accountID": account.get("accountID"),
                    "name": account.get("name"),
                    "provider": account.get("provider"),
                    "currency": account.get("currency"),
                    "objective": account.get("objective", "N/A"),
                    "vertical": account.get("vertical", "N/A")
                }
                
                # Añadir login_customer_id para Google Ads si existe
                if account.get("externalLoginCustomerID"):
                    formatted_account["login_customer_id"] = account.get("externalLoginCustomerID")
                
                # Añadir credential_email para Google Analytics si existe
                if account.get("credentialEmail"):
                    formatted_account["credential_email"] = account.get("credentialEmail")
                
                formatted_accounts.append(formatted_account)
            
            formatted_client = {
                "ID": client.get("ID"),
                "name": client.get("name"),
                "status": client.get("status", "Desconocido"),
                "accounts": formatted_accounts
            }
            formatted_clients.append(formatted_client)
        
        # Convertir a JSON bonito
        pretty_json = json.dumps(formatted_clients, indent=2, ensure_ascii=False)
        ctx.info(f"Se encontraron {len(clients)} clientes")
        
        return [BaseModel(type="text", text=pretty_json)]
    
    except Exception as e:
        logger.error(f"Error al extraer clientes: {str(e)}")
        return [BaseModel(type="text", text=f"Error al extraer clientes: {str(e)}")]

async def mediums_and_accounts_selector(
    client_id: str,
    medium: str,
    account_ids: List[str],
    ctx: Context
) -> List[BaseModel]:
    """
    Selecciona el medio y las cuentas para extraer datos.
    
    Args:
        client_id: ID del cliente
        medium: Medio para extraer datos (google_ads, facebook_ads, google_analytics)
        account_ids: Lista de IDs de cuentas
        ctx: Contexto de la petición
        
    Returns:
        Confirmación de selección
    """
    logger.info(f"Seleccionando medio: {medium} y cuentas: {account_ids} para cliente: {client_id}")
    
    try:
        # Validar medio
        valid_mediums = ["google_ads", "facebook_ads", "google_analytics"]
        if medium not in valid_mediums:
            error_msg = f"Medio no válido: {medium}. Medios válidos: {', '.join(valid_mediums)}"
            logger.error(error_msg)
            return [BaseModel(type="text", text=error_msg)]
        
        # Buscar cliente en el contexto
        clients = getattr(ctx.request_context.lifespan_context, "clients", [])
        if not clients:
            error_msg = "No hay clientes disponibles. Ejecute primero extract_clients_data."
            logger.error(error_msg)
            return [BaseModel(type="text", text=error_msg)]
        
        selected_client = None
        for client in clients:
            if client.get("ID") == client_id:
                selected_client = client
                break
        
        if not selected_client:
            error_msg = f"Cliente no encontrado con ID: {client_id}"
            logger.error(error_msg)
            return [BaseModel(type="text", text=error_msg)]
        
        # Filtrar cuentas por medio y ID
        valid_accounts = []
        for account in selected_client.get("accounts", []):
            # Mapear el medio al proveedor correspondiente
            provider_mapping = {
                "google_ads": "adwords",
                "facebook_ads": "facebook",
                "google_analytics": "analytics"
            }
            
            if account.get("provider") == provider_mapping.get(medium):
                if account.get("accountID") in account_ids:
                    formatted_account = {
                        "account_id": account.get("accountID"),
                        "name": account.get("name")
                    }
                    
                    # Añadir login_customer_id para Google Ads
                    if medium == "google_ads" and account.get("externalLoginCustomerID"):
                        formatted_account["login_customer_id"] = account.get("externalLoginCustomerID")
                    
                    # Añadir credential_email para Google Analytics
                    if medium == "google_analytics" and account.get("credentialEmail"):
                        formatted_account["credential_email"] = account.get("credentialEmail")
                        formatted_account["property_id"] = account.get("accountID")
                    
                    valid_accounts.append(formatted_account)
        
        if not valid_accounts:
            error_msg = f"No se encontraron cuentas válidas para el medio {medium} con los IDs proporcionados"
            logger.error(error_msg)
            return [BaseModel(type="text", text=error_msg)]
        
        # Guardar selección en el contexto
        selection = {
            "client": selected_client.get("name"),
            "client_id": client_id,
            "medium": medium,
            "accounts": valid_accounts
        }
        ctx.request_context.lifespan_context.selection = selection
        
        # Respuesta
        response_text = (
            f"Selección exitosa:\n"
            f"Cliente: {selected_client.get('name')}\n"
            f"Medio: {medium}\n"
            f"Cuentas: {json.dumps([acc.get('name') for acc in valid_accounts])}\n\n"
            f"Puede proceder a extraer datos usando las herramientas de extracción específicas."
        )
        
        # También guardar cuentas seleccionadas como formato esperado por la API
        ctx.request_context.lifespan_context.selected_accounts = valid_accounts
        
        return [BaseModel(type="text", text=response_text)]
    
    except Exception as e:
        logger.error(f"Error al seleccionar medio y cuentas: {str(e)}")
        return [BaseModel(type="text", text=f"Error al seleccionar medio y cuentas: {str(e)}")]