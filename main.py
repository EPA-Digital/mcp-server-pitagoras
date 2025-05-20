# main.py
import asyncio
import logging
from pitagoras.server import create_server
from pitagoras.config import logger

def main():
    """Main entry point for the MCP server."""
    try:
        # Create the server
        mcp = create_server()
        
        # Run the server
        logger.info("Starting Pitagoras MCP server")
        mcp.run()
        
    except Exception as e:
        logger.error(f"Error starting Pitagoras MCP server: {str(e)}")
        raise

if __name__ == "__main__":
    main()