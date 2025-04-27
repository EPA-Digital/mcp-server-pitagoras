#!/usr/bin/env python3
# Servidor MCP para Pitagoras API
import httpx
import os
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context}
from dotenv import load_dotenv

# Configuración
PITAGORAS_API_BASE_URL = "https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1"
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

# Crear servidor MCP
mcp = FastMCP("Pitagoras API", dependencies=["httpx"])

# -------------------- Helpers --------------------

async def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
    """Realiza una petición a la API de Pitagoras"""
    url = f"{PITAGORAS_API_BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        if method.upper() == "GET":
            response = await client.get(url, headers=headers)
        elif method.upper() == "POST":
            response = await client.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")
        
        response.raise_for_status()
        return response.json()

async def get_customers(email: str) -> Dict:
    """Obtiene la lista de clientes para un email específico"""
    try:
        data = {"user_email": email}
        return await make_api_request("customers", method="POST", data=data)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return {"error": "No se encontró el email en la solicitud"}
        elif e.response.status_code == 401:
            return {"error": "El usuario no tiene acceso a la herramienta Pitagoras"}
        elif e.response.status_code == 404:
            return {"error": "Email no encontrado en la base de datos"}
        else:
            return {"error": f"Error al comunicarse con la API de Pitagoras: {str(e)}"}

# -------------------- Resources --------------------

@mcp.resource("pitagoras://customers/{email}")
async def get_customers_resource(email: str) -> str:
    """
    Obtiene la lista de clientes para un email específico.
    
    Args:
        email: El correo electrónico del usuario para el que se consultarán los clientes.
    """
    result = await get_customers(email)
    
    if "error" in result:
        return f"Error al obtener clientes: {result['error']}"
    
    # Formatear los datos de los clientes en un texto legible
    customers_info = []
    for customer in result.get("customers", []):
        customer_id = customer.get("ID", "ID desconocido")
        customer_name = customer.get("name", "Nombre desconocido")
        
        accounts_info = []
        for account in customer.get("accounts", []):
            account_id = account.get("accountID", "ID desconocido")
            account_name = account.get("name", "Nombre desconocido")
            provider = account.get("provider", "Proveedor desconocido")
            accounts_info.append(f"    - Cuenta: {account_name} (ID: {account_id}, Proveedor: {provider})")
        
        accounts_text = "\n".join(accounts_info) if accounts_info else "    - No hay cuentas disponibles"
        customers_info.append(f"Cliente: {customer_name} (ID: {customer_id})\n{accounts_text}")
    
    if not customers_info:
        return "No se encontraron clientes para este usuario."
    
    return "Clientes disponibles:\n\n" + "\n\n".join(customers_info)

# -------------------- Tools --------------------

@mcp.tool()
async def obtener_datos_cuenta_ads(email: str, cliente_id: str, provider: str) -> str:
    """
    Obtiene los datos necesarios de una cuenta para hacer llamadas a la API de ads.
    
    Args:
        email: El correo electrónico del usuario.
        cliente_id: El ID del cliente del que se quieren consultar las cuentas de ads.
        provider: El proveedor (adwords, facebook) para el que se quieren las cuentas.
    
    Returns:
        Un formato JSON con los datos necesarios para hacer llamadas a la API de ads.
    """
    result = await get_customers(email)
    
    if "error" in result:
        return f"Error al obtener datos del cliente: {result['error']}"
    
    # Buscar el cliente específico
    cliente = None
    for c in result.get("customers", []):
        if c.get("ID") == cliente_id:
            cliente = c
            break
    
    if not cliente:
        return f"No se encontró el cliente con ID: {cliente_id}"
    
    # Filtrar las cuentas por proveedor
    cuentas_filtradas = []
    for account in cliente.get("accounts", []):
        if account.get("provider", "").lower() == provider.lower():
            if provider.lower() == "adwords":
                cuentas_filtradas.append({
                    "name": account.get("name", "Nombre desconocido"),
                    "account_id": str(account.get("accountID", "")),
                    "login_customer_id": str(account.get("externalLoginCustomerID", ""))
                })
            elif provider.lower() == "facebook":
                cuentas_filtradas.append({
                    "name": account.get("name", "Nombre desconocido"),
                    "account_id": str(account.get("accountID", ""))
                })
    
    if not cuentas_filtradas:
        return f"No se encontraron cuentas de {provider} para este cliente."
    
    # Formatear el resultado en JSON
    import json
    return json.dumps(cuentas_filtradas, ensure_ascii=False, indent=2)

@mcp.tool()
async def obtener_clientes(email: str) -> str:
    """
    Obtiene la lista de clientes para un email específico.
    
    Args:
        email: El correo electrónico del usuario para el que se consultarán los clientes.
    
    Returns:
        Un resumen de los clientes disponibles para el usuario.
    """
    result = await get_customers(email)
    
    if "error" in result:
        return f"Error al obtener clientes: {result['error']}"
    
    # Formatear los datos de los clientes en un texto legible
    customers_info = []
    for customer in result.get("customers", []):
        customer_id = customer.get("ID", "ID desconocido")
        customer_name = customer.get("name", "Nombre desconocido")
        account_count = len(customer.get("accounts", []))
        
        customers_info.append(f"- {customer_name} (ID: {customer_id}): {account_count} cuentas")
    
    if not customers_info:
        return "No se encontraron clientes para este usuario."
    
    return f"Se encontraron {len(customers_info)} clientes para {email}:\n\n" + "\n".join(customers_info)

