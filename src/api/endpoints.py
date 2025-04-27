"""
Definiciones de endpoints para interactuar con la API de Pitágoras.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Union

from api.client import PitagorasClient
from config import (
    ADWORDS_REPORT_ENDPOINT,
    ANALYTICS4_REPORT_ENDPOINT,
    CUSTOMERS_ENDPOINT,
    DEFAULT_USER_EMAIL,
    FACEBOOK_REPORT_ENDPOINT,
)
from models import (
    CustomerResponse,
    DateRange,
    FacebookQuery,
    GoogleAdsQuery,
    GoogleAnalyticsQuery,
    ReportResponse,
)


async def get_customers(user_email: str = DEFAULT_USER_EMAIL) -> CustomerResponse:
    """
    Obtiene la lista de clientes disponibles para el usuario.
    
    Args:
        user_email: Email del usuario para el que se obtendrán los clientes.
        
    Returns:
        Respuesta con la lista de clientes y sus cuentas.
    """
    client = PitagorasClient()
    data = {"user_email": user_email}
    return await client.post(CUSTOMERS_ENDPOINT, data, CustomerResponse)


async def get_google_ads_report(
    accounts: List[Dict[str, str]],
    date_range: DateRange,
    include_campaigns: bool = True,
) -> ReportResponse:
    """
    Obtiene un reporte de Google Ads.
    
    Args:
        accounts: Lista de cuentas para las que obtener datos.
        date_range: Rango de fechas para el reporte.
        include_campaigns: Si se deben incluir datos a nivel de campaña.
        
    Returns:
        Respuesta con los datos del reporte.
    """
    client = PitagorasClient()
    
    # Construir la consulta
    query = GoogleAdsQuery(
        accounts=accounts,
        attributes=[
            {
                "resource_name": "campaign",
                "fields": ["campaign.name", "campaign.id"]
            }
        ],
        segments=["segments.date"],
        metrics=[
            "metrics.cost_micros",
            "metrics.impressions",
            "metrics.clicks",
        ],
        resource="campaign",
        start_date=date_range.start_date.strftime("%Y-%m-%d"),
        end_date=date_range.end_date.strftime("%Y-%m-%d"),
    )
    
    return await client.post(ADWORDS_REPORT_ENDPOINT, query.model_dump(), ReportResponse)


async def get_facebook_report(
    customer_id: str,
    accounts: List[Dict[str, str]],
    date_range: DateRange,
    account_ids: Optional[List[str]] = None,
) -> ReportResponse:
    """
    Obtiene un reporte de Facebook Ads.
    
    Args:
        customer_id: ID del cliente.
        accounts: Lista de cuentas para las que obtener datos.
        date_range: Rango de fechas para el reporte.
        account_ids: IDs de las cuentas (opcional, si no se proporciona se extraen de accounts).
        
    Returns:
        Respuesta con los datos del reporte.
    """
    client = PitagorasClient()
    
    if account_ids is None:
        account_ids = [acc.get("account_id", "") for acc in accounts]
    
    # Construir la consulta
    query = FacebookQuery(
        customer=customer_id,
        parsed_accounts=accounts,
        accounts=account_ids,
        date_range=date_range.to_fb_format(),
        fields=[
            "campaign_name",
            "date_start",
            "spend",
            "impressions",
            "clicks",
        ],
    )
    
    return await client.post(FACEBOOK_REPORT_ENDPOINT, query.model_dump(), ReportResponse)


async def get_analytics_report(
    accounts: List[Dict[str, str]],
    date_range: DateRange,
    include_campaign_filter: bool = True,
) -> ReportResponse:
    """
    Obtiene un reporte de Google Analytics 4.
    
    Args:
        accounts: Lista de cuentas para las que obtener datos.
        date_range: Rango de fechas para el reporte.
        include_campaign_filter: Si se debe aplicar un filtro para campañas.
        
    Returns:
        Respuesta con los datos del reporte.
    """
    client = PitagorasClient()
    
    # Filtro para incluir solo campañas de Google Ads y Facebook
    campaign_filter = {
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
    } if include_campaign_filter else None
    
    # Construir la consulta
    query = GoogleAnalyticsQuery(
        accounts=accounts,
        dimensions=[
            "date",
            "sessionCampaignName",
            "sessionSourceMedium",
        ],
        metrics=[
            "sessions",
            "transactions",
            "totalRevenue",
        ],
        start_date=date_range.start_date.strftime("%Y-%m-%d"),
        end_date=date_range.end_date.strftime("%Y-%m-%d"),
        filters=campaign_filter,
    )
    
    return await client.post(ANALYTICS4_REPORT_ENDPOINT, query.model_dump(), ReportResponse)


async def get_analytics_channel_report(
    accounts: List[Dict[str, str]],
    date_range: DateRange,
) -> ReportResponse:
    """
    Obtiene un reporte de canales de Google Analytics 4.
    
    Args:
        accounts: Lista de cuentas para las que obtener datos.
        date_range: Rango de fechas para el reporte.
        
    Returns:
        Respuesta con los datos del reporte.
    """
    client = PitagorasClient()
    
    # Construir la consulta
    query = GoogleAnalyticsQuery(
        accounts=accounts,
        dimensions=[
            "sessionDefaultChannelGroup",
        ],
        metrics=[
            "sessions",
            "conversions",
            "ecommercePurchases",
            "purchaseRevenue",
        ],
        start_date=date_range.start_date.strftime("%Y-%m-%d"),
        end_date=date_range.end_date.strftime("%Y-%m-%d"),
    )
    
    return await client.post(ANALYTICS4_REPORT_ENDPOINT, query.model_dump(), ReportResponse)


async def get_analytics_hourly_report(
    accounts: List[Dict[str, str]],
    date_range: DateRange,
) -> ReportResponse:
    """
    Obtiene un reporte por hora del día de Google Analytics 4.
    
    Args:
        accounts: Lista de cuentas para las que obtener datos.
        date_range: Rango de fechas para el reporte.
        
    Returns:
        Respuesta con los datos del reporte.
    """
    client = PitagorasClient()
    
    # Construir la consulta
    query = GoogleAnalyticsQuery(
        accounts=accounts,
        dimensions=[
            "hour",
        ],
        metrics=[
            "sessions",
            "conversions",
            "ecommercePurchases",
            "purchaseRevenue",
        ],
        start_date=date_range.start_date.strftime("%Y-%m-%d"),
        end_date=date_range.end_date.strftime("%Y-%m-%d"),
    )
    
    return await client.post(ANALYTICS4_REPORT_ENDPOINT, query.model_dump(), ReportResponse)