# Pitágoras MCP Server

Un servidor MCP (Model Context Protocol) para integrar datos de campañas de marketing digital desde Pitágoras API, permitiendo análisis interactivos a través de interfaces como Claude Desktop.

## Características

- Conexión a la API de Pitágoras para obtener datos de:
  - Google Ads
  - Facebook Ads
  - Google Analytics 4
- Herramientas para análisis de rendimiento de campañas:
  - ROAS (Return on Ad Spend)
  - CR (Conversion Rate)
  - Tendencias por período (7, 14, 30 días)
- Visualización de métricas clave:
  - Costo, impresiones y clics por campaña
  - Sesiones, transacciones y revenue
  - Rendimiento por canal
  - Rendimiento por hora del día

## Instalación

1. Clona este repositorio
2. Instala las dependencias:
   ```bash
   pip install -e .
   ```
3. Crea un archivo `.env` en la raíz del proyecto con:
   ```
   AUTH_TOKEN=tu_token_de_pitagoras
   ```

## Uso

### Iniciar el servidor MCP

```bash
python -m src.main
```

O usando la utilidad mcp:

```bash
mcp run src.main
```

### Instalar en Claude Desktop

```bash
mcp install main
```

## Integración con Claude Desktop

Una vez configurado el servidor MCP, puedes:

1. Conectarte a través de Claude Desktop
2. Seleccionar un cliente
3. Elegir las cuentas y medios para análisis
4. Realizar consultas sobre rendimiento de campañas
5. Generar dashboards, gráficos, análisis y reportes

## Estructura del proyecto

- `src/main.py`: Punto de entrada principal
- `src/config/`: Configuración y variables de entorno
- `src/api/`: Cliente HTTP y definiciones de API
- `src/models/`: Esquemas de datos
- `src/services/`: Servicios para acceder a diferentes plataformas