@mcp.tool()
async def obtener_detalles_cliente(email: str, cliente_id: str) -> str:
    """
    Obtiene los detalles completos de un cliente específico.
    
    Args:
        email: El correo electrónico del usuario.
        cliente_id: El ID del cliente para el que se consultarán los detalles.
    
    Returns:
        Información detallada sobre el cliente y sus cuentas.
    """
    result = await get_customers(email)
    
    if "error" in result:
        return f"Error al obtener datos del cliente: {result['error']}"
    
    # Buscar el cliente específico
    cliente = None
    for c in result.get("customers", []):
        if c.get("ID") == cliente_id:
            cliente = c
            break
    
    if not cliente:
        return f"No se encontró el cliente con ID: {cliente_id}"
    
    # Formatear los detalles del cliente
    customer_name = cliente.get("name", "Nombre desconocido")
    status = cliente.get("status", "Estado desconocido")
    
    accounts_info = []
    for account in cliente.get("accounts", []):
        account_id = account.get("accountID", "ID desconocido")
        account_name = account.get("name", "Nombre desconocido")
        provider = account.get("provider", "Proveedor desconocido")
        currency = account.get("currency", "Moneda desconocida")
        business_unit = account.get("businessUnit", "Unidad de negocio desconocida")
        vertical = account.get("vertical", "Vertical desconocido")
        objective = account.get("objective", "Objetivo desconocido")
        
        manager_info = "No disponible"
        if "manager" in account and account["manager"]:
            manager_name = account["manager"].get("name", "Nombre desconocido")
            manager_id = account["manager"].get("userID", "ID desconocido")
            manager_info = f"{manager_name} (ID: {manager_id})"
        
        accounts_info.append(
            f"- Cuenta: {account_name}\n"
            f"  ID: {account_id}\n"
            f"  Proveedor: {provider}\n"
            f"  Moneda: {currency}\n"
            f"  Unidad de negocio: {business_unit}\n"
            f"  Vertical: {vertical}\n"
            f"  Objetivo: {objective}\n"
            f"  Manager: {manager_info}"
        )
    
    accounts_text = "\n\n".join(accounts_info) if accounts_info else "No hay cuentas disponibles"
    
    return f"Detalles del cliente: {customer_name} (ID: {cliente_id})\nEstado: {status}\n\nCuentas:\n\n{accounts_text}"

# -------------------- Prompts --------------------

@mcp.prompt()
def obtener_cuenta_ads(email: str, cliente_id: str, provider: str) -> str:
    """
    Prompt para obtener detalles de cuentas de ads para un cliente específico.
    
    Args:
        email: El correo electrónico del usuario.
        cliente_id: El ID del cliente para el que se consultarán las cuentas.
        provider: El proveedor de ads (adwords, facebook).
    """
    return f"""Por favor, obtén las cuentas de {provider} para el cliente con ID '{cliente_id}' 
para el usuario con correo electrónico '{email}'.

Necesito estos datos en formato JSON para poder realizar llamadas a la API de {provider}.
Si hay múltiples cuentas, muéstralas todas."""

@mcp.prompt()
def consultar_clientes(email: str) -> str:
    """
    Prompt para consultar los clientes asociados a un correo electrónico.
    
    Args:
        email: El correo electrónico del usuario.
    """
    return f"""Por favor, consulta los clientes disponibles para el usuario con correo electrónico {email}.
Muestra un resumen de todos los clientes encontrados junto con su información básica."""

@mcp.prompt()
def consultar_cliente_especifico(email: str, cliente_id: str) -> str:
    """
    Prompt para consultar información detallada de un cliente específico.
    
    Args:
        email: El correo electrónico del usuario.
        cliente_id: El ID del cliente a consultar.
    """
    return f"""Por favor, consulta la información detallada del cliente con ID {cliente_id} 
para el usuario con correo electrónico {email}.

Muestra toda la información disponible de este cliente, incluyendo sus cuentas asociadas, 
unidades de negocio, proveedores y cualquier otro dato relevante."""

@mcp.prompt()
def generar_reporte_resumen(email: str) -> str:
    """
    Prompt para generar un reporte de resumen de todos los clientes de un usuario.
    
    Args:
        email: El correo electrónico del usuario.
    """
    return f"""Por favor, genera un reporte resumido de todos los clientes disponibles 
para el usuario con correo electrónico {email}.

El reporte debe incluir:
1. Número total de clientes
2. Distribución por tipo de proveedor
3. Listado de clientes con mayor número de cuentas
4. Cualquier otra información estadística relevante que puedas extraer

Organiza la información de manera clara y estructurada para facilitar su comprensión."""

# Ejecutar el servidor
if __name__ == "__main__":
    mcp.run()