# server/prompts.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base


async def register_prompts(mcp: FastMCP):
    """Register all MCP prompts"""
    @mcp.prompt()
    def select_customer() -> list[base.Message]:
        """Guía al usuario para seleccionar un cliente específico de la lista disponible."""
        return [
            base.UserMessage("""
            # Selección de Cliente de Pitágoras
            
            Para comenzar el análisis de datos, necesito que selecciones un cliente específico.
            
            ## Proceso automático:
            1. Estoy obteniendo la lista completa de clientes disponibles en el sistema
            2. Te presentaré cada cliente con su ID único y nombre completo
            
            ## Instrucciones:
            1. Revisa la lista de clientes que te mostraré a continuación
            2. Selecciona UN cliente escribiendo su ID exacto o su nombre completo
            3. Si no encuentras el cliente que buscas, indica "Cliente no encontrado" y describiré opciones alternativas
            
            ## Formato de respuesta esperado:
            - "Selecciono el cliente [ID]" 
            - "Selecciono el cliente [Nombre completo]"
            
            Ejecutando la herramienta `get_customers_data` para obtener la información...
            """)
        ]

    @mcp.prompt()
    def select_medium(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guía al usuario para seleccionar uno o más medios específicos para el cliente seleccionado."""
        return [
            base.UserMessage(f"""
            # Selección de Medio Publicitario para {customer_name}
            
            Ahora necesito que especifiques exactamente qué plataforma(s) publicitaria(s) deseas analizar para {customer_name} (ID: {customer_id}).
            
            ## Plataformas disponibles:
            1. **Google Ads** - Datos de campañas de búsqueda, display y video
            2. **Facebook Ads** - Datos de campañas en Facebook e Instagram
            3. **Google Analytics 4** - Métricas de rendimiento del sitio web y resultados
            
            ## Instrucciones específicas:
            1. Estoy obteniendo la lista completa de cuentas por cada plataforma
            2. Indica claramente qué plataforma(s) deseas consultar (puedes seleccionar más de una)
            3. Si quieres analizar TODAS las plataformas, escribe "Todas las plataformas"
            
            ## Formato de respuesta esperado:
            - "Quiero analizar Google Ads"
            - "Selecciono Facebook Ads y Google Analytics"
            - "Todas las plataformas"
            
            Ejecutando la herramienta `list_accounts_by_medium` para el cliente {customer_id}...
            """)
        ]

    @mcp.prompt()
    def google_ads_extraction(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guía al usuario para extraer datos específicos de Google Ads con parámetros claros."""
        return [
            base.UserMessage(f"""
            # Extracción de Datos de Google Ads para {customer_name}
            
            He obtenido las cuentas específicas de Google Ads disponibles para {customer_name} (ID: {customer_id}).
            
            ## Parámetros requeridos:
            1. **Cuentas** - Indica los números o IDs de las cuentas que aparecen en la tabla:
            - Ejemplo: "1,3" o "1234567890,0987654321"
            - Alternativa: "all" para todas las cuentas
            
            2. **Rango de fechas** - Define el período exacto a analizar:
            - Fecha inicial: YYYY-MM-DD (Ej: 2025-01-01)
            - Fecha final: YYYY-MM-DD (Ej: 2025-04-30)
            - Períodos predefinidos: "Último mes", "Último trimestre", "Año actual"
            
            ## Métricas (opcional):
            Si no especificas métricas, usaré las predeterminadas (costo, impresiones, clics).
            Para personalizar, indica exactamente cuáles necesitas:
            
            - metrics.cost_micros → Costo (ya convertido a unidades monetarias)
            - metrics.impressions → Número total de impresiones
            - metrics.clicks → Número total de clics
            
            ## Formato de respuesta requerido:
            ```
            Cuentas: [IDs separados por coma o "Todas"]
            Fecha inicial: YYYY-MM-DD
            Fecha final: YYYY-MM-DD
            Métricas: [lista separada por comas o "predeterminadas"]
            ```
            
            ## Importante
            - Si no encuentras información no continues reintenta extraer los datos pero en ningun caso aproximes la información.
            - En caso de continuar con errores comunicalo a l usuario, pero no uses datos que no vengan de la API de Pitágoras.
            
            Con esta información precisa, ejecutaré la herramienta `get_google_ads_data` para obtener los datos solicitados.
            """)
        ]

    @mcp.prompt()
    def facebook_ads_extraction(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guía al usuario para extraer datos específicos de Facebook Ads con parámetros precisos."""
        return [
            base.UserMessage(f"""
            # Extracción de Datos de Facebook Ads para {customer_name}
            
            He obtenido las cuentas específicas de Facebook Ads disponibles para {customer_name} (ID: {customer_id}).
            
            ## Parámetros requeridos:
            1. **Cuentas** - Indica los números o IDs de las cuentas mostradas en la tabla:
            - Ejemplo: "2,5" o "act_1234567890,act_0987654321"
            - Alternativa: "all" para todas las cuentas disponibles
            
            2. **Rango de fechas** - Define el período exacto a analizar:
            - Fecha inicial: YYYY-MM-DD (Ej: 2025-01-01)
            - Fecha final: YYYY-MM-DD (Ej: 2025-04-30)
            - Períodos predefinidos: "Último mes", "Último trimestre", "Año actual"
            
            ## Campos (opcional):
            Si no especificas campos, usaré los predeterminados (campaign_name, date_start, spend, impressions, clicks).
            Para personalizar, indica exactamente cuáles necesitas:
            
            - campaign_name → Nombre de la campaña
            - date_start → Fecha de inicio de datos
            - spend → Gasto total en moneda de la cuenta
            - impressions → Número total de impresiones
            - clicks → Número total de clics
            
            ## Formato de respuesta requerido:
            ```
            Cuentas: [Nombres/IDs separados por coma o "Todas"]
            Fecha inicial: YYYY-MM-DD
            Fecha final: YYYY-MM-DD
            Campos: [lista separada por comas o "predeterminados"]
            ```
            ## Importante
            - Si no encuentras información no continues reintenta extraer los datos pero en ningun caso aproximes la información.
            - En caso de continuar con errores comunicalo a l usuario, pero no uses datos que no vengan de la API de Pitágoras.
            
            Con esta información precisa, ejecutaré la herramienta `get_facebook_ads_data` para obtener los datos solicitados.
            """)
        ]

    @mcp.prompt()
    def google_analytics_extraction(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guía al usuario para extraer datos específicos de Google Analytics 4 con parámetros completos."""
        return [
            base.UserMessage(f"""
            # Extracción de Datos de Google Analytics 4 para {customer_name}
            
            He obtenido las propiedades específicas de Google Analytics 4 disponibles para {customer_name} (ID: {customer_id}).
            
            ## Parámetros requeridos:
            1. **Propiedades** - Indica los números o IDs de las propiedades mostradas en la tabla:
            - Ejemplo: "1,4" o "196407566,123456789"
            - Alternativa: "all" para todas las propiedades disponibles
            
            2. **Rango de fechas** - Define el período exacto a analizar:
            - Fecha inicial: YYYY-MM-DD (Ej: 2025-01-01)
            - Fecha final: YYYY-MM-DD (Ej: 2025-04-30)
            - O usa períodos predefinidos: "Último mes", "Último trimestre", "Año actual"
            
            ## Parámetros opcionales:
            1. **Dimensiones** (opcional):
            - Usa "predeterminadas" o especifica una lista separada por comas
            - Predeterminadas: date, sessionCampaignName, sessionSourceMedium
            - Otras opciones: city, country, deviceCategory, landingPage, etc.
            
            2. **Métricas** (opcional):
            - Usa "predeterminadas" o especifica una lista separada por comas
            - Predeterminadas: sessions, transactions, totalRevenue
            
            3. **Filtro de campañas** (opcional):
            - Usa "activado" (predeterminado) o "desactivado"  
            - Cuando está activado, solo muestra campañas que empiezan con 'aw_' o 'fb_'
            
            ## Formato de respuesta requerido:
            ```
            Propiedades: [números/IDs o "all"]
            Fecha inicial: YYYY-MM-DD
            Fecha final: YYYY-MM-DD
            Dimensiones: [lista o "predeterminadas"]
            Métricas: [lista o "predeterminadas"]
            Filtro de campañas: [activado/desactivado]
            ```
            
            ## Importante
            - Si no encuentras información no continues reintenta extraer los datos pero en ningun caso aproximes la información.
            - En caso de continuar con errores comunicalo a l usuario, pero no uses datos que no vengan de la API de Pitágoras.
            
            Con esta información completa, ejecutaré la herramienta `get_google_analytics_data` para obtener los datos solicitados.
            """)
        ]
    
    @mcp.prompt()
    def combined_data_extraction(customer_id: str, customer_name: str) -> list[base.Message]:
        """Guía completa para extraer datos de múltiples plataformas de forma estructurada."""
        return [
            base.UserMessage(f"""
            # Extracción Multiplataforma para {customer_name}
            
            Voy a ayudarte a extraer datos de múltiples plataformas para {customer_name} (ID: {customer_id}) siguiendo un proceso estructurado.
            
            ## Proceso secuencial:
            1. Primero obtendré y te mostraré el inventario completo de cuentas agrupadas por plataforma
            2. Luego seguiremos un flujo de trabajo específico para cada plataforma seleccionada
            
            ## Instrucciones paso a paso:
            
            ### PASO 1: Selección de plataformas
            Después de ver el inventario, indica exactamente qué plataformas deseas analizar:
            - "Google Ads únicamente"
            - "Facebook Ads y Google Analytics"
            - "Todas las plataformas disponibles"
            
            ### PASO 2: Parámetros por plataforma
            Para cada plataforma seleccionada, especificarás:
            
            **Para Google Ads:**
            ```
            Cuentas: [IDs específicos o "Todas"]
            Fecha inicial: YYYY-MM-DD
            Fecha final: YYYY-MM-DD
            Métricas: [métricas específicas o "predeterminadas"]
            ```
            
            **Para Facebook Ads:**
            ```
            Cuentas: [IDs/Nombres específicos o "Todas"]
            Fecha inicial: YYYY-MM-DD
            Fecha final: YYYY-MM-DD
            Campos: [campos específicos o "predeterminados"]
            ```
            
            **Para Google Analytics:**
            ```
            Property IDs: [lista específica]
            Account IDs: [lista correspondiente]
            Account Names: [nombres exactos]
            Fecha inicial: YYYY-MM-DD
            Fecha final: YYYY-MM-DD
            Dimensiones y Métricas: [específicas o "predeterminadas"]
            Filtro de campañas: [activado/desactivado]
            ```
            
            ### PASO 3: Análisis de resultados
            Después de cada extracción, tendrás estas opciones:
            - "Continuar con la siguiente plataforma"
            - "Analizar estos resultados en detalle"
            - "Descargar los datos en formato CSV"
            - "Finalizar la extracción"
            
            
            ## Nota importante:
            
            - Si no encuentras información no continues reintenta extraer los datos pero en ningun caso aproximes la información.
            - En caso de continuar con errores comunicalo a l usuario, pero no uses datos que no vengan de la API de Pitágoras.
            
            Ejecutando `list_accounts_by_medium` para obtener el inventario completo de cuentas para {customer_name}...
            """)
        ]