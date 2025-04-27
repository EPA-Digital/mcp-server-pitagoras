"""
Servicio para gestionar clientes y cuentas de Pitágoras.
"""

import logging
import time
from typing import Dict, List, Optional

from api import get_customers
from models import Account, Customer

# Configuración de logging
logger = logging.getLogger(__name__)
performance_logger = logging.getLogger("pitagoras.performance")


class ClientService:
    """Servicio para gestionar clientes y cuentas de Pitágoras."""
    
    def __init__(self):
        """Inicializa el servicio de clientes."""
        # Cache para evitar llamadas repetidas a la API
        self._customers_cache: List[Customer] = []
    
    async def get_customers(self, force_refresh: bool = False) -> List[Customer]:
        """
        Obtiene la lista de clientes disponibles.
        
        Args:
            force_refresh: Si se debe forzar la actualización de la caché.
            
        Returns:
            Lista de clientes.
        """
        start_time = time.time()
        
        if not self._customers_cache or force_refresh:
            try:
                logger.info("Obteniendo lista de clientes de la API de Pitágoras")
                response = await get_customers()
                self._customers_cache = response.customers
                
                # Medir tiempo de respuesta
                elapsed = time.time() - start_time
                performance_logger.info(f"API de Pitágoras - get_customers - {elapsed:.2f}s - {len(self._customers_cache)} clientes obtenidos")
                logger.info(f"Se obtuvieron {len(self._customers_cache)} clientes de Pitágoras")
            except Exception as e:
                elapsed = time.time() - start_time
                error_msg = f"Error al obtener clientes: {str(e)}"
                logger.error(error_msg)
                performance_logger.error(f"API de Pitágoras - ERROR - get_customers - {elapsed:.2f}s - {error_msg}")
                raise
        else:
            logger.debug("Usando cache de clientes (para forzar actualización use force_refresh=True)")
        
        return self._customers_cache
    
    async def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """
        Obtiene un cliente por su ID.
        
        Args:
            customer_id: ID del cliente a buscar.
            
        Returns:
            El cliente con el ID especificado, o None si no se encuentra.
        """
        customers = await self.get_customers()
        
        for customer in customers:
            if customer.ID == customer_id:
                return customer
        
        return None
    
    async def get_customer_by_name(self, name: str) -> Optional[Customer]:
        """
        Obtiene un cliente por su nombre.
        
        Args:
            name: Nombre del cliente a buscar.
            
        Returns:
            El cliente con el nombre especificado, o None si no se encuentra.
        """
        customers = await self.get_customers()
        
        for customer in customers:
            if customer.name.lower() == name.lower():
                return customer
        
        # Búsqueda parcial si no hay coincidencia exacta
        for customer in customers:
            if name.lower() in customer.name.lower():
                return customer
        
        return None
    
    async def get_accounts_by_provider(
        self, customer_id: str, provider: str
    ) -> List[Account]:
        """
        Obtiene las cuentas de un cliente para un proveedor específico.
        
        Args:
            customer_id: ID del cliente.
            provider: Nombre del proveedor (adwords, fb, analytics4).
            
        Returns:
            Lista de cuentas que corresponden al proveedor.
        """
        customer = await self.get_customer_by_id(customer_id)
        
        if not customer:
            return []
        
        return [
            account for account in customer.accounts 
            if account.provider.lower() == provider.lower()
        ]
    
    async def get_account_by_id(
        self, customer_id: str, account_id: str
    ) -> Optional[Account]:
        """
        Obtiene una cuenta específica por su ID.
        
        Args:
            customer_id: ID del cliente.
            account_id: ID de la cuenta a buscar.
            
        Returns:
            La cuenta con el ID especificado, o None si no se encuentra.
        """
        customer = await self.get_customer_by_id(customer_id)
        
        if not customer:
            return None
        
        for account in customer.accounts:
            if account.accountID == account_id:
                return account
        
        return None

    async def get_customer_summary(self, customer_id: str) -> Dict:
        """
        Obtiene un resumen del cliente incluyendo cuentas por proveedor.
        
        Args:
            customer_id: ID del cliente.
            
        Returns:
            Diccionario con información resumida del cliente.
        """
        customer = await self.get_customer_by_id(customer_id)
        
        if not customer:
            return {"error": "Cliente no encontrado"}
        
        # Agrupar cuentas por proveedor
        accounts_by_provider = {}
        for account in customer.accounts:
            provider = account.provider
            if provider not in accounts_by_provider:
                accounts_by_provider[provider] = []
            
            accounts_by_provider[provider].append({
                "id": account.accountID,
                "name": account.name
            })
        
        return {
            "id": customer.ID,
            "name": customer.name,
            "status": customer.status,
            "accounts_by_provider": accounts_by_provider,
            "total_accounts": len(customer.accounts)
        }