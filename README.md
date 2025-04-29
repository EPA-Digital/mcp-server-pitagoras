# Pitágoras MCP Server

Un servidor MCP (Model Context Protocol) para integrar datos de campañas de marketing digital desde Pitágoras API, permitiendo análisis interactivos a través de interfaces como Claude Desktop.

## Características

- Conexión a la API de Pitágoras para obtener datos de:
  - Google Ads
  - Facebook Ads
  - Google Analytics 4

## Instalación
Sigue las instrucciones de las [guia de instalación]()

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
- Crear herramientas para los siguientes endpoint:
  - https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/analytics4/metadata