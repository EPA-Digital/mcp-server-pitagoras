# Pitágoras MCP Server

Un servidor MCP (Model Context Protocol) para integrar datos de campañas de marketing digital desde Pitágoras API, permitiendo análisis interactivos a través de interfaces como Claude Desktop.

## Características

- Conexión a la API de Pitágoras para obtener datos de:
  - Google Ads
  - Facebook Ads
  - Google Analytics 4

## Instalación

Sigue las instrucciones de la [guía de instalación](https://github.com/EPA-Digital/mcp-server-pitagoras/blob/master/install_guide.md)

## Integración con Claude Desktop

Una vez configurado el servidor MCP, puedes:

1. Conectarte a través de Claude Desktop
2. Seleccionar un cliente
3. Elegir las cuentas y medios para análisis
4. Realizar consultas sobre rendimiento de campañas
5. Generar dashboards, gráficos, análisis y reportes

## Estructura del proyecto

```bash
.
├── CLAUDE.md
├── README.md
├── initial_prompt.md
├── main.py
├── pitagoras
│   ├── __init__.py
│   ├── api.py
│   ├── config.py
│   └── models.py
├── pyproject.toml
├── requirements.txt
└── server
    ├── __init__.py
    ├── prompts.py
    ├── resources.py
    ├── tools.py
    └── utils.py
```

## Todo

- Crear prompts más elaborados por medio
- Crear herramientas para los siguientes endpoints para mostrarle al LLM el esquema de los medios:
  - https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/analytics4/metadata
  - https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/facebook/schema
  - https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/adwords/resources
  - https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/adwords/attributes?resource_name=campaign
  - https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/adwords/segments?resource_name=campaign
  - https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/adwords/metrics?resource_name=campaign
- Publicar el módulo en pypi para mantenerlo actualizado
  - Encontrar la forma de pasarle el token sin exponerlo al público

## Changelog

### v0.2.1
- Corrección: Solucionado error que impedía realizar consultas a Google Analytics 4

### v0.2.0
- Agregada integración con Google Analytics 4
- Mejoras en la estructura del proyecto
- Actualización de dependencias

### v0.1.0
- Versión inicial
- Soporte para Google Ads y Facebook Ads
- Implementación del protocolo MCP básico