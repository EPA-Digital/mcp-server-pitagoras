"""
Servicio para gestionar datos de Google Ads.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd

from api import get_google_ads_report
from models import Account, DateRange, ReportResponse

# Configuración de logging
logger = logging.getLogger(__name__)


class GoogleAdsService:
    """Servicio para obtener y procesar datos de Google Ads."""
    
    def __init__(self):
        """Inicializa el servicio de Google Ads."""
        # Mapeo de índices de las columnas en la respuesta de la API
        self.column_mapping = {
            "campaign_name": 0,
            "campaign_id": 1,
            "date": 2,
            "cost": 3,
            "impressions": 4,
            "clicks": 5,
        }
    
    async def get_campaign_performance(
        self,
        accounts: List[Account],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Obtiene el rendimiento de las campañas de Google Ads.
        
        Args:
            accounts: Lista de cuentas de Google Ads.
            start_date: Fecha de inicio del período.
            end_date: Fecha de fin del período.
            
        Returns:
            DataFrame con los datos de rendimiento de campañas.
        """
        # Preparar las cuentas en el formato requerido por la API
        formatted_accounts = [account.to_dict_for_ads_query() for account in accounts]
        
        # Crear el rango de fechas
        date_range = DateRange(start_date=start_date, end_date=end_date)
        
        try:
            # Obtener los datos
            response = await get_google_ads_report(formatted_accounts, date_range)
            
            # Procesar los datos
            return self._process_response(response)
            
        except Exception as e:
            logger.error(f"Error al obtener datos de Google Ads: {str(e)}")
            # Retornar un DataFrame vacío con las columnas esperadas
            return pd.DataFrame(columns=[
                "date", "campaign_name", "campaign_id", 
                "cost", "impressions", "clicks"
            ])
    
    def _process_response(self, response: ReportResponse) -> pd.DataFrame:
        """
        Procesa la respuesta de la API de Google Ads.
        
        Args:
            response: Respuesta de la API con los datos del reporte.
            
        Returns:
            DataFrame con los datos procesados.
        """
        # Si no hay datos, retornar un DataFrame vacío
        if not response.rows:
            return pd.DataFrame(columns=[
                "date", "campaign_name", "campaign_id", 
                "cost", "impressions", "clicks"
            ])
        
        # Obtener los nombres de columnas de los headers
        headers = [h.split('.')[-1] for h in response.headers]
        
        # Crear el DataFrame
        df = pd.DataFrame(response.rows, columns=headers)
        
        # Renombrar columnas
        column_rename = {
            'name': 'campaign_name',
            'id': 'campaign_id',
            'date': 'date',
            'cost_micros': 'cost',
            'impressions': 'impressions',
            'clicks': 'clicks'
        }
        
        df = df.rename(columns=column_rename)
        
        # Convertir tipos de datos
        df['date'] = pd.to_datetime(df['date'])
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce') / 1000000  # Convertir micros a unidades
        df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce')
        df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce')
        
        return df
    
    async def get_performance_summary(
        self,
        accounts: List[Account],
        days: int = 30
    ) -> Dict:
        """
        Obtiene un resumen del rendimiento de Google Ads para el período especificado.
        
        Args:
            accounts: Lista de cuentas de Google Ads.
            days: Número de días para el período (por defecto 30).
            
        Returns:
            Diccionario con el resumen del rendimiento.
        """
        # Calcular las fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Obtener los datos
        df = await self.get_campaign_performance(accounts, start_date, end_date)
        
        if df.empty:
            return {
                "period": f"Últimos {days} días",
                "total_cost": 0,
                "total_impressions": 0,
                "total_clicks": 0,
                "avg_ctr": 0,
                "avg_cpc": 0,
                "campaigns": [],
                "error": "No hay datos disponibles para el período seleccionado."
            }
        
        # Calcular métricas adicionales
        df['ctr'] = df['clicks'] / df['impressions'] * 100
        df['cpc'] = df['cost'] / df['clicks'].replace(0, float('nan'))
        
        # Calcular totales
        total_cost = df['cost'].sum()
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        
        # Calcular promedios ponderados para CTR y CPC
        avg_ctr = (df['clicks'].sum() / df['impressions'].sum() * 100) if df['impressions'].sum() > 0 else 0
        avg_cpc = (df['cost'].sum() / df['clicks'].sum()) if df['clicks'].sum() > 0 else 0
        
        # Agrupar por campaña
        campaign_summary = df.groupby('campaign_name').agg({
            'cost': 'sum',
            'impressions': 'sum',
            'clicks': 'sum'
        }).reset_index()
        
        # Calcular CTR y CPC por campaña
        campaign_summary['ctr'] = campaign_summary['clicks'] / campaign_summary['impressions'] * 100
        campaign_summary['cpc'] = campaign_summary['cost'] / campaign_summary['clicks'].replace(0, float('nan'))
        
        # Ordenar por costo (de mayor a menor)
        campaign_summary = campaign_summary.sort_values('cost', ascending=False)
        
        # Convertir a lista de diccionarios
        campaigns = campaign_summary.to_dict('records')
        
        return {
            "period": f"{start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}",
            "total_cost": total_cost,
            "total_impressions": int(total_impressions),
            "total_clicks": int(total_clicks),
            "avg_ctr": avg_ctr,
            "avg_cpc": avg_cpc,
            "campaigns": campaigns
        }