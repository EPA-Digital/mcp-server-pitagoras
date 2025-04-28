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
    def select_medium(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guide the user to select a medium"""
        return [
            base.UserMessage(f"""
            # Selección de Medio para {customer_name}
            
            Ahora necesito que selecciones qué medio(s) deseas consultar para {customer_name}.
            
            ## Medios disponibles:
            1. **Google Ads** - Datos de campañas, costos, impresiones y clics
            2. **Facebook Ads** - Datos de campañas, gastos, impresiones y clics
            3. **Google Analytics** - Datos de sesiones, transacciones e ingresos
            
            Primero, voy a obtener una lista de todas las cuentas disponibles para cada medio.
            Luego podrás seleccionar específicamente qué cuentas quieres consultar.
            
            Voy a usar la herramienta `list_accounts_by_medium` para listar todas las cuentas disponibles para el cliente {customer_id}.
            """)
        ]

    @mcp.prompt()
    def google_ads_extraction(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guide the user to extract Google Ads data"""
        return [
            base.UserMessage(f"""
            # Extracción de Datos de Google Ads para {customer_name}
            
            He obtenido las cuentas de Google Ads disponibles para {customer_name}.
            
            ## Pasos:
            1. Selecciona cuáles de las cuentas listadas deseas consultar (puedes indicar los números o nombres).
            2. Define el rango de fechas para los datos (formato YYYY-MM-DD).
            3. Opcionalmente, puedes especificar las métricas que deseas obtener.
            
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
            
            He obtenido las cuentas de Facebook Ads disponibles para {customer_name}.
            
            ## Pasos:
            1. Selecciona cuáles de las cuentas listadas deseas consultar (puedes indicar los números o nombres).
            2. Define el rango de fechas para los datos (formato YYYY-MM-DD).
            3. Opcionalmente, puedes especificar los campos que deseas obtener.
            
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
            
            He obtenido las propiedades de Google Analytics disponibles para {customer_name}.
            
            ## Pasos:
            1. Selecciona cuáles de las propiedades listadas deseas consultar (puedes indicar los números o nombres).
            2. Define el rango de fechas para los datos (formato YYYY-MM-DD).
            3. Opcionalmente, puedes especificar las dimensiones y métricas que deseas obtener.
            
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
            # Selección de Medios y Cuentas para {customer_name}
            
            Para ayudarte a extraer datos de {customer_name}, seguiremos estos pasos:
            
            1. Primero, listaré todas las cuentas disponibles agrupadas por medio (Google Ads, Facebook Ads, Google Analytics).
            2. Luego, seleccionarás qué medios deseas consultar.
            3. Para cada medio seleccionado, elegirás las cuentas específicas.
            4. Finalmente, determinaremos el rango de fechas y los campos/métricas a consultar.
            
            ## Procedimiento recomendado:
            1. Revisa la lista de cuentas disponibles.
            2. Indícame qué medio deseas consultar primero.
            3. Selecciona las cuentas específicas de ese medio.
            4. Define el rango de fechas y otros parámetros.
            5. Obtendremos los datos y podrás continuar con otro medio si lo deseas.
            
            Vamos a empezar listando todas las cuentas disponibles para {customer_name}.
            """)
        ]