"""
Servicio para gestionar datos de Facebook Ads.
"""

import logging
import time
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd

from api import get_facebook_report
from models import Account, DateRange, ReportResponse

# Configuración de logging
logger = logging.getLogger(__name__)
performance_logger = logging.getLogger("pitagoras.performance")


class FacebookAdsService:
    """Servicio para obtener y procesar datos de Facebook Ads."""
    
    def __init__(self):
        """Inicializa el servicio de Facebook Ads."""
        # Mapeo de índices de las columnas en la respuesta de la API
        self.column_mapping = {
            "campaign_name": 0,
            "date": 1,
            "spend": 2,
            "impressions": 3,
            "clicks": 4,
        }
    
    async def get_campaign_performance(
        self,
        customer_id: str,
        accounts: List[Account],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Obtiene el rendimiento de las campañas de Facebook Ads.
        
        Args:
            customer_id: ID del cliente.
            accounts: Lista de cuentas de Facebook Ads.
            start_date: Fecha de inicio del período.
            end_date: Fecha de fin del período.
            
        Returns:
            DataFrame con los datos de rendimiento de campañas.
        """
        # Preparar las cuentas en el formato requerido por la API
        formatted_accounts = [account.to_dict_for_fb_query() for account in accounts]
        account_ids = [account.accountID for account in accounts]
        
        # Crear el rango de fechas
        date_range = DateRange(start_date=start_date, end_date=end_date)
        
        start_time = time.time()
        try:
            logger.info(f"Obteniendo datos de Facebook Ads para {len(accounts)} cuentas - Cliente: {customer_id} - Período: {start_date} a {end_date}")
            
            # Obtener los datos
            response = await get_facebook_report(
                customer_id=customer_id,
                accounts=formatted_accounts,
                date_range=date_range,
                account_ids=account_ids
            )
            
            # Medir tiempo de respuesta
            elapsed = time.time() - start_time
            performance_logger.info(f"Facebook Ads API - get_campaign_performance - Cliente: {customer_id} - {len(accounts)} cuentas - {elapsed:.2f}s")
            
            # Procesar los datos
            df = self._process_response(response)
            logger.info(f"Procesados {len(df)} registros de campañas de Facebook Ads")
            return df
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = f"Error al obtener datos de Facebook Ads: {str(e)}"
            logger.error(error_msg)
            performance_logger.error(f"Facebook Ads API - ERROR - Cliente: {customer_id} - {elapsed:.2f}s - {error_msg}")
            
            # Retornar un DataFrame vacío con las columnas esperadas
            return pd.DataFrame(columns=[
                "date", "campaign_name", "spend", "impressions", "clicks"
            ])
    
    def _process_response(self, response: ReportResponse) -> pd.DataFrame:
        """
        Procesa la respuesta de la API de Facebook Ads.
        
        Args:
            response: Respuesta de la API con los datos del reporte.
            
        Returns:
            DataFrame con los datos procesados.
        """
        # Si no hay datos, retornar un DataFrame vacío
        if not response.rows:
            return pd.DataFrame(columns=[
                "date", "campaign_name", "spend", "impressions", "clicks"
            ])
        
        # Crear el DataFrame
        df = pd.DataFrame(response.rows, columns=response.headers)
        
        # Convertir tipos de datos
        df['date_start'] = pd.to_datetime(df['date_start'])
        df['spend'] = pd.to_numeric(df['spend'], errors='coerce')
        df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce')
        df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce')
        
        # Renombrar columnas para consistencia con Google Ads
        df = df.rename(columns={
            'date_start': 'date',
            'campaign_name': 'campaign_name',
            'spend': 'cost',  # Renombrar spend a cost para consistencia
        })
        
        return df
    
    async def get_performance_summary(
        self,
        customer_id: str,
        accounts: List[Account],
        days: int = 30
    ) -> Dict:
        """
        Obtiene un resumen del rendimiento de Facebook Ads para el período especificado.
        
        Args:
            customer_id: ID del cliente.
            accounts: Lista de cuentas de Facebook Ads.
            days: Número de días para el período (por defecto 30).
            
        Returns:
            Diccionario con el resumen del rendimiento.
        """
        # Calcular las fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Obtener los datos
        df = await self.get_campaign_performance(customer_id, accounts, start_date, end_date)
        
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