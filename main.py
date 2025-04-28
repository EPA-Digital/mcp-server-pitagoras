# main.py
from server import create_server

# Crear el servidor MCP y asignarlo a una variable que el CLI pueda detectar
mcp = create_server()

if __name__ == "__main__":
    mcp.run(transport="stdio")