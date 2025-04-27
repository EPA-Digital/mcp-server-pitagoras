# server/prompts.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base


async def register_prompts(mcp: FastMCP):
    """Register all MCP prompts"""
    
    @mcp.prompt()
    def select_customer() -> list[base.Message]:
        """Guide the user to select a customer"""
        return [
            base.UserMessage("""
            # Selección de Cliente de Pitágoras
            
            Para empezar a extraer datos, necesito que selecciones un cliente.
            
            Voy a buscar la lista de clientes disponibles para ti y te los mostraré.
            
            ## Pasos:
            1. Primero voy a obtener la lista de clientes.
            2. Te mostraré los clientes disponibles con sus IDs.
            3. Selecciona el cliente del que quieres extraer datos.
            
            Voy a usar la herramienta `get_customers_data` para obtener esta información.
            """)
        ]
    
    @mcp.prompt()
    def google_ads_extraction(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guide the user to extract Google Ads data"""
        return [
            base.UserMessage(f"""
            # Extracción de Datos de Google Ads para {customer_name}
            
            Ahora vamos a extraer datos de Google Ads para el cliente seleccionado.
            
            ## Información del Cliente:
            - ID del Cliente: {customer_id}
            - Nombre del Cliente: {customer_name}
            
            ## Pasos:
            1. Voy a buscar las cuentas de Google Ads disponibles para este cliente.
            2. Te mostraré las cuentas disponibles con sus IDs.
            3. Selecciona las cuentas de las que quieres extraer datos.
            4. Define el rango de fechas para los datos (formato YYYY-MM-DD).
            5. Opcionalmente, puedes especificar las métricas que deseas obtener.
            
            ## Métricas disponibles comunes:
            - metrics.cost_micros (Costo)
            - metrics.impressions (Impresiones)
            - metrics.clicks (Clics)
            - metrics.conversions (Conversiones)
            - metrics.conversions_value (Valor de conversiones)
            
            Una vez que tengas esta información, usaré la herramienta `get_google_ads_data` para obtener los datos.
            """)
        ]
    
    @mcp.prompt()
    def facebook_ads_extraction(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guide the user to extract Facebook Ads data"""
        return [
            base.UserMessage(f"""
            # Extracción de Datos de Facebook Ads para {customer_name}
            
            Ahora vamos a extraer datos de Facebook Ads para el cliente seleccionado.
            
            ## Información del Cliente:
            - ID del Cliente: {customer_id}
            - Nombre del Cliente: {customer_name}
            
            ## Pasos:
            1. Voy a buscar las cuentas de Facebook Ads disponibles para este cliente.
            2. Te mostraré las cuentas disponibles con sus IDs.
            3. Selecciona las cuentas de las que quieres extraer datos.
            4. Define el rango de fechas para los datos (formato YYYY-MM-DD).
            5. Opcionalmente, puedes especificar los campos que deseas obtener.
            
            ## Campos disponibles comunes:
            - campaign_name (Nombre de la campaña)
            - date_start (Fecha)
            - spend (Gasto)
            - impressions (Impresiones)
            - clicks (Clics)
            - actions (Acciones)
            
            Una vez que tengas esta información, usaré la herramienta `get_facebook_ads_data` para obtener los datos.
            """)
        ]
    
    @mcp.prompt()
    def google_analytics_extraction(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guide the user to extract Google Analytics data"""
        return [
            base.UserMessage(f"""
            # Extracción de Datos de Google Analytics para {customer_name}
            
            Ahora vamos a extraer datos de Google Analytics para el cliente seleccionado.
            
            ## Información del Cliente:
            - ID del Cliente: {customer_id}
            - Nombre del Cliente: {customer_name}
            
            ## Pasos:
            1. Voy a buscar las propiedades de Google Analytics disponibles para este cliente.
            2. Te mostraré las propiedades disponibles con sus IDs.
            3. Selecciona las propiedades de las que quieres extraer datos.
            4. Define el rango de fechas para los datos (formato YYYY-MM-DD).
            5. Opcionalmente, puedes especificar las dimensiones y métricas que deseas obtener.
            
            ## Dimensiones comunes:
            - date (Fecha)
            - sessionCampaignName (Nombre de la campaña)
            - sessionSourceMedium (Fuente/Medio)
            
            ## Métricas comunes:
            - sessions (Sesiones)
            - transactions (Transacciones)
            - totalRevenue (Ingresos totales)
            
            Por defecto, se aplicará un filtro para mostrar solo campañas que comiencen con 'aw_' o 'fb_'.
            Puedes indicar si deseas desactivar este filtro.
            
            Una vez que tengas esta información, usaré la herramienta `get_google_analytics_data` para obtener los datos.
            """)
        ]
    
    @mcp.prompt()
    def combined_data_extraction(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guide the user to extract data from multiple platforms"""
        return [
            base.UserMessage(f"""
            # Extracción de Datos Combinados para {customer_name}
            
            Ahora vamos a extraer datos de múltiples plataformas para el cliente seleccionado.
            
            ## Información del Cliente:
            - ID del Cliente: {customer_id}
            - Nombre del Cliente: {customer_name}
            
            ## Plataformas Disponibles:
            1. Google Ads
            2. Facebook Ads
            3. Google Analytics
            
            ## Procedimiento:
            1. Indica de qué plataformas quieres extraer datos.
            2. Para cada plataforma, te guiaré a través del proceso de selección de cuentas y parámetros.
            3. Extraeré los datos de cada plataforma.
            4. Te mostraré los resultados consolidados.
            
            Puedo ayudarte a extraer datos de una sola plataforma o de múltiples plataformas al mismo tiempo.
            """)
        ]