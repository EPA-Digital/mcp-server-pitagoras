# server/resources.py
from mcp.server.fastmcp import FastMCP
from pitagoras.api import get_customers


async def register_resources(mcp: FastMCP):
    """Register all MCP resources"""
    
    @mcp.resource("pitagoras://customers")
    async def list_customers() -> str:
        """Get list of all available customers"""
        customers = await get_customers()
        formatted_customers = []
        
        for customer in customers:
            customer_info = f"- ID: {customer['ID']}\n  Name: {customer['name']}\n  Status: {customer['status']}"
            formatted_customers.append(customer_info)
        
        return "\n".join(formatted_customers)
    
    @mcp.resource("pitagoras://customer/{customer_id}/accounts")
    async def get_customer_accounts(customer_id: str) -> str:
        """Get all accounts for a specific customer"""
        customers = await get_customers()
        
        for customer in customers:
            if customer["ID"] == customer_id:
                accounts = customer.get("accounts", [])
                formatted_accounts = []
                
                for account in accounts:
                    account_info = [
                        f"- ID: {account.get('accountID', 'N/A')}",
                        f"  Name: {account.get('name', 'N/A')}",
                        f"  Provider: {account.get('provider', 'N/A')}",
                    ]
                    
                    if "externalLoginCustomerID" in account:
                        account_info.append(f"  Login Customer ID: {account['externalLoginCustomerID']}")
                    
                    if "credentialEmail" in account:
                        account_info.append(f"  Credential Email: {account['credentialEmail']}")
                    
                    formatted_accounts.append("\n".join(account_info))
                
                return "\n".join(formatted_accounts)
        
        return f"Customer with ID {customer_id} not found"