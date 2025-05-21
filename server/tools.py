import logging
import sys
from typing import List, Dict, Optional

from .utils import parse_account_selection

from mcp.server.fastmcp import FastMCP
from pitagoras.api import (
    get_customers,
    search_customers,
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
    async def get_customers_data(query: Optional[str] = None) -> str:
        """Get all available customers and their accounts.

        Args:
            query: optional text to filter customers by name or ID
        """
        customers = await (search_customers(query) if query else get_customers())
        
        if not customers:
            return "No se encontraron clientes disponibles."
        
        result = ["# Clientes disponibles\n"]
        result.append("| # | Nombre del cliente | ID | Status | Cuentas |") 
        result.append("| --- | --- | --- | --- | --- |")
        
        for i, customer in enumerate(customers, 1):
            account_counts = {
                "adwords": 0,
                "facebook": 0,
                "analytics4": 0
            }
            
            # Contar cuentas por tipo
            for account in customer.get("accounts", []):
                provider = account.get("provider", "").lower()
                if provider == "adwords" or provider == "google ads":
                    account_counts["adwords"] += 1
                elif provider == "facebook" or provider == "fb" or provider == "facebook ads":
                    account_counts["facebook"] += 1
                elif provider == "analytics4" or "property_id" in account or "propertyId" in account or "propertyID" in account:
                    account_counts["analytics4"] += 1
            
            # Crear resumen de cuentas
            account_summary = []
            if account_counts["adwords"] > 0:
                account_summary.append(f"Google Ads: {account_counts['adwords']}")
            if account_counts["facebook"] > 0:
                account_summary.append(f"Facebook: {account_counts['facebook']}")
            if account_counts["analytics4"] > 0:
                account_summary.append(f"GA4: {account_counts['analytics4']}")
            
            account_text = ", ".join(account_summary) if account_summary else "*Sin cuentas*"
            
            # Agregar fila a la tabla
            result.append(f"| {i} | {customer['name']} | {customer['ID']} | {customer['status']} | {account_text} |")
        
        # Agregar instrucciones de uso
        result.append("\n## Cómo seleccionar un cliente")
        result.append("- Escriba el **número** del cliente: Ej. `2`")
        result.append("- Use el **ID exacto**: Ej. `Selecciono el cliente RG-123456`")
        result.append("- Use el **nombre completo**: Ej. `Selecciono el cliente Empresa ABC`")
        result.append("- Puede filtrar la lista usando el parámetro `query`: Ej. `get_customers_data(query='ABC')`")
        
        return "\n".join(result)
    
    @mcp.tool()
    async def get_google_ads_data(
        customer_id: str,
        account_selection: str,
        start_date: str,
        end_date: str,
        metrics: Optional[List[str]] = None
    ) -> str:
        """
        Get Google Ads data for specific accounts
        
        Args:
            customer_id: The customer ID
            account_selection: String with the user's selection (e.g. "1,3,id:123")
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metrics: Optional list of metrics to fetch (defaults to cost_micros, impressions, clicks)
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
                    "account_id": account.get("accountID"),
                    "name": account.get("name"),
                    "login_customer_id": account.get("externalLoginCustomerID", "")
                })
        
        # Si no hay cuentas de Google Ads, informarlo
        if not all_adwords_accounts:
            return f"El cliente {customer_name} (ID: {customer_id}) no tiene cuentas de Google Ads configuradas."
        
        # Interpretar la selección del usuario
        matching_accounts = parse_account_selection(account_selection, all_adwords_accounts)
        
        # Si no encontramos las cuentas solicitadas, mostrar información de depuración
        if not matching_accounts:
            available_accounts = [f"{a['id']} ({a['name']})" for a in all_adwords_accounts]
            return (f"No se encontraron las cuentas de Google Ads solicitadas para el cliente {customer_name}.\n"
                    f"Selección solicitada: {account_selection}\n"
                    f"Cuentas disponibles: {', '.join(available_accounts)}")
        
        # Configurar métricas predeterminadas si no se proporcionan
        if not metrics:
            metrics = ["metrics.cost_micros", "metrics.impressions", "metrics.clicks"]
        else:
            # Asegurar que todas las métricas tengan el prefijo 'metrics.' 
            formatted_metrics = []
            for metric in metrics:
                if not metric.startswith("metrics."):
                    formatted_metrics.append(f"metrics.{metric}")
                else:
                    formatted_metrics.append(metric)
            metrics = formatted_metrics
        
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
        
        account_names = [account["name"] for account in matching_accounts]
        result = [f"# Datos de Google Ads ({start_date} a {end_date})"]
        result.append(f"**Cliente:** {customer_name}")
        result.append(f"**Cuentas incluidas:** {', '.join(account_names)}")
        result.append("")
        
        # Crear tabla en formato markdown
        result.append("| " + " | ".join(headers) + " |")
        result.append("| " + " | ".join(["---" for _ in headers]) + " |")
        
        for row in rows:
            # No necesitamos convertir cost_micros ya que Pitágoras ya lo devuelve en unidades monetarias
            formatted_row = [str(cell) for cell in row]
            result.append("| " + " | ".join(formatted_row) + " |")
        
        # Incluir resumen numérico
        result.append("")
        result.append(f"**Total de filas:** {len(rows)}")
        
        return "\n".join(result)

    @mcp.tool()
    async def get_facebook_ads_data(
        customer_id: str,
        accounts_selection: str,
        start_date: str,
        end_date: str,
        fields: Optional[List[str]] = None
    ) -> str:
        """
        Get Facebook Ads data for specific accounts
        
        Args:
            customer_id: The customer ID
            accounts_selection: String with the user's selection
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            fields: Optional list of fields to fetch (defaults to campaign_name, date_start, spend, impressions, clicks)
        """
        # Obtener clientes y encontrar el objetivo
        customers = await get_customers()
        target_customer = next((c for c in customers if c["ID"] == customer_id), None)
        if not target_customer:
            available = ", ".join(f"{c['ID']} ({c['name']})" for c in customers)
            return f"Cliente con ID {customer_id} no encontrado. Clientes disponibles: {available}"

        all_fb_accounts = []
        for account in target_customer.get("accounts", []):
            if account.get("provider", "").lower() in ["fb", "facebook", "facebook ads"]:
                all_fb_accounts.append({
                    "id": account.get("accountID"),
                    "account_id": account.get("accountID"),
                    "name": account.get("name")
                })

        if not all_fb_accounts:
            return f"El cliente {target_customer['name']} no tiene cuentas de Facebook Ads configuradas."

        formatted_accounts = parse_account_selection(accounts_selection, all_fb_accounts)

        if not formatted_accounts:
            available = [f"{a['id']} ({a['name']})" for a in all_fb_accounts]
            return (f"No se encontraron las cuentas de Facebook Ads solicitadas para {target_customer['name']}.\n"
                    f"Selección solicitada: {accounts_selection}\n"
                    f"Cuentas disponibles: {', '.join(available)}")

        # Establecer campos predeterminados si no se proporcionan
        if not fields:
            fields = ["campaign_name", "date_start", "spend", "impressions", "clicks"]
        
        try:
            # Obtener los datos del informe usando el formato correcto de la API
            data = await get_facebook_ads_report(
                accounts=formatted_accounts,
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
        
        account_names = [account["name"] for account in formatted_accounts]
        result = [f"# Datos de Facebook Ads ({start_date} a {end_date})"]
        result.append(f"**Cuentas incluidas:** {', '.join(account_names)}")
        result.append("")
        
        # Crear tabla en formato markdown
        result.append("| " + " | ".join(headers) + " |")
        result.append("| " + " | ".join(["---" for _ in headers]) + " |")
        
        for row in rows:
            result.append("| " + " | ".join(str(cell) for cell in row) + " |")
        
        # Incluir resumen numérico
        result.append("")
        result.append(f"**Total de filas:** {len(rows)}")
        
        # Incluir campos consultados
        result.append(f"**Campos consultados:** {', '.join(fields)}")
        
        return "\n".join(result)
    
    @mcp.tool()
    async def get_google_analytics_data(
        customer_id: str,
        accounts_selection: str,
        start_date: str,
        end_date: str,
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        with_campaign_filter: bool = True
    ) -> str:
        """
        Get Google Analytics data for specific properties
        
        Args:
            customer_id: The customer ID
            accounts_selection: Selection string with numbers or IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            dimensions: Optional list of dimensions (defaults to date, sessionCampaignName, sessionSourceMedium)
            metrics: Optional list of metrics (defaults to sessions, transactions, totalRevenue)
            with_campaign_filter: Whether to filter for campaigns starting with 'aw_' or 'fb_'
        """
        customers = await get_customers()
        target_customer = next((c for c in customers if c["ID"] == customer_id), None)
        if not target_customer:
            available = ", ".join(f"{c['ID']} ({c['name']})" for c in customers)
            return f"Cliente con ID {customer_id} no encontrado. Clientes disponibles: {available}"

        all_ga_accounts = []
        for account in target_customer.get("accounts", []):
            if "propertyId" in account or "property_id" in account or account.get("provider", "").lower() == "analytics4":
                property_id = account.get("propertyId") or account.get("property_id") or account.get("propertyID")
                account_id = account.get("accountID") or account.get("account_id")
                all_ga_accounts.append({
                    "id": account_id,
                    "account_id": account_id,
                    "property_id": property_id,
                    "name": account.get("name", "Sin nombre"),
                    "credential_email": account.get("credentialEmail", "analytics@epa.digital")
                })

        if not all_ga_accounts:
            return f"El cliente {target_customer['name']} no tiene propiedades de Google Analytics configuradas."

        accounts = parse_account_selection(accounts_selection, all_ga_accounts)
        if not accounts:
            available = [f"{a['property_id']} ({a['name']})" for a in all_ga_accounts]
            return (
                f"No se encontraron las propiedades de Google Analytics solicitadas para {target_customer['name']}.\n"
                f"Selección solicitada: {accounts_selection}\n"
                f"Propiedades disponibles: {', '.join(available)}"
            )

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
        
        try:
            # Get the report data
            data = await get_google_analytics_report(
                accounts=accounts,
                dimensions=dimensions,
                metrics=metrics,
                start_date=start_date,
                end_date=end_date,
                filters=filters
            )
            
        except Exception as e:
            return f"Error al obtener datos de Google Analytics: {str(e)}"
        
        # Format the response
        if "errors" in data and data["errors"]:
            return f"Errores en la API: {data['errors']}"
        
        headers = data.get("headers", [])
        rows = data.get("rows", [])
        
        if not rows:
            return f"No se encontraron datos para las propiedades seleccionadas en el período {start_date} a {end_date}."
        
        result = [f"# Datos de Google Analytics ({start_date} a {end_date})"]
        result.append("")
        
        # Crear tabla en formato markdown
        result.append("| " + " | ".join(headers) + " |")
        result.append("| " + " | ".join(["---" for _ in headers]) + " |")
        
        for row in rows:
            result.append("| " + " | ".join(str(cell) for cell in row) + " |")
        
        # Incluir resumen numérico
        result.append("")
        result.append(f"**Total de filas:** {len(rows)}")
        result.append(f"**Propiedades incluidas:** {', '.join(a['name'] for a in accounts)}")

        
        return "\n".join(result)

    @mcp.tool()
    async def list_accounts_by_medium(customer_id: str) -> str:
        """
        List all available accounts for a specific customer, grouped by medium
        
        Args:
            customer_id: The customer ID
        """
        customers = await get_customers()
        
        target_customer = None
        for customer in customers:
            if customer["ID"] == customer_id:
                target_customer = customer
                break
        
        if not target_customer:
            available_customers = [f"{c['ID']} ({c['name']})" for c in customers]
            return f"Cliente con ID {customer_id} no encontrado. Clientes disponibles: {', '.join(available_customers)}"
        
        customer_name = target_customer["name"]
        
        # Agrupar cuentas por tipo de medio
        accounts_by_medium = {
            "google_ads": [],
            "facebook_ads": [],
            "google_analytics": [],
            "other": []
        }
        
        for account in target_customer.get("accounts", []):
            if account.get("provider") == "adwords":
                accounts_by_medium["google_ads"].append({
                    "id": account.get("accountID", "N/A"),
                    "name": account.get("name", "Sin nombre"),
                    "login_customer_id": account.get("externalLoginCustomerID", "")
                })
            elif account.get("provider", "").lower() in ["fb", "facebook"]:
                accounts_by_medium["facebook_ads"].append({
                    "id": account.get("accountID", "N/A"),
                    "name": account.get("name", "Sin nombre")
                })
            elif "propertyId" in account or "property_id" in account or account.get("provider", "").lower() == "analytics4":
                property_id = account.get("propertyId") or account.get("property_id") or account.get("propertyID", "N/A")
                account_id = account.get("accountID") or account.get("account_id", "N/A")
                accounts_by_medium["google_analytics"].append({
                    "id": account_id,
                    "property_id": property_id,
                    "name": account.get("name", "Sin nombre"),
                    "credential_email": account.get("credentialEmail", "analytics@epa.digital")
                })
            else:
                accounts_by_medium["other"].append({
                    "id": account.get("accountID", "N/A"),
                    "name": account.get("name", "Sin nombre"),
                    "provider": account.get("provider", "desconocido")
                })
        
        # Formatear la respuesta
        result = [f"# Cuentas disponibles para {customer_name} (ID: {customer_id})\n"]
        
        # Mostrar resumen de cuentas disponibles primero
        available_media = []
        if accounts_by_medium["google_ads"]:
            available_media.append(f"Google Ads ({len(accounts_by_medium['google_ads'])})")
        if accounts_by_medium["facebook_ads"]:
            available_media.append(f"Facebook Ads ({len(accounts_by_medium['facebook_ads'])})")
        if accounts_by_medium["google_analytics"]:
            available_media.append(f"Google Analytics ({len(accounts_by_medium['google_analytics'])})")
        
        if available_media:
            result.append(f"**Plataformas disponibles:** {', '.join(available_media)}\n")
        else:
            result.append("**No hay cuentas de plataformas publicitarias configuradas para este cliente**\n")
        
        # Google Ads
        result.append("## Google Ads")
        if accounts_by_medium["google_ads"]:
            result.append("| # | Nombre | ID | Login Customer ID |")
            result.append("| --- | --- | --- | --- |")
            for i, account in enumerate(accounts_by_medium["google_ads"], 1):
                result.append(f"| {i} | {account['name']} | {account['id']} | {account['login_customer_id']} |")
            result.append("\n**Para seleccionar todas las cuentas de Google Ads use:** `all_google_ads`")
        else:
            result.append("*No se encontraron cuentas de Google Ads*")
        
        # Facebook Ads
        result.append("\n## Facebook Ads")
        if accounts_by_medium["facebook_ads"]:
            result.append("| # | Nombre | ID |")
            result.append("| --- | --- | --- |")
            for i, account in enumerate(accounts_by_medium["facebook_ads"], 1):
                result.append(f"| {i} | {account['name']} | {account['id']} |")
            result.append("\n**Para seleccionar todas las cuentas de Facebook Ads use:** `all_facebook_ads`")
        else:
            result.append("*No se encontraron cuentas de Facebook Ads*")
        
        # Google Analytics
        result.append("\n## Google Analytics")
        if accounts_by_medium["google_analytics"]:
            result.append("| # | Nombre | Property ID | Account ID | Email |")
            result.append("| --- | --- | --- | --- | --- |")
            for i, account in enumerate(accounts_by_medium["google_analytics"], 1):
                result.append(f"| {i} | {account['name']} | {account['property_id']} | {account['id']} | {account['credential_email']} |")
            result.append("\n**Para seleccionar todas las propiedades de Google Analytics use:** `all_google_analytics`")
        else:
            result.append("*No se encontraron propiedades de Google Analytics*")
        
        # Otras cuentas
        if accounts_by_medium["other"]:
            result.append("\n## Otras cuentas")
            result.append("| # | Nombre | ID | Proveedor |")
            result.append("| --- | --- | --- | --- |")
            for i, account in enumerate(accounts_by_medium["other"], 1):
                result.append(f"| {i} | {account['name']} | {account['id']} | {account['provider']} |")
        
        # Agregar ayuda para comandos rápidos
        result.append("\n## Comandos rápidos")
        result.append("- `all`: Seleccionar todas las cuentas disponibles")
        result.append("- Puedes responder con los **números** o los **IDs** de la tabla (ej: `1,3` o `123456789,987654321`). La selección se interpretará automáticamente")

        return "\n".join(result)
        
        return "\n".join(result)