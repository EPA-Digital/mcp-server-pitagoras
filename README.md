# Servidor MCP para Pitagoras API

Este servidor MCP proporciona acceso a la API de Pitagoras a través del protocolo Model Context Protocol (MCP), permitiendo a los modelos de lenguaje interactuar con los datos de clientes de Pitagoras de manera segura y estructurada.

## Características

- **Consulta de clientes**: Obtén información de clientes asociados a un correo electrónico
- **Detalles de cliente**: Consulta información detallada sobre un cliente específico
- **Prompts predefinidos**: Utiliza plantillas para generar consultas comunes
- **Acceso simplificado**: Interactúa con la API de Pitagoras sin necesidad de gestionar tokens o parámetros complejos

## Requisitos

- Python 3.10 o superior
- Librería MCP (`mcp[cli]`)
- httpx

## Instalación

1. Clona este repositorio o descarga el archivo `pitagoras_server.py`

2. Instala las dependencias:
   ```bash
   pip install "mcp[cli]" httpx
   ```

## Uso

### Iniciar el servidor

```bash
python pitagoras_server.py
```

### Conectar con Claude for Desktop

Para usar este servidor con Claude for Desktop, edita tu archivo de configuración `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pitagoras": {
      "command": "python",
      "args": ["/ruta/completa/a/pitagoras_server.py"]
    }
  }
}
```

### Probar con MCP Inspector

Para depurar y probar el servidor:

```bash
mcp dev /ruta/a/pitagoras_server.py
```

## Recursos disponibles

### `pitagoras://customers/{email}`

Proporciona información sobre los clientes asociados a un correo electrónico específico.

## Herramientas disponibles

### `obtener_clientes(email: str)`

Obtiene un resumen de los clientes disponibles para el correo electrónico proporcionado.

### `obtener_detalles_cliente(email: str, cliente_id: str)`

Obtiene información detallada sobre un cliente específico, incluyendo todas sus cuentas asociadas.

## Prompts disponibles

### `consultar_clientes(email: str)`

Plantilla para consultar los clientes disponibles para un usuario.

### `consultar_cliente_especifico(email: str, cliente_id: str)`

Plantilla para consultar información detallada de un cliente específico.

### `generar_reporte_resumen(email: str)`

Plantilla para generar un reporte estadístico resumido de todos los clientes de un usuario.

## Ejemplos de uso

### Consultar clientes

```
Consulta los clientes disponibles para el correo usuario@ejemplo.com
```

### Obtener detalles de un cliente específico

```
Dame información detallada del cliente con ID ABC123 para el usuario usuario@ejemplo.com
```

### Generar un reporte de resumen

```
Genera un reporte resumido de todos los clientes del usuario usuario@ejemplo.com, incluyendo estadísticas sobre tipos de cuentas y distribución por proveedor
```

## Documentación de la API

Este servidor consume la API de Pitagoras. Para más información sobre los endpoints disponibles, consulta la documentación oficial de la API.

## Limitaciones actuales

- Solo proporciona acceso al endpoint de clientes
- No soporta operaciones de escritura en la API de Pitagoras
- El token de autenticación está hardcodeado en el servidor

## Próximas mejoras

- Añadir soporte para más endpoints de la API de Pitagoras
- Implementar almacenamiento seguro del token de autenticación
- Añadir soporte para operaciones de escritura
- Mejorar el manejo de errores y reintentos