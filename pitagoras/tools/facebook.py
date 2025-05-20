# pitagoras/tools/facebook.py
import json
from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, List, Any, Optional

from ..api import PitagorasAPI
from ..config import logger

def register_facebook_tools(mcp: FastMCP) -> None:
    """Register Facebook Ads tools with the MCP server."""
    
    @mcp.tool()
    async def get_facebook_fields(ctx: Context) -> str:
        """
        Get available fields for Facebook Ads.
        
        Returns:
            A list of available fields for Facebook Ads
        """
        logger.info("Get Facebook fields tool called")
        
        try:
            data = await PitagorasAPI.get_facebook_metadata()
            fields = data.get("fields", [])
            
            result = "Available Facebook Ads fields:\n\n"
            for idx, field in enumerate(fields, 1):
                field_name = field.get("name", "Unknown")
                field_type = field.get("type", "No type info")
                result += f"{idx}. {field_name} ({field_type})\n"
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting Facebook fields: {str(e)}")
            return f"Error retrieving Facebook fields: {str(e)}"
    
    @mcp.tool()
    async def get_facebook_data(
        account_ids: List[str],
        account_names: List[str],
        fields: List[str],
        start_date: str,
        end_date: str,
        ctx: Context
    ) -> str:
        """
        Fetch Facebook Ads data for specified accounts.
        
        Args:
            account_ids: List of account IDs
            account_names: List of account names
            fields: List of fields to fetch
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Formatted Facebook Ads data
        """
        logger.info(f"Get Facebook data tool called for {len(account_ids)} accounts")
        
        try:
            # Create accounts list
            accounts = [
                {
                    "account_id": account_id,
                    "name": account_name
                }
                for account_id, account_name in zip(account_ids, account_names)
            ]
            
            data = await PitagorasAPI.get_facebook_data(
                accounts=accounts,
                fields=fields,
                start_date=start_date,
                end_date=end_date
            )
            
            # Format the response
            headers = data.get("headers", [])
            rows = data.get("rows", [])
            errors = data.get("errors", [])
            
            if errors:
                error_msg = "\n".join([f"- {error}" for error in errors])
                return f"Errors occurred while fetching Facebook Ads data:\n{error_msg}"
            
            if not rows:
                return "No data found for the specified parameters."
            
            # Create a formatted table
            result = "Facebook Ads Data:\n\n"
            
            # Add headers
            result += " | ".join(headers) + "\n"
            result += "-" * (sum(len(h) for h in headers) + (len(headers) - 1) * 3) + "\n"
            
            # Add rows
            for row in rows:
                result += " | ".join(str(cell) for cell in row) + "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting Facebook data: {str(e)}")
            return f"Error retrieving Facebook Ads data: {str(e)}"