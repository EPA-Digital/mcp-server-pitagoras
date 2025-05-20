# pitagoras/tools/analytics.py
import json
from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, List, Any, Optional

from ..api import PitagorasAPI
from ..config import logger

def register_analytics_tools(mcp: FastMCP) -> None:
    """Register Google Analytics tools with the MCP server."""
    
    @mcp.tool()
    async def get_analytics_dimensions_metrics(
        property_id: str,
        credential_email: str,
        ctx: Context
    ) -> str:
        """
        Get available dimensions and metrics for Google Analytics.
        
        Args:
            property_id: The property ID
            credential_email: The credential email
        
        Returns:
            A list of available dimensions and metrics
        """
        logger.info(f"Get Analytics dimensions and metrics tool called for property: {property_id}")
        
        try:
            data = await PitagorasAPI.get_analytics_metadata(property_id, credential_email)
            dimensions = data.get("dimensions", [])
            metrics = data.get("metrics", [])
            
            result = "Available Google Analytics dimensions and metrics:\n\n"
            
            result += "Dimensions:\n"
            for idx, dim in enumerate(dimensions[:20], 1):  # Limiting to 20 for readability
                value = dim.get("value", "Unknown")
                label = dim.get("label", "No label")
                result += f"{idx}. {value} ({label})\n"
            
            if len(dimensions) > 20:
                result += f"...and {len(dimensions) - 20} more dimensions\n"
            
            result += "\nMetrics:\n"
            for idx, metric in enumerate(metrics[:20], 1):  # Limiting to 20 for readability
                value = metric.get("value", "Unknown")
                label = metric.get("label", "No label")
                result += f"{idx}. {value} ({label})\n"
            
            if len(metrics) > 20:
                result += f"...and {len(metrics) - 20} more metrics\n"
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting Analytics dimensions and metrics: {str(e)}")
            return f"Error retrieving Google Analytics dimensions and metrics: {str(e)}"
    
    @mcp.tool()
    async def get_analytics_data(
        ctx: Context,
        property_ids: List[str],
        account_ids: List[str],
        account_names: List[str],
        dimensions: List[str],
        metrics: List[str],
        start_date: str,
        end_date: str,
        with_campaign_filter: bool = True
    ) -> str:
        """
        Fetch Google Analytics data for specified properties.
        
        Args:
            property_ids: List of GA4 property IDs
            account_ids: List of GA4 account IDs
            account_names: List of account names
            dimensions: List of dimensions to include
            metrics: List of metrics to fetch
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            with_campaign_filter: Whether to filter for campaigns starting with 'aw_' or 'fb_'
        
        Returns:
            Formatted Google Analytics data
        """
        logger.info(f"Get Analytics data tool called for {len(property_ids)} properties")
        
        try:
            # Create accounts list
            accounts = [
                {
                    "property_id": property_id,
                    "account_id": account_id,
                    "name": account_name,
                    "credential_email": "analytics@epa.digital"  # Using default email
                }
                for property_id, account_id, account_name 
                in zip(property_ids, account_ids, account_names)
            ]
            
            # Create campaign filters if requested
            filters = None
            if with_campaign_filter:
                filters = {
                    "or": [
                        {
                            "in": [
                                "aw_",
                                {
                                    "var": "sessionCampaignName"
                                }
                            ]
                        },
                        {
                            "in": [
                                "fb_",
                                {
                                    "var": "sessionCampaignName"
                                }
                            ]
                        }
                    ]
                }
            
            data = await PitagorasAPI.get_analytics_data(
                accounts=accounts,
                dimensions=dimensions,
                metrics=metrics,
                start_date=start_date,
                end_date=end_date,
                filters=filters
            )
            
            # Format the response
            headers = data.get("headers", [])
            rows = data.get("rows", [])
            errors = data.get("errors", [])
            
            if errors:
                error_msg = "\n".join([f"- {error}" for error in errors])
                return f"Errors occurred while fetching Google Analytics data:\n{error_msg}"
            
            if not rows:
                return "No data found for the specified parameters."
            
            # Create a formatted table
            result = "Google Analytics Data:\n\n"
            
            # Add headers
            result += " | ".join(headers) + "\n"
            result += "-" * (sum(len(h) for h in headers) + (len(headers) - 1) * 3) + "\n"
            
            # Add rows
            for row in rows:
                result += " | ".join(str(cell) for cell in row) + "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting Analytics data: {str(e)}")
            return f"Error retrieving Google Analytics data: {str(e)}"