"""
Esquemas y modelos de datos para el servidor MCP de Pitágoras.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Provider(str, Enum):
    """Proveedores de datos soportados."""
    
    GOOGLE_ADS = "adwords"
    FACEBOOK = "fb"
    GOOGLE_ANALYTICS = "analytics4"


class Manager(BaseModel):
    """Información del administrador de la cuenta."""
    
    name: str
    userID: str


class Account(BaseModel):
    """Modelo para una cuenta de publicidad."""
    
    accountID: str
    name: str 
    provider: str
    businessUnit: Optional[str] = None
    clientName: Optional[str] = None
    credentialEmail: Optional[str] = None
    currency: Optional[str] = None
    externalLoginCustomerID: Optional[str] = None
    manager: Optional[Manager] = None
    objective: Optional[str] = None
    postgresID: Optional[int] = None
    timezone: Optional[str] = None
    vertical: Optional[str] = None
    
    def to_dict_for_ads_query(self) -> Dict[str, str]:
        """Convierte la cuenta a formato para consulta de Adwords."""
        return {
            "account_id": self.accountID,
            "name": self.name,
            "login_customer_id": self.externalLoginCustomerID or ""
        }
    
    def to_dict_for_fb_query(self) -> Dict[str, str]:
        """Convierte la cuenta a formato para consulta de Facebook."""
        return {
            "name": self.name,
            "account_id": self.accountID
        }
        
    def to_dict_for_ga_query(self) -> Dict[str, str]:
        """Convierte la cuenta a formato para consulta de Google Analytics."""
        return {
            "property_id": self.accountID,
            "name": self.name,
            "credential_email": self.credentialEmail or "analytics@epa.digital"
        }


class Customer(BaseModel):
    """Modelo para un cliente."""
    
    ID: str
    name: str
    accounts: List[Account]
    status: Optional[str] = None
    postgresID: Optional[int] = None


class CustomerResponse(BaseModel):
    """Respuesta de la API con lista de clientes."""
    
    customers: List[Customer]
    token: str


class DateRange(BaseModel):
    """Rango de fechas para consultas."""
    
    start_date: date
    end_date: date
    
    def to_fb_format(self) -> Dict[str, str]:
        """Convierte a formato para API de Facebook."""
        return {
            "start": self.start_date.strftime("%Y-%m-%d"),
            "end": self.end_date.strftime("%Y-%m-%d")
        }


class ReportResponse(BaseModel):
    """Respuesta de la API con datos de reporte."""
    
    headers: List[str]
    rows: List[List[Any]]
    errors: List[Any] = []


class GoogleAdsQuery(BaseModel):
    """Modelo para la consulta a Google Ads."""
    
    accounts: List[Dict[str, str]]
    attributes: List[Dict[str, Union[str, List[str]]]]
    segments: List[str]
    metrics: List[str]
    resource: str
    start_date: str
    end_date: str


class FacebookQuery(BaseModel):
    """Modelo para la consulta a Facebook Ads."""
    
    provider: str = "fb"
    customer: str
    query_name: str = "data_fb"
    parsed_accounts: List[Dict[str, str]]
    accounts: List[str]
    date_range: Dict[str, str]
    fields: List[str]
    preset_date: Optional[Dict[str, Union[str, int]]] = None


class GoogleAnalyticsQuery(BaseModel):
    """Modelo para la consulta a Google Analytics."""
    
    accounts: List[Dict[str, str]]
    dimensions: List[str]
    metrics: List[str]
    start_date: str
    end_date: str
    filters: Optional[Dict[str, Any]] = None


class CombinedCampaignData(BaseModel):
    """Modelo para datos combinados de campañas."""
    
    date: str
    campaign_name: str
    source_medium: str
    platform: str
    cost: float = 0
    impressions: int = 0
    clicks: int = 0
    sessions: int = 0
    transactions: int = 0
    revenue: float = 0
    roas: float = 0
    cr: float = 0


class ChannelPerformance(BaseModel):
    """Modelo para rendimiento por canal."""
    
    channel: str
    sessions: int = 0
    conversion_rate: float = 0
    aov: float = 0
    transactions: int = 0
    revenue: float = 0


class HourlyPerformance(BaseModel):
    """Modelo para rendimiento por hora."""
    
    hour: int
    sessions: int = 0
    conversion_rate: float = 0
    aov: float = 0
    transactions: int = 0
    revenue: float = 0