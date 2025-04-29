# Guía de Instalación del Servidor Pitágoras para Claude Desktop (Python)

## Requisitos Previos

Antes de comenzar, asegúrate de tener:

1. Claude Desktop instalado en tu computadora (macOS o Windows)
2. Python 3.x instalado (explicaré cómo verificarlo y descargarlo)

## Paso 1: Descargar Claude Desktop

Si aún no tienes Claude Desktop:

1. Visita [claude.ai/download](https://claude.ai/download)
2. Descarga la versión para tu sistema operativo (macOS o Windows)
3. Sigue las instrucciones de instalación que aparecen en pantalla

Si ya tienes Claude Desktop instalado, asegúrate de tener la última versión:
- Haz clic en el menú de Claude en tu computadora
- Selecciona "Check for Updates..." (Buscar actualizaciones)

## Paso 2: Verificar si tienes Python instalado

### Para usuarios de Mac:
1. Abre la aplicación Terminal (está en la carpeta Aplicaciones > Utilidades)
2. Escribe: `python3 --version` y presiona Enter

Si ves un número de versión (como Python 3.11.0), ya tienes Python. Si aparece un error, deberás instalarlo:

1. Descarga Python desde [python.org](https://www.python.org/downloads/macos/)
2. Selecciona la versión más reciente de Python 3 (recomendamos 3.12 o superior)
3. Ejecuta el instalador y sigue las instrucciones
4. Importante: durante la instalación, selecciona la opción "Install certificates" y "Add Python to PATH"

### Para usuarios de Windows:
1. Presiona las teclas Windows + R
2. Escribe "cmd" y presiona Enter
3. En la ventana de comandos, escribe: `python --version` o `py --version`

Si ves un número de versión, ya tienes Python. Si aparece un error, deberás instalarlo:

1. Descarga Python desde [python.org](https://www.python.org/downloads/windows/)
2. Selecciona la versión más reciente de Python 3
3. Importante: durante la instalación, marca la casilla "Add Python to PATH"
4. Sigue las instrucciones de instalación

## Paso 3: Descargar el Servidor Pitágoras

Vamos a descargar el repositorio como archivo ZIP:

1. Visita [https://github.com/EPA-Digital/mcp-server-pitagoras](https://github.com/EPA-Digital/mcp-server-pitagoras)
2. Haz clic en el botón verde "Code"
3. Selecciona "Download ZIP"
4. Guarda el archivo en una ubicación fácil de encontrar

### Para usuarios de Mac:
1. Localiza el archivo ZIP descargado (normalmente en la carpeta Descargas)
2. Haz doble clic para descomprimirlo
3. Se creará una carpeta llamada "mcp-server-pitagoras-main"
4. Te recomendamos mover esta carpeta a una ubicación permanente, como tu carpeta Documentos:
   - Abre Finder
   - Navega a la carpeta donde se descomprimió el archivo
   - Arrastra la carpeta "mcp-server-pitagoras-main" a tu carpeta Documentos

### Para usuarios de Windows:
1. Localiza el archivo ZIP descargado
2. Haz clic derecho y selecciona "Extraer todo"
3. Elige una ubicación permanente como "Mis Documentos"
4. Haz clic en "Extraer"

## Paso 4: Instalar dependencias necesarias

El servidor Pitágoras necesita algunas bibliotecas de Python para funcionar. Vamos a instalarlas:

### Para usuarios de Mac:
1. Abre Terminal
2. Navega a la carpeta del servidor con el comando:
   ```
   cd ~/Documentos/mcp-server-pitagoras-main
   ```
   (O usa la ruta donde hayas guardado la carpeta)
3. Instala las dependencias con:
   ```
   pip3 install -r requirements.txt
   ```

### Para usuarios de Windows:
1. Abre el Símbolo del sistema (CMD)
2. Navega a la carpeta del servidor con el comando:
   ```
   cd "C:\Users\TuUsuario\Documentos\mcp-server-pitagoras-main"
   ```
   (Reemplaza "TuUsuario" con tu nombre de usuario y ajusta la ruta si es necesario)
3. Instala las dependencias con:
   ```
   pip install -r requirements.txt
   ```

## Paso 5: Configurar las variables de entorno

Para proteger información sensible como tokens y credenciales, el servidor Pitágoras utiliza un archivo `.env` que debes crear:

### Para usuarios de Mac:
1. Abre Terminal
2. Navega a la carpeta del servidor con el comando:
   ```
   cd ~/Documentos/mcp-server-pitagoras-main
   ```
3. Crea un archivo `.env` usando el editor de texto nano:
   ```
   nano .env
   ```
4. En el editor, agrega las siguientes líneas (reemplaza los valores con tus credenciales reales):
   ```
   # Credenciales generales
   # Pitágoras API Token
   AUTH_TOKEN=tu_token_aquí
   
   # API Base URL
   API_BASE_URL=https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1
   
   # Default user email
   DEFAULT_USER_EMAIL=jcorona@epa.digital
   ```
5. Guarda el archivo presionando `Control + O`, luego `Enter`, y luego `Control + X` para salir

### Para usuarios de Windows:
1. Abre Bloc de notas u otro editor de texto
2. Crea un nuevo archivo
3. Agrega las siguientes líneas (reemplaza los valores con tus credenciales reales):
   ```
   # Credenciales generales
   # Pitágoras API Token
   AUTH_TOKEN=tu_token_aquí
   
   # API Base URL
   API_BASE_URL=https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1
   
   # Default user email
   DEFAULT_USER_EMAIL=jcorona@epa.digital
   ```
4. Guarda el archivo con el nombre `.env` (incluyendo el punto al inicio) en la carpeta `mcp-server-pitagoras-main`
   - Al guardar, selecciona "Todos los archivos" en el tipo de archivo para evitar que se guarde como ".env.txt"
   - Asegúrate de que la ubicación sea la carpeta del proyecto

### Notas importantes:
- Si no tienes todas las credenciales en este momento, completa las que tengas y agrega las demás más tarde
- Estas credenciales son altamente sensibles. No las compartas con nadie ni las incluyas en correos electrónicos o mensajes
- El archivo `.env` está configurado para ser ignorado por los sistemas de control de versiones, por lo que no se subirá accidentalmente a repositorios públicos
- Si necesitas obtener estas credenciales, consulta con tu administrador de cuentas publicitarias o con el soporte técnico correspondiente

## Paso 6: Encontrar la ruta a Python y al script principal

Necesitamos conocer la ruta exacta de Python y del script principal para la configuración:

### Para usuarios de Mac:
1. Abre Terminal
2. Escribe `which python3` y presiona Enter
3. Copia la ruta que aparece (normalmente es `/usr/bin/python3` o similar a `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3`)
4. Ahora necesitas la ruta completa al script principal. Usa el comando:
   ```
   echo "$(cd ~/Documentos/mcp-server-pitagoras-main && pwd)/main.py"
   ```
   (Ajusta la ruta si guardaste la carpeta en otro lugar)
5. Copia esta ruta completa también

### Para usuarios de Windows:
1. Abre el Símbolo del sistema (CMD)
2. Escribe `where python` y presiona Enter
3. Copia la ruta que aparece (normalmente es `C:\Users\TuUsuario\AppData\Local\Programs\Python\Python312\python.exe`)
4. Para encontrar la ruta al script principal, escribe:
   ```
   echo %CD%\main.py
   ```
   (Asegúrate de estar en la carpeta del proyecto cuando ejecutes este comando)
5. Copia esta ruta completa también

## Paso 7: Configurar Claude Desktop

Ahora configuraremos Claude Desktop para que use el servidor Pitágoras con Python:

1. Abre Claude Desktop
2. Haz clic en el menú de Claude en tu computadora (no en la ventana de la aplicación)
3. Selecciona "Settings..." (Configuración)
4. En el panel izquierdo, haz clic en "Developer" (Desarrollador)
5. Haz clic en el botón "Edit Config" (Editar configuración)

Se abrirá un archivo de configuración. Reemplaza el contenido con lo siguiente, usando las rutas que copiaste en el paso anterior:

```json
{
    "mcpServers": {
        "pitagoras": {
            "command": "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
            "args": [
                "/Users/TuUsuario/Documentos/mcp-server-pitagoras-main/main.py"
            ]
        }
    }
}
```

Reemplaza las rutas de `command` y `args` con las de python y de la ubicación del script respectivamente.

## Paso 8: Guardar la configuración y reiniciar Claude

1. Guarda el archivo de configuración:
   - En Windows: Ctrl + S
   - En macOS: Command + S
2. Cierra el archivo
3. Cierra completamente Claude Desktop
4. Vuelve a abrir Claude Desktop

## Paso 9: Verificar la instalación

Para comprobar que el servidor Pitágoras está correctamente instalado:

1. Observa la parte inferior derecha del área de entrada de texto en Claude Desktop
2. Deberías ver un icono de martillo 🔨 
3. Haz clic en el icono del martillo
4. Verifica que aparecen las herramientas de Pitágoras en la lista

Si no ves el icono del martillo o las herramientas de Pitágoras, consulta la sección de solución de problemas.

## Paso 10: Probar el servidor Pitágoras

Ahora puedes probar el servidor Pitágoras haciendo preguntas relacionadas con marketing digital:

- "¿Qué costo tuve en las campañas de Google Ads para Innovasport en los últimos 7 días?"
- "Muéstrame el rendimiento de mis campañas de Facebook Ads para Kipling de los últimos 14 días"
- "Haz un gráfico de lineas del ROAS de los últimos 7 días para chedraui ecommerce"

Claude utilizará las herramientas del servidor Pitágoras para ayudarte con tus consultas de marketing.

## Solución de Problemas

Si encuentras problemas durante la instalación:

### El icono del martillo no aparece
1. Asegúrate de haber reiniciado completamente Claude Desktop
2. Verifica que el archivo de configuración se guardó correctamente
3. Comprueba los registros (logs) de Claude Desktop:
   - En macOS: `~/Library/Logs/Claude/mcp*.log`
   - En Windows: `%APPDATA%\Claude\logs\mcp*.log`

### Las herramientas no funcionan correctamente
1. Verifica que Python está instalado correctamente
2. Asegúrate de que el archivo `.env` está correctamente configurado
3. Verifica que las rutas en el archivo de configuración son correctas
4. Prueba ejecutar el script manualmente para ver si hay errores:
   ```
   python3 /ruta/a/tu/mcp-server-pitagoras-main/main.py
   ```

### Si necesitas más ayuda
Si continúas teniendo problemas, contacta al equipo de soporte técnico de tu agencia o consulta los recursos de desarrollo del servidor Pitágoras.
