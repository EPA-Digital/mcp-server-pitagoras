# MCP Pitagoras Analytics Server

Servidor MCP que combina la extracción de datos desde Pitágoras con capacidades de análisis de datos en Python. Permite a los usuarios extraer datos de marketing digital y analizarlos directamente en Claude Desktop.

## Requisitos

- Python 3.9 o superior
- Token de autenticación para la API de Pitágoras

## Instalación

### Con pip

```bash
pip install git+https://github.com/tu-usuario/mcp-pitagoras.git
```

### Desde el código fuente

1. Clona el repositorio:

```bash
git clone https://github.com/tu-usuario/mcp-pitagoras.git
cd mcp-pitagoras
```

2. Instala las dependencias:

```bash
pip install -e .
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
AUTH_TOKEN=tu_token_de_autenticacion_para_pitagoras
```

## Uso

### Con Claude Desktop

1. Abre Claude Desktop.

2. Edita el archivo de configuración de Claude Desktop ubicado en:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

3. Añade el servidor MCP Pitágoras:

```json
{
  "mcpServers": {
    "pitagoras-analytics": {
      "command": "mcp-pitagoras",
      "env": {
        "AUTH_TOKEN": "tu_token_de_autenticacion_para_pitagoras"
      }
    }
  }
}
```

4. Reinicia Claude Desktop.

### Desde la línea de comandos

Para ejecutar el servidor directamente desde la línea de comandos:

```bash
mcp-pitagoras
```

## Herramientas disponibles

### Herramientas de cliente

- `extract_clients_data`: Extrae los clientes disponibles para un correo electrónico.
- `mediums_and_accounts_selector`: Selecciona los medios y cuentas de los que se va a extraer datos.

### Herramientas de extracción

- `extract_from_pitagoras`: Extracción unificada de datos de Google Ads, Facebook Ads y Google Analytics.
- `get_google_ads_metadata`: Obtiene campos disponibles para Google Ads.
- `get_facebook_ads_metadata`: Obtiene campos disponibles para Facebook Ads.
- `get_google_analytics_metadata`: Obtiene campos disponibles para Google Analytics.

### Herramientas de análisis

- `run_script`: Ejecuta scripts para análisis de datos en Python.
- `list_dataframes`: Lista los DataFrames disponibles en memoria.

## Prompts disponibles

- `analisis_exploratorio`: Prompt para análisis exploratorio básico de datos de marketing.
- `comparacion_rendimiento`: Prompt para comparación de rendimiento entre plataformas.
- `recomendaciones_optimizacion`: Prompt para recomendaciones de optimización de campañas.

## Flujo de uso típico

1. Extraer clientes disponibles con `extract_clients_data`.
2. Seleccionar cliente, medio y cuentas con `mediums_and_accounts_selector`.
3. Obtener metadatos (campos disponibles) con las herramientas de metadatos.
4. Extraer datos con `extract_from_pitagoras`.
5. Listar DataFrames disponibles con `list_dataframes`.
6. Analizar datos utilizando `run_script`.
7. Usar prompts para análisis específicos según necesidad.

## Ejemplos

### Extracción de clientes

```
¿Puedes extraer los clientes disponibles para mi correo jcorona@epa.digital?
```

### Selección de plataforma y cuentas

```
Selecciona el cliente con ID "0MzvbWaTrW7gedBvdwOD", la plataforma Google Ads y las cuentas con IDs "1019423192" y "2535179120"
```

### Extracción de datos

```
Extrae datos de Google Ads para las siguientes métricas: "metrics.impressions", "metrics.clicks", "metrics.cost_micros" del 2025-01-01 al 2025-01-31.
```

### Análisis de datos

```
Ejecuta un análisis exploratorio de los datos de Google Ads extraídos, mostrando las principales estadísticas y tendencias.
```

## Seguridad

- El servidor valida todas las entradas del usuario.
- Implementa manejo de errores para todas las llamadas a la API.
- Las credenciales se guardan de forma segura en variables de entorno.
- La ejecución de scripts está limitada al entorno del servidor.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Haz push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la licencia MIT - vea el archivo LICENSE para más detalles.