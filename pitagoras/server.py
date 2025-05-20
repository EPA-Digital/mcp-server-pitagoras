# pitagoras/server.py
import logging
from mcp.server.fastmcp import FastMCP

from .config import logger
from .tools.accounts import register_account_tools
from .tools.google_ads import register_google_ads_tools
from .tools.facebook import register_facebook_tools
from .tools.analytics import register_analytics_tools
from .prompts.templates import register_prompts

def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    # Create the server with metadata
    mcp = FastMCP(
        "Pitagoras Analytics",
        version="1.0.0",
        description="MCP server for accessing marketing analytics data via Pitagoras API",
        dependencies=["httpx", "python-dotenv"]
    )
    
    # Register all tools
    register_account_tools(mcp)
    register_google_ads_tools(mcp)
    register_facebook_tools(mcp)
    register_analytics_tools(mcp)
    
    # Register all prompts
    register_prompts(mcp)
    
    logger.info("Pitagoras MCP server initialized with all tools and prompts")
    return mcp