"""
Servicio para gestionar datos de Google Analytics 4.
"""

import logging
import time
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd

from api import (
    get_analytics_channel_report,
    get_analytics_hourly_report,
    get_analytics_report,
)
from models import Account, DateRange, ReportResponse

# Configuración de logging
logger = logging.getLogger(__name__)
performance_logger = logging.getLogger("pitagoras.performance")


class GoogleAnalyticsService:
    """Servicio para obtener y procesar datos de Google Analytics 4."""
    
    def __init__(self):
        """Inicializa el servicio de Google Analytics."""
        # Mapeo de índices de las columnas en la respuesta de la API
        self.column_mapping = {
            "date": 0,
            "campaign_name": 1,
            "source_medium": 2,
            "sessions": 3,
            "transactions": 4,
            "revenue": 5,
        }
    
    async def get_campaign_performance(
        self,
        accounts: List[Account],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Obtiene el rendimiento de campañas desde Google Analytics.
        
        Args:
            accounts: Lista de cuentas de Google Analytics.
            start_date: Fecha de inicio del período.
            end_date: Fecha de fin del período.
            
        Returns:
            DataFrame con los datos de rendimiento de campañas.
        """
        # Preparar las cuentas en el formato requerido por la API
        formatted_accounts = [account.to_dict_for_ga_query() for account in accounts]
        
        # Crear el rango de fechas
        date_range = DateRange(start_date=start_date, end_date=end_date)
        
        start_time = time.time()
        try:
            logger.info(f"Obteniendo datos de campañas de Google Analytics para {len(accounts)} cuentas - Período: {start_date} a {end_date}")
            
            # Obtener los datos con filtro para campañas pagadas
            response = await get_analytics_report(
                accounts=formatted_accounts,
                date_range=date_range,
                include_campaign_filter=True
            )
            
            # Medir tiempo de respuesta
            elapsed = time.time() - start_time
            performance_logger.info(f"Google Analytics API - get_campaign_performance - {len(accounts)} cuentas - {elapsed:.2f}s")
            
            # Procesar los datos
            df = self._process_campaign_response(response)
            logger.info(f"Procesados {len(df)} registros de campañas de Google Analytics")
            return df
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = f"Error al obtener datos de campañas de Google Analytics: {str(e)}"
            logger.error(error_msg)
            performance_logger.error(f"Google Analytics API - ERROR - {elapsed:.2f}s - {error_msg}")
            
            # Retornar un DataFrame vacío con las columnas esperadas
            return pd.DataFrame(columns=[
                "date", "campaign_name", "source_medium", 
                "sessions", "transactions", "revenue"
            ])
    
    def _process_campaign_response(self, response: ReportResponse) -> pd.DataFrame:
        """
        Procesa la respuesta de la API de Google Analytics para campañas.
        
        Args:
            response: Respuesta de la API con los datos del reporte.
            
        Returns:
            DataFrame con los datos procesados.
        """
        # Si no hay datos, retornar un DataFrame vacío
        if not response.rows:
            return pd.DataFrame(columns=[
                "date", "campaign_name", "source_medium", 
                "sessions", "transactions", "revenue"
            ])
        
        # Crear el DataFrame
        df = pd.DataFrame(response.rows, columns=response.headers)
        
        # Renombrar columnas
        column_rename = {
            'date': 'date',
            'sessionCampaignName': 'campaign_name',
            'sessionSourceMedium': 'source_medium',
            'sessions': 'sessions',
            'transactions': 'transactions',
            'totalRevenue': 'revenue'
        }
        
        df = df.rename(columns=column_rename)
        
        # Convertir tipos de datos
        df['date'] = pd.to_datetime(df['date'])
        df['sessions'] = pd.to_numeric(df['sessions'], errors='coerce')
        df['transactions'] = pd.to_numeric(df['transactions'], errors='coerce')
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
        
        # Agregar columnas derivadas
        df['conversion_rate'] = (df['transactions'] / df['sessions'] * 100).fillna(0)
        df['aov'] = (df['revenue'] / df['transactions']).fillna(0)  # Average Order Value
        
        return df
    
    async def get_channel_performance(
        self,
        accounts: List[Account],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Obtiene el rendimiento por canal de Google Analytics.
        
        Args:
            accounts: Lista de cuentas de Google Analytics.
            start_date: Fecha de inicio del período.
            end_date: Fecha de fin del período.
            
        Returns:
            DataFrame con los datos de rendimiento por canal.
        """
        # Preparar las cuentas
        formatted_accounts = [account.to_dict_for_ga_query() for account in accounts]
        
        # Crear el rango de fechas
        date_range = DateRange(start_date=start_date, end_date=end_date)
        
        start_time = time.time()
        try:
            logger.info(f"Obteniendo datos de canales de Google Analytics para {len(accounts)} cuentas - Período: {start_date} a {end_date}")
            
            # Obtener los datos
            response = await get_analytics_channel_report(
                accounts=formatted_accounts,
                date_range=date_range
            )
            
            # Medir tiempo de respuesta
            elapsed = time.time() - start_time
            performance_logger.info(f"Google Analytics API - get_channel_performance - {len(accounts)} cuentas - {elapsed:.2f}s")
            
            # Procesar los datos
            df = self._process_channel_response(response)
            logger.info(f"Procesados {len(df)} registros de canales de Google Analytics")
            return df
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = f"Error al obtener datos de canales de Google Analytics: {str(e)}"
            logger.error(error_msg)
            performance_logger.error(f"Google Analytics API - ERROR - {elapsed:.2f}s - {error_msg}")
            
            # Retornar un DataFrame vacío
            return pd.DataFrame(columns=[
                "channel", "sessions", "conversions", "transactions", "revenue", 
                "conversion_rate", "aov"
            ])
    
    def _process_channel_response(self, response: ReportResponse) -> pd.DataFrame:
        """
        Procesa la respuesta de la API de Google Analytics para canales.
        
        Args:
            response: Respuesta de la API con los datos del reporte.
            
        Returns:
            DataFrame con los datos procesados.
        """
        # Si no hay datos, retornar un DataFrame vacío
        if not response.rows:
            return pd.DataFrame(columns=[
                "channel", "sessions", "conversions", "transactions", "revenue", 
                "conversion_rate", "aov"
            ])
        
        # Crear el DataFrame
        df = pd.DataFrame(response.rows, columns=response.headers)
        
        # Renombrar columnas
        column_rename = {
            'sessionDefaultChannelGroup': 'channel',
            'sessions': 'sessions',
            'conversions': 'conversions',
            'ecommercePurchases': 'transactions',
            'purchaseRevenue': 'revenue'
        }
        
        df = df.rename(columns=column_rename)
        
        # Convertir tipos de datos
        df['sessions'] = pd.to_numeric(df['sessions'], errors='coerce')
        df['conversions'] = pd.to_numeric(df['conversions'], errors='coerce')
        df['transactions'] = pd.to_numeric(df['transactions'], errors='coerce')
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
        
        # Agregar columnas derivadas
        df['conversion_rate'] = (df['transactions'] / df['sessions'] * 100).fillna(0)
        df['aov'] = (df['revenue'] / df['transactions']).fillna(0)  # Average Order Value
        
        return df
    
    async def get_hourly_performance(
        self,
        accounts: List[Account],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Obtiene el rendimiento por hora del día de Google Analytics.
        
        Args:
            accounts: Lista de cuentas de Google Analytics.
            start_date: Fecha de inicio del período.
            end_date: Fecha de fin del período.
            
        Returns:
            DataFrame con los datos de rendimiento por hora.
        """
        # Preparar las cuentas
        formatted_accounts = [account.to_dict_for_ga_query() for account in accounts]
        
        # Crear el rango de fechas
        date_range = DateRange(start_date=start_date, end_date=end_date)
        
        start_time = time.time()
        try:
            logger.info(f"Obteniendo datos por hora de Google Analytics para {len(accounts)} cuentas - Período: {start_date} a {end_date}")
            
            # Obtener los datos
            response = await get_analytics_hourly_report(
                accounts=formatted_accounts,
                date_range=date_range
            )
            
            # Medir tiempo de respuesta
            elapsed = time.time() - start_time
            performance_logger.info(f"Google Analytics API - get_hourly_performance - {len(accounts)} cuentas - {elapsed:.2f}s")
            
            # Procesar los datos
            df = self._process_hourly_response(response)
            logger.info(f"Procesados {len(df)} registros de datos por hora de Google Analytics")
            return df
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = f"Error al obtener datos por hora de Google Analytics: {str(e)}"
            logger.error(error_msg)
            performance_logger.error(f"Google Analytics API - ERROR - {elapsed:.2f}s - {error_msg}")
            
            # Retornar un DataFrame vacío
            return pd.DataFrame(columns=[
                "hour", "sessions", "conversions", "transactions", "revenue", 
                "conversion_rate", "aov"
            ])
    
    def _process_hourly_response(self, response: ReportResponse) -> pd.DataFrame:
        """
        Procesa la respuesta de la API de Google Analytics para datos por hora.
        
        Args:
            response: Respuesta de la API con los datos del reporte.
            
        Returns:
            DataFrame con los datos procesados.
        """
        # Si no hay datos, retornar un DataFrame vacío
        if not response.rows:
            return pd.DataFrame(columns=[
                "hour", "sessions", "conversions", "transactions", "revenue", 
                "conversion_rate", "aov"
            ])
        
        # Crear el DataFrame
        df = pd.DataFrame(response.rows, columns=response.headers)
        
        # Renombrar columnas
        column_rename = {
            'hour': 'hour',
            'sessions': 'sessions',
            'conversions': 'conversions',
            'ecommercePurchases': 'transactions',
            'purchaseRevenue': 'revenue'
        }
        
        df = df.rename(columns=column_rename)
        
        # Convertir tipos de datos
        df['hour'] = pd.to_numeric(df['hour'], errors='coerce')
        df['sessions'] = pd.to_numeric(df['sessions'], errors='coerce')
        df['conversions'] = pd.to_numeric(df['conversions'], errors='coerce')
        df['transactions'] = pd.to_numeric(df['transactions'], errors='coerce')
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
        
        # Agregar columnas derivadas
        df['conversion_rate'] = (df['transactions'] / df['sessions'] * 100).fillna(0)
        df['aov'] = (df['revenue'] / df['transactions']).fillna(0)
        
        return df
    
    async def get_analytics_summary(
        self,
        accounts: List[Account],
        days: int = 30
    ) -> Dict:
        """
        Obtiene un resumen de los datos de Google Analytics.
        
        Args:
            accounts: Lista de cuentas de Google Analytics.
            days: Número de días para el período (por defecto 30).
            
        Returns:
            Diccionario con el resumen de los datos de Analytics.
        """
        start_time = time.time()
        logger.info(f"Generando resumen de Analytics para {len(accounts)} cuentas - Período: {days} días")
        
        # Calcular las fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Obtener los datos
        campaign_df = await self.get_campaign_performance(accounts, start_date, end_date)
        channel_df = await self.get_channel_performance(accounts, start_date, end_date)
        hourly_df = await self.get_hourly_performance(accounts, start_date, end_date)
        
        # Medir tiempo total
        elapsed = time.time() - start_time
        performance_logger.info(f"Analytics Summary - {len(accounts)} cuentas - {days} días - {elapsed:.2f}s")
        
        # Si no hay datos, retornar un resumen básico
        if campaign_df.empty and channel_df.empty and hourly_df.empty:
            return {
                "period": f"Últimos {days} días",
                "total_sessions": 0,
                "total_transactions": 0,
                "total_revenue": 0,
                "conversion_rate": 0,
                "channels": [],
                "hourly_performance": [],
                "error": "No hay datos disponibles para el período seleccionado."
            }
        
        # Preparar resumen de campañas
        campaign_summary = {}
        if not campaign_df.empty:
            # Calcular totales
            total_sessions = campaign_df['sessions'].sum()
            total_transactions = campaign_df['transactions'].sum()
            total_revenue = campaign_df['revenue'].sum()
            
            # Calcular tasa de conversión
            conversion_rate = (total_transactions / total_sessions * 100) if total_sessions > 0 else 0
            
            campaign_summary = {
                "total_sessions": int(total_sessions),
                "total_transactions": int(total_transactions),
                "total_revenue": float(total_revenue),
                "conversion_rate": float(conversion_rate)
            }
        else:
            campaign_summary = {
                "total_sessions": 0,
                "total_transactions": 0,
                "total_revenue": 0,
                "conversion_rate": 0
            }
        
        # Preparar resumen de canales
        channel_summary = []
        if not channel_df.empty:
            # Ordenar por sesiones (de mayor a menor)
            channel_df = channel_df.sort_values('sessions', ascending=False)
            
            # Convertir a lista de diccionarios
            channel_summary = channel_df.to_dict('records')
        
        # Preparar resumen por hora
        hourly_summary = []
        if not hourly_df.empty:
            # Ordenar por hora
            hourly_df = hourly_df.sort_values('hour')
            
            # Convertir a lista de diccionarios
            hourly_summary = hourly_df.to_dict('records')
        
        # Combinar todos los resúmenes
        return {
            "period": f"{start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}",
            **campaign_summary,
            "channels": channel_summary,
            "hourly_performance": hourly_summary
        }