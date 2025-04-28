# server/__init__.py
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP

from .prompts import register_prompts
from .resources import register_resources
from .tools import register_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def create_server(name: str = "Pitágoras MCP") -> FastMCP:
    """
    Create and configure an MCP server for Pitágoras
    
    Args:
        name: Name of the MCP server
        
    Returns:
        Configured FastMCP server
    """
    # Create FastMCP server
    mcp = FastMCP(name)
    
    # Register all components
    # We use async functions to register components, and call them synchronously
    import asyncio
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Register all resources, tools, and prompts
    loop.run_until_complete(register_resources(mcp))
    loop.run_until_complete(register_tools(mcp))
    loop.run_until_complete(register_prompts(mcp))
    
    return mcp