import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

from mcp.server.fastmcp import FastMCP
from pitagoras.api import (
    get_customers,
    get_google_ads_report,
    get_facebook_ads_report,
    get_google_analytics_report
)

# Configurar logging para escribir en stderr (que MCP captura automáticamente)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr  # Escribir en stderr en lugar de un archivo
)

logger = logging.getLogger("pitagoras")

async def register_tools(mcp: FastMCP):
    """Register all MCP tools"""
    
    @mcp.tool()
    async def get_customers_data() -> str:
        """Get all available customers and their accounts"""
        customers = await get_customers()
        
        if not customers:
            return "No se encontraron clientes disponibles."
        
        result = ["# Clientes disponibles\n"]
        
        for customer in customers:
            result.append(f"## {customer['name']} (ID: {customer['ID']})")
            result.append(f"Status: {customer['status']}")
            
            # Añadir información sobre las cuentas
            accounts = customer.get("accounts", [])
            if accounts:
                result.append("\n### Cuentas:")
                
                # Agrupar cuentas por proveedor
                accounts_by_provider = {}
                for account in accounts:
                    provider = account.get("provider", "desconocido")
                    if provider not in accounts_by_provider:
                        accounts_by_provider[provider] = []
                    accounts_by_provider[provider].append(account)
                
                # Mostrar cuentas agrupadas por proveedor
                for provider, provider_accounts in accounts_by_provider.items():
                    result.append(f"\n#### {provider.upper()}:")
                    for account in provider_accounts:
                        account_id = account.get("accountID", "N/A")
                        account_name = account.get("name", "Sin nombre")
                        result.append(f"- {account_name} (ID: {account_id})")
            else:
                result.append("\n*Este cliente no tiene cuentas configuradas.*")
            
            result.append("\n---")
        
        return "\n".join(result)
    
    @mcp.tool()
    async def get_google_ads_data(
        customer_id: str,
        account_ids: List[str],
        start_date: str,
        end_date: str,
        metrics: Optional[List[str]] = None
    ) -> str:
        """
        Get Google Ads data for specific accounts
        
        Args:
            customer_id: The customer ID
            account_ids: List of account IDs to fetch data from
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metrics: Optional list of metrics to fetch (defaults to cost, impressions, clicks)
        """
        # Obtener clientes y registrar para depuración
        customers = await get_customers()
        target_customer = None
        
        # Buscar el cliente específico
        for customer in customers:
            if customer["ID"] == customer_id:
                target_customer = customer
                break
        
        # Si no encontramos el cliente, mostrar información de depuración
        if not target_customer:
            available_customers = [f"{c['ID']} ({c['name']})" for c in customers]
            return f"Cliente con ID {customer_id} no encontrado. Clientes disponibles: {', '.join(available_customers)}"
        
        customer_name = target_customer["name"]
        
        # Encontrar todas las cuentas de Google Ads para este cliente
        all_adwords_accounts = []
        for account in target_customer.get("accounts", []):
            if account.get("provider") == "adwords":
                all_adwords_accounts.append({
                    "id": account.get("accountID"),
                    "name": account.get("name")
                })
        
        # Si no hay cuentas de Google Ads, informarlo
        if not all_adwords_accounts:
            return f"El cliente {customer_name} (ID: {customer_id}) no tiene cuentas de Google Ads configuradas."
        
        # Buscar las cuentas solicitadas
        matching_accounts = []
        
        for account in target_customer.get("accounts", []):
            # Revisar si es una cuenta de adwords y si está en la lista solicitada
            if account.get("provider") == "adwords" and account.get("accountID") in account_ids:
                matching_accounts.append({
                    "account_id": account["accountID"],
                    "name": account["name"],
                    "login_customer_id": account.get("externalLoginCustomerID", "")
                })
        
        # Si no encontramos las cuentas solicitadas, mostrar información de depuración
        if not matching_accounts:
            available_accounts = [f"{a['id']} ({a['name']})" for a in all_adwords_accounts]
            return (f"No se encontraron las cuentas de Google Ads solicitadas para el cliente {customer_name}.\n"
                    f"IDs solicitados: {account_ids}\n"
                    f"Cuentas disponibles: {', '.join(available_accounts)}")
        
        # Configurar métricas predeterminadas si no se proporcionan
        if not metrics:
            metrics = ["metrics.cost_micros", "metrics.impressions", "metrics.clicks"]
        
        # Preparar parámetros de la solicitud
        report_params = {
            "accounts": matching_accounts,
            "attributes": [
                {
                    "resource_name": "campaign",
                    "fields": ["campaign.name", "campaign.id"]
                }
            ],
            "segments": ["segments.date"],
            "metrics": metrics,
            "resource": "campaign",
            "start_date": start_date,
            "end_date": end_date
        }
        
        # Obtener datos del informe
        try:
            data = await get_google_ads_report(
                accounts=matching_accounts,
                attributes=report_params["attributes"],
                segments=report_params["segments"],
                metrics=report_params["metrics"],
                resource=report_params["resource"],
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            return f"Error al obtener datos de Google Ads: {str(e)}"
        
        # Formatear la respuesta
        if "errors" in data and data["errors"]:
            return f"Errores en la API: {data['errors']}"
        
        headers = data.get("headers", [])
        rows = data.get("rows", [])
        
        if not rows:
            return f"No se encontraron datos para las cuentas seleccionadas en el período {start_date} a {end_date}."
        
        result = [f"Datos de Google Ads para {customer_name}:"]
        result.append(",".join(headers))
        
        for row in rows:
            result.append(",".join(str(cell) for cell in row))
        
        return "\n".join(result)

    @mcp.tool()
    async def get_facebook_ads_data(
        account_names: List[str],
        account_ids: List[str],
        start_date: str,
        end_date: str,
        fields: Optional[List[str]] = None
    ) -> str:
        """
        Get Facebook Ads data for specific accounts
        
        Args:
            account_names: List of account names (used for display only)
            account_ids: List of Facebook Ad account IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            fields: Optional list of fields to fetch (defaults to campaign_name, date_start, spend, impressions, clicks)
        """
        # Verificar que las listas de nombres e IDs tengan el mismo tamaño
        if len(account_names) != len(account_ids):
            return "Error: La lista de nombres de cuenta y la lista de IDs de cuenta deben tener el mismo tamaño."
        
        # Crear el formato correcto para las cuentas
        accounts = [
            {"name": name, "account_id": account_id}
            for name, account_id in zip(account_names, account_ids)
        ]
        
        # Establecer campos predeterminados si no se proporcionan
        if not fields:
            fields = ["campaign_name", "date_start", "spend", "impressions", "clicks"]
        
        try:
            # Obtener los datos del informe
            data = await get_facebook_ads_report(
                accounts=accounts,
                fields=fields,
                start_date=start_date,
                end_date=end_date
            )
            
        except Exception as e:
            return f"Error al obtener datos de Facebook Ads: {str(e)}"
        
        # Formatear la respuesta
        if "errors" in data and data["errors"]:
            return f"Errores en la API: {data['errors']}"
        
        headers = data.get("headers", [])
        rows = data.get("rows", [])
        
        if not rows:
            return f"No se encontraron datos para las cuentas seleccionadas en el período {start_date} a {end_date}."
        
        result = [f"Datos de Facebook Ads:"]
        result.append(",".join(headers))
        
        for row in rows:
            result.append(",".join(str(cell) for cell in row))
        
        return "\n".join(result)
    
    @mcp.tool()
    async def get_google_analytics_data(
        property_ids: List[str],
        start_date: str,
        end_date: str,
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        with_campaign_filter: bool = True
    ) -> str:
        """
        Get Google Analytics data for specific properties
        
        Args:
            property_ids: List of GA4 property IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            dimensions: Optional list of dimensions (defaults to date, sessionCampaignName, sessionSourceMedium)
            metrics: Optional list of metrics (defaults to sessions, transactions, totalRevenue)
            with_campaign_filter: Whether to filter for campaigns starting with 'aw_' or 'fb_'
        """
        customers = await get_customers()
        
        # Find the matching GA accounts
        matching_accounts = []
        
        for customer in customers:
            for account in customer.get("accounts", []):
                if account.get("property_id") in property_ids:
                    matching_accounts.append({
                        "property_id": account["property_id"],
                        "name": account["name"],
                        "credential_email": account.get("credentialEmail", "analytics@epa.digital")
                    })
        
        if not matching_accounts:
            # Create accounts with default values if no matches found
            matching_accounts = [
                {
                    "property_id": property_id,
                    "name": f"Property {property_id}",
                    "credential_email": "analytics@epa.digital"
                }
                for property_id in property_ids
            ]
        
        # Set default dimensions and metrics if not provided
        if not dimensions:
            dimensions = ["date", "sessionCampaignName", "sessionSourceMedium"]
        
        if not metrics:
            metrics = ["sessions", "transactions", "totalRevenue"]
        
        # Set campaign filter if requested
        filters = None
        if with_campaign_filter:
            filters = {
                "or": [
                    {
                        "in": [
                            "aw_",
                            {
                                "var": "sessionCampaignName"
                            }
                        ]
                    },
                    {
                        "in": [
                            "fb_",
                            {
                                "var": "sessionCampaignName"
                            }
                        ]
                    }
                ]
            }
        
        # Get the report data
        data = await get_google_analytics_report(
            accounts=matching_accounts,
            dimensions=dimensions,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date,
            filters=filters
        )
        
        # Format the response
        if "errors" in data and data["errors"]:
            return f"Errors occurred: {data['errors']}"
        
        headers = data.get("headers", [])
        rows = data.get("rows", [])
        
        result = ["Google Analytics data:"]
        result.append(",".join(headers))
        
        for row in rows:
            result.append(",".join(str(cell) for cell in row))
        
        return "\n".join(result)