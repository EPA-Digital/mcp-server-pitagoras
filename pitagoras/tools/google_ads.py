# pitagoras/tools/google_ads.py
import json
from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, List, Any, Optional

from ..api import PitagorasAPI
from ..config import logger

def register_google_ads_tools(mcp: FastMCP) -> None:
    """Register Google Ads tools with the MCP server."""
    
    @mcp.tool()
    async def get_google_ads_metrics(resource_name: str, ctx: Context) -> str:
        """
        Get available metrics for Google Ads.
        
        Args:
            resource_name: Resource name (e.g., campaign, ad_group)
        
        Returns:
            A list of available metrics for the specified resource
        """
        logger.info(f"Get Google Ads metrics tool called for resource: {resource_name}")
        
        try:
            metrics = await PitagorasAPI.get_google_ads_metadata(resource_name)
            
            # Replace cost_micros with cost as mentioned in requirements
            metrics = ["cost" if m == "metrics.cost_micros" else m for m in metrics]
            
            result = f"Available Google Ads metrics for {resource_name}:\n\n"
            for idx, metric in enumerate(metrics, 1):
                result += f"{idx}. {metric}\n"
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting Google Ads metrics: {str(e)}")
            return f"Error retrieving Google Ads metrics: {str(e)}"
    
    @mcp.tool()
    async def get_google_ads_data(
        account_ids: List[str],
        login_customer_ids: List[str],
        account_names: List[str],
        attributes: List[Dict[str, Any]],
        segments: List[str],
        metrics: List[str],
        resource: str,
        start_date: str,
        end_date: str,
        ctx: Context
    ) -> str:
        """
        Fetch Google Ads data for specified accounts.
        
        Args:
            account_ids: List of account IDs
            login_customer_ids: List of login customer IDs
            account_names: List of account names
            attributes: List of attributes to fetch
            segments: List of segments to include
            metrics: List of metrics to fetch
            resource: Resource type (e.g., campaign)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Formatted Google Ads data
        """
        logger.info(f"Get Google Ads data tool called for {len(account_ids)} accounts")
        
        try:
            # Transform metrics to include "metrics." prefix if not already there
            formatted_metrics = [
                m if m == "cost" or m.startswith("metrics.") else f"metrics.{m}" 
                for m in metrics
            ]
            
            # Convert "cost" back to "metrics.cost_micros" for the API call
            formatted_metrics = [
                "metrics.cost_micros" if m == "cost" else m 
                for m in formatted_metrics
            ]
            
            # Create accounts list
            accounts = [
                {
                    "account_id": account_id,
                    "name": account_name,
                    "login_customer_id": login_customer_id
                }
                for account_id, account_name, login_customer_id 
                in zip(account_ids, account_names, login_customer_ids)
            ]
            
            data = await PitagorasAPI.get_google_ads_data(
                accounts=accounts,
                attributes=attributes,
                segments=segments,
                metrics=formatted_metrics,
                resource=resource,
                start_date=start_date,
                end_date=end_date
            )
            
            # Format the response
            headers = data.get("headers", [])
            rows = data.get("rows", [])
            errors = data.get("errors", [])
            
            if errors:
                error_msg = "\n".join([f"- {error}" for error in errors])
                return f"Errors occurred while fetching Google Ads data:\n{error_msg}"
            
            if not rows:
                return "No data found for the specified parameters."
            
            # Create a formatted table
            result = "Google Ads Data:\n\n"
            
            # Add headers
            result += " | ".join(headers) + "\n"
            result += "-" * (sum(len(h) for h in headers) + (len(headers) - 1) * 3) + "\n"
            
            # Add rows
            for row in rows:
                result += " | ".join(str(cell) for cell in row) + "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting Google Ads data: {str(e)}")
            return f"Error retrieving Google Ads data: {str(e)}"