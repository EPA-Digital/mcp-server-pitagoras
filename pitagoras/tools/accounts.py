# pitagoras/tools/accounts.py
import json
from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, List, Any, Optional

from ..api import PitagorasAPI
from ..config import logger

def register_account_tools(mcp: FastMCP) -> None:
    """Register account-related tools with the MCP server."""
    
    @mcp.tool()
    async def list_clients(user_email: str, ctx: Context) -> str:
        """
        List available clients for a user email.
        
        Args:
            user_email: The email of the user
        
        Returns:
            A formatted list of available clients
        """
        logger.info(f"List clients tool called for email: {user_email}")
        
        try:
            data = await PitagorasAPI.get_customers(user_email)
            customers = data.get("customers", [])
            
            if not customers:
                return "No clients found for this email."
            
            result = "Available clients:\n\n"
            for idx, customer in enumerate(customers, 1):
                result += f"{idx}. ID: {customer['ID']}, Name: {customer['name']}, Status: {customer['status']}\n"
            
            return result
        
        except Exception as e:
            logger.error(f"Error listing clients: {str(e)}")
            return f"Error retrieving clients: {str(e)}"
    
    @mcp.tool()
    async def list_mediums(ctx: Context) -> str:
        """
        List available media platforms.
        
        Returns:
            A formatted list of available media platforms
        """
        logger.info("List mediums tool called")
        
        # Intentionally excluding 'analytics' as requested
        mediums = [
            {"id": "google_ads", "name": "Google Ads", "description": "Google Ads platform data"},
            {"id": "facebook", "name": "Facebook Ads", "description": "Facebook advertising data"},
            {"id": "analytics4", "name": "Google Analytics 4", "description": "Google Analytics 4 data"}
        ]
        
        result = "Available media platforms:\n\n"
        for idx, medium in enumerate(mediums, 1):
            result += f"{idx}. {medium['name']}: {medium['description']}\n"
        
        return result
    
    @mcp.tool()
    async def list_accounts(client_id: str, medium: str, ctx: Context) -> str:
        """
        List accounts for a specific client and medium.
        
        Args:
            client_id: The ID of the client
            medium: The medium to list accounts for (google_ads, facebook, analytics4)
        
        Returns:
            A formatted list of available accounts for the specified client and medium
        """
        logger.info(f"List accounts tool called for client: {client_id}, medium: {medium}")
        
        try:
            # Get all customers data
            data = await PitagorasAPI.get_customers("jcorona@epa.digital")  # Using default email as parameter
            
            # Find the specific customer
            customer = next((c for c in data.get("customers", []) if c["ID"] == client_id), None)
            if not customer:
                return f"Client with ID {client_id} not found."
            
            # Filter accounts by medium
            provider_mapping = {
                "google_ads": "adwords",
                "facebook": "facebook",
                "analytics4": "analytics4"
            }
            
            provider = provider_mapping.get(medium)
            if not provider:
                return f"Invalid medium: {medium}"
            
            accounts = [acc for acc in customer["accounts"] if acc.get("provider") == provider]
            
            if not accounts:
                return f"No {medium} accounts found for client {customer['name']}."
            
            result = f"{medium.capitalize()} accounts for {customer['name']}:\n\n"
            for idx, account in enumerate(accounts, 1):
                result += f"{idx}. ID: {account['accountID']}, Name: {account['name']}\n"
                if medium == "google_ads" and "externalLoginCustomerID" in account:
                    result += f"   Login Customer ID: {account['externalLoginCustomerID']}\n"
            
            return result
        
        except Exception as e:
            logger.error(f"Error listing accounts: {str(e)}")
            return f"Error retrieving accounts: {str(e)}"