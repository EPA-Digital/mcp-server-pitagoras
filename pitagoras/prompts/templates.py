# pitagoras/prompts/templates.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

def register_prompts(mcp: FastMCP) -> None:
    """Register prompts with the MCP server."""
    
    @mcp.prompt()
    def select_client(user_email: str) -> str:
        """
        Prompt for selecting a client.
        
        Args:
            user_email: The user's email address
        """
        return f"""
        To get started, I need to know which client you want to work with.
        
        1. First, I'll retrieve the list of clients available for your email ({user_email})
        2. Then you can select the client you want to work with
        
        Let me list the available clients for you...
        """
    
    @mcp.prompt()
    def select_medium() -> str:
        """Prompt for selecting a medium."""
        return """
        Now, let's choose which media platform you want to get data from.
        
        The available platforms are:
        1. Google Ads - Get data from your Google Ads campaigns
        2. Facebook Ads - Get data from your Facebook advertising
        3. Google Analytics 4 - Get analytics data from your websites
        
        Which platform would you like to work with?
        """
    
    @mcp.prompt()
    def select_accounts(client_name: str, medium_name: str) -> str:
        """
        Prompt for selecting accounts.
        
        Args:
            client_name: The name of the selected client
            medium_name: The name of the selected medium
        """
        return f"""
        Now, let's select which {medium_name} accounts you want to retrieve data from for client "{client_name}".
        
        I'll list the available accounts for you, and then you can tell me which ones you want to include.
        
        You can specify accounts by name or ID, or tell me "all accounts" if you want to include all of them.
        """
    
    @mcp.prompt()
    def facebook_data_request() -> list[base.Message]:
        """Prompt with detailed instructions for Facebook Ads data request."""
        return [
            base.UserMessage("""
            I'd like to fetch some Facebook Ads data. Here's what I need help with:
            
            1. Time Period:
               - Start date and end date in YYYY-MM-DD format
            
            2. Fields to include:
               - Common fields include: campaign_name, date_start, spend, impressions, clicks
               - You can request additional fields if needed
            """),
            
            base.AssistantMessage("""
            I'll help you fetch Facebook Ads data. Let me guide you through the process:
            
            1. First, I need to know which client you want to work with.
            
            2. Then, I'll help you select the Facebook Ads accounts you're interested in.
            
            3. Finally, we'll specify the date range and fields you want to include in your report.
            
            Let's start by selecting a client.
            """)
        ]
    
    @mcp.prompt()
    def analytics_data_request() -> list[base.Message]:
        """Prompt with detailed instructions for Google Analytics data request."""
        return [
            base.UserMessage("""
            I'd like to fetch some Google Analytics 4 data. Here's what I need help with:
            
            1. Time Period:
               - Start date and end date in YYYY-MM-DD format
            
            2. Dimensions:
               - Common dimensions include: date, sessionCampaignName, sessionSourceMedium
            
            3. Metrics:
               - Common metrics include: sessions, transactions, totalRevenue
            
            4. Campaign Filtering:
               - Whether to filter for campaigns starting with 'aw_' or 'fb_'
            """),
            
            base.AssistantMessage("""
            I'll help you fetch Google Analytics 4 data. Let me guide you through the process:
            
            1. First, I need to know which client you want to work with.
            
            2. Then, I'll help you select the Google Analytics properties you're interested in.
            
            3. Finally, we'll specify the dimensions, metrics, date range, and any filtering options you want to apply.
            
            Let's start by selecting a client.
            """)
        ]

    @mcp.prompt()
    def google_ads_data_request() -> list[base.Message]:
        """Prompt with detailed instructions for Google Ads data request."""
        return [
            base.UserMessage("""
            I'd like to fetch some Google Ads data. Here's what I need help with:
            
            1. Time Period:
            - Start date and end date in YYYY-MM-DD format
            
            2. Fields to include:
            - Campaign attributes (e.g., campaign.name, campaign.id)
            - Segments (e.g., segments.date)
            - Metrics (e.g., cost, metrics.impressions, metrics.clicks)
            
            3. Resources:
            - Which resource type to query (e.g., campaign, ad_group)
            """),
            
            base.AssistantMessage("""
            I'll help you fetch Google Ads data. Let me guide you through the process:
            
            1. First, I need to know which client you want to work with.
            
            2. Then, I'll help you select the Google Ads accounts you're interested in.
            
            3. Next, we'll determine the date range for your data.
            
            4. Finally, we'll specify the attributes, segments, metrics, and resource type for your report.
            
            Let's start by selecting a client.
            """)
        ]