#!/usr/bin/env python3
# Servidor MCP para Pitagoras API
import httpx
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context

# Configuración
PITAGORAS_API_BASE_URL = "https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRob3JpemVkIjp0cnVlLCJjbGllbnRzV2l0aFBlcm1pc3Npb24iOlt7ImlkIjoiME16dmJXYVRyVzdnZWRCdmR3T0QifSx7ImlkIjoiMGZrd01PMFcweGpHSVRkQWxyVVQifSx7ImlkIjoiMld5b3paVThoampycThFNFVPT1gifSx7ImlkIjoiNE5QOGZZdVdSaHdrNTJwNEVDTWQifSx7ImlkIjoiNWhFc21wQmRvcnRCT3BMbjNhNFEifSx7ImlkIjoiNW9ZeDFWemNSU0hHb290QkV6Q3YifSx7ImlkIjoiNXVmamc1U09VNGZKbkxyT0pBcjcifSx7ImlkIjoiNlZMVDBJMzBDdU1pdmxyM0I3TEEifSx7ImlkIjoiNmYyN2FxQktmZlRLRkdLMVpHZXkifSx7ImlkIjoiNmZBZlVTeXRTd2dydXU3SHVXMEYifSx7ImlkIjoiNmZEMGE3UFJOUzgzc0d6NVVwOEcifSx7ImlkIjoiODJKWE4yQlJ1b0xoZ25LbHV0UUgifSx7ImlkIjoiQUZhVmJnM2ZsRVRlZjNjdWxudDQifSx7ImlkIjoiQUdqbEFMMXNVZ25hc0JNRjFEMjcifSx7ImlkIjoiQXVydktZclJvNE1JWkpaT3M1REIifSx7ImlkIjoiQjNMbTlMMGdMT05PN2dTMW50V3gifSx7ImlkIjoiQlM4Q05uUXhxTzlEb3JWN2dWMVoifSx7ImlkIjoiQ0l3UmlwSEZFYkxNSXVEYWhDRXIifSx7ImlkIjoiQ043Y1VBTW1haURuNmFIR2hib3gifSx7ImlkIjoiQ3I0T1ZOREJWdlVBc1JId2ZmWmkifSx7ImlkIjoiRDIwZ1F1dDl4SkdMSHNnSXh5NDIifSx7ImlkIjoiRGV5b1luakpBdjNCV1g5UENYZlkifSx7ImlkIjoiRHVvS3JJTGdSbWVya1VoR2c1eGoifSx7ImlkIjoiR3gzVjlVOU1OWGhFV0hidnlaZXMifSx7ImlkIjoiSFVYaGpDZGo5RUxoejlkUklhaVQifSx7ImlkIjoiSVRQRTBBSFFFbzMwcmg1VUd1d00ifSx7ImlkIjoiS3k2Z0hBTFFxdGs0RXpiZmxBRlkifSx7ImlkIjoiTEpuM3VWQ2V5WUVYOFdPMGZrbTAifSx7ImlkIjoiTTV6UG9Sc2VtS1Y0VzRUOWdieVkifSx7ImlkIjoiTU5BR2pvZUdXdDhnbHRYUzhPSHQifSx7ImlkIjoiTXRmVmlqZndSZkVOa3FZREZFR28ifSx7ImlkIjoiTkNhQmpQamFBNUR4bU1XaW5VMlgifSx7ImlkIjoiTzQ1Y0FYWEhINW1NaU5kWk1NWDMifSx7ImlkIjoiT3Z5U3VIamFPbnBaTENSZXhoRTEifSx7ImlkIjoiUFNCeTFjdGNsZ3dXNmE4THBMS0UifSx7ImlkIjoiUURhSm85U1poS055Mm1xOUJUa00ifSx7ImlkIjoiUnoySXRsV2FmNDhSUHg5V0lFeVcifSx7ImlkIjoiU3ZMVkdYMk1KMkw4ZFpUUEVFNFIifSx7ImlkIjoiVUNESkRyUEo3U0hUN3RsNGh4UmoifSx7ImlkIjoiVVRQeWRaeHhlZVFJMW85ejJUZHYifSx7ImlkIjoiVlpJSDlLeVk0ZVhKM0ticXhsSXUifSx7ImlkIjoiVnJHSWpxdUJVU0ZiRE5JaE5namQifSx7ImlkIjoiV093VkNYQkJTQTZqNkswa2J2SzAifSx7ImlkIjoiV2JmWm5YY3c2MHA2UUhQVG44TmgifSx7ImlkIjoiWGdnZE5pT1BNZ1duazBTdUhkVzQifSx7ImlkIjoiWWVBb3RUa0ZUdEdEczNkaEdsRWgifSx7ImlkIjoiWXdjSGxSWVhQVTJFTWNRUXJ0UngifSx7ImlkIjoiYUZHUjNsN2JNTXJNb0t4MW1EbzMifSx7ImlkIjoiYkZJMVJ5OWtMQjBKeUgwUTY2d2kifSx7ImlkIjoiZHFrbVY4NFVicDJIdXJjWkt4MW0ifSx7ImlkIjoiZXE4SjFDM1BXZEI4cDF0RDR6SUcifSx7ImlkIjoiZjB5SE8wcUZGMldKb0lwS3hualcifSx7ImlkIjoiZmM2MXM3UmlGS0lKM1l0QjdWRzkifSx7ImlkIjoiaVN2Rm1GelRzR2o2OFpEOW5RVVcifSx7ImlkIjoibDQ1RzB6ZjNPbENiT1FBckJaUUwifSx7ImlkIjoibG9RWjZzQVhYZzNVQzRtSkgweTQifSx7ImlkIjoibWJvR2JNd1VMc2tTZzdQVjd0elkifSx7ImlkIjoicUh2TEYyUUtoZGl0QzFjT1dqT3EifSx7ImlkIjoickRMOG43UThCWVhUd2p0R0xtN2QifSx7ImlkIjoickZNWmg5SjVxM1pwV2xZVlNRVUgifSx7ImlkIjoiczliZzlDQWlTYzFXNThhMXlRRGYifSx7ImlkIjoidEludlJnZlNCNUFqZzdZa2dMSEwifSx7ImlkIjoidFZPT0U4VUVlcm9nVEM2b0Z5MVAifSx7ImlkIjoidjNMV0J1YlNSV2Z0U211azBlaFoifSx7ImlkIjoidjRERmJNbm5RdWMwd0lQdktlQ0QifSx7ImlkIjoidmxHdzB0TnFrcXB1NmRPMGhTQTAifV0sImRlcGFydG1lbnQiOiJkYXRvcyIsImVtYWlsIjoiamNvcm9uYUBlcGEuZGlnaXRhbCIsImV4cCI6MTY5NTg1NzQxNSwiaWF0IjoiMjAyMy0wOS0yN1QyMjozMDoxNS43ODk1NTA3NTZaIiwicHVibGljQWNjZXNzRGF0ZSI6IiIsInVzZXJJRCI6IlBLVFFVRU5mTU1UVnFyTXg2VVlxazdKSzVoWjIifQ.HbICpzNTUr3VzuvJmK-Ke3h1Hgc05zrN1ULQrdLcVzI"

# Crear servidor MCP
mcp = FastMCP("Pitagoras API")

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
        for account in customer.get("account", []):
            account_id = account.get("accountID", "ID desconocido")
            account_name = account.get("name", "Nombre desconocido")
            provider = account.get("Provider", "Proveedor desconocido")
            accounts_info.append(f"    - Cuenta: {account_name} (ID: {account_id}, Proveedor: {provider})")
        
        accounts_text = "\n".join(accounts_info) if accounts_info else "    - No hay cuentas disponibles"
        customers_info.append(f"Cliente: {customer_name} (ID: {customer_id})\n{accounts_text}")
    
    if not customers_info:
        return "No se encontraron clientes para este usuario."
    
    return "Clientes disponibles:\n\n" + "\n\n".join(customers_info)

# -------------------- Tools --------------------

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
        account_count = len(customer.get("account", []))
        
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
    
    accounts_info = []
    for account in cliente.get("account", []):
        account_id = account.get("accountID", "ID desconocido")
        account_name = account.get("name", "Nombre desconocido")
        provider = account.get("Provider", "Proveedor desconocido")
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
    
    return f"Detalles del cliente: {customer_name} (ID: {cliente_id})\n\nCuentas:\n\n{accounts_text}"

# -------------------- Prompts --------------------

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