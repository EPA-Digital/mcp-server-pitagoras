"""
Servicio para combinar y analizar datos de múltiples fuentes.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import BytesIO
import base64

from models import Account, ChannelPerformance, CombinedCampaignData, Customer, HourlyPerformance
from services.adwords import GoogleAdsService
from services.analytics import GoogleAnalyticsService
from services.clients import ClientService
from services.facebook import FacebookAdsService

# Configuración de logging
logger = logging.getLogger(__name__)


class AnalysisService:
    """Servicio para combinar y analizar datos de diferentes plataformas."""
    
    def __init__(self):
        """Inicializa el servicio de análisis."""
        self.client_service = ClientService()
        self.google_ads_service = GoogleAdsService()
        self.facebook_ads_service = FacebookAdsService()
        self.analytics_service = GoogleAnalyticsService()
    
    async def get_combined_campaign_performance(
        self,
        customer_id: str,
        google_ads_accounts: List[Account],
        facebook_accounts: List[Account],
        analytics_accounts: List[Account],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Combina datos de rendimiento de campañas de múltiples plataformas.
        
        Args:
            customer_id: ID del cliente.
            google_ads_accounts: Lista de cuentas de Google Ads.
            facebook_accounts: Lista de cuentas de Facebook Ads.
            analytics_accounts: Lista de cuentas de Google Analytics.
            start_date: Fecha de inicio del período.
            end_date: Fecha de fin del período.
            
        Returns:
            DataFrame con los datos combinados de rendimiento de campañas.
        """
        # Obtener datos de cada plataforma
        ads_df = await self.google_ads_service.get_campaign_performance(
            google_ads_accounts, start_date, end_date
        )
        
        fb_df = await self.facebook_ads_service.get_campaign_performance(
            customer_id, facebook_accounts, start_date, end_date
        )
        
        ga_df = await self.analytics_service.get_campaign_performance(
            analytics_accounts, start_date, end_date
        )
        
        # Añadir columna de plataforma a cada DataFrame
        if not ads_df.empty:
            ads_df['platform'] = 'google_ads'
        
        if not fb_df.empty:
            fb_df['platform'] = 'facebook'
        
        # Combinar datos de costos (Google Ads y Facebook)
        cost_df = pd.DataFrame()
        if not ads_df.empty:
            cost_df = pd.concat([cost_df, ads_df])
        
        if not fb_df.empty:
            cost_df = pd.concat([cost_df, fb_df])
        
        if cost_df.empty:
            # Si no hay datos de costos, crear un DataFrame con estructura básica
            cost_df = pd.DataFrame(columns=[
                'date', 'campaign_name', 'platform', 'cost', 'impressions', 'clicks'
            ])
        
        # Si no hay datos de Analytics, crear un DataFrame con estructura básica
        if ga_df.empty:
            ga_df = pd.DataFrame(columns=[
                'date', 'campaign_name', 'source_medium', 'sessions', 
                'transactions', 'revenue', 'conversion_rate', 'aov'
            ])
        
        # Combinar datos de costos con datos de Analytics
        # Primero asegurarse de que 'date' tenga el mismo tipo en ambos DataFrames
        if 'date' in cost_df.columns and 'date' in ga_df.columns:
            cost_df['date'] = pd.to_datetime(cost_df['date']).dt.date
            ga_df['date'] = pd.to_datetime(ga_df['date']).dt.date
        
        # Realizar la combinación
        combined_df = pd.merge(
            cost_df,
            ga_df,
            how='outer',
            left_on=['date', 'campaign_name'],
            right_on=['date', 'campaign_name']
        )
        
        # Llenar valores nulos con 0
        combined_df = combined_df.fillna(0)
        
        # Calcular métricas derivadas
        combined_df['roas'] = combined_df['revenue'] / combined_df['cost']
        combined_df['roas'] = combined_df['roas'].replace([np.inf, -np.inf], 0)
        
        combined_df['cr'] = combined_df['transactions'] / combined_df['sessions'] * 100
        combined_df['cr'] = combined_df['cr'].replace([np.inf, -np.inf], 0)
        
        return combined_df
    
    async def get_campaign_performance_summary(
        self,
        customer_id: str,
        days: int = 30
    ) -> Dict:
        """
        Obtiene un resumen combinado del rendimiento de campañas para el período especificado.
        
        Args:
            customer_id: ID del cliente.
            days: Número de días para el período (por defecto 30).
            
        Returns:
            Diccionario con el resumen del rendimiento.
        """
        # Obtener cliente y cuentas
        customer = await self.client_service.get_customer_by_id(customer_id)
        
        if not customer:
            return {
                "error": f"Cliente con ID {customer_id} no encontrado."
            }
        
        # Obtener cuentas por plataforma
        google_ads_accounts = [
            account for account in customer.accounts 
            if account.provider.lower() == 'adwords'
        ]
        
        facebook_accounts = [
            account for account in customer.accounts 
            if account.provider.lower() == 'fb'
        ]
        
        analytics_accounts = [
            account for account in customer.accounts 
            if account.provider.lower() in ['analytics4']
        ]
        
        # Calcular fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Obtener datos combinados
        combined_df = await self.get_combined_campaign_performance(
            customer_id, 
            google_ads_accounts,
            facebook_accounts,
            analytics_accounts,
            start_date,
            end_date
        )
        
        if combined_df.empty:
            return {
                "customer": customer.name,
                "period": f"Últimos {days} días",
                "total_cost": 0,
                "total_revenue": 0,
                "total_roas": 0,
                "total_sessions": 0,
                "total_transactions": 0,
                "total_cr": 0,
                "campaigns": [],
                "error": "No hay datos disponibles para el período seleccionado."
            }
        
        # Calcular totales
        total_cost = combined_df['cost'].sum()
        total_revenue = combined_df['revenue'].sum()
        total_sessions = combined_df['sessions'].sum()
        total_transactions = combined_df['transactions'].sum()
        
        # Calcular métricas derivadas
        total_roas = total_revenue / total_cost if total_cost > 0 else 0
        total_cr = total_transactions / total_sessions * 100 if total_sessions > 0 else 0
        
        # Agrupar por campaña
        campaign_summary = combined_df.groupby('campaign_name').agg({
            'cost': 'sum',
            'revenue': 'sum',
            'sessions': 'sum',
            'transactions': 'sum',
            'platform': 'first'  # Para identificar la plataforma principal
        }).reset_index()
        
        # Calcular ROAS y CR por campaña
        campaign_summary['roas'] = campaign_summary['revenue'] / campaign_summary['cost']
        campaign_summary['roas'] = campaign_summary['roas'].replace([np.inf, -np.inf], 0)
        
        campaign_summary['cr'] = campaign_summary['transactions'] / campaign_summary['sessions'] * 100
        campaign_summary['cr'] = campaign_summary['cr'].replace([np.inf, -np.inf], 0)
        
        # Ordenar por costo (de mayor a menor)
        campaign_summary = campaign_summary.sort_values('cost', ascending=False)
        
        # Convertir a lista de diccionarios
        campaigns = campaign_summary.to_dict('records')
        
        return {
            "customer": customer.name,
            "period": f"{start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}",
            "total_cost": total_cost,
            "total_revenue": total_revenue,
            "total_roas": total_roas,
            "total_sessions": int(total_sessions),
            "total_transactions": int(total_transactions),
            "total_cr": total_cr,
            "campaigns": campaigns
        }
    
    async def get_channel_performance_summary(
        self,
        customer_id: str,
        days: int = 30
    ) -> Dict:
        """
        Obtiene un resumen del rendimiento por canal para el período especificado.
        
        Args:
            customer_id: ID del cliente.
            days: Número de días para el período (por defecto 30).
            
        Returns:
            Diccionario con el resumen del rendimiento por canal.
        """
        # Obtener cliente y cuentas de Analytics
        customer = await self.client_service.get_customer_by_id(customer_id)
        
        if not customer:
            return {
                "error": f"Cliente con ID {customer_id} no encontrado."
            }
        
        analytics_accounts = [
            account for account in customer.accounts 
            if account.provider.lower() in ['analytics4']
        ]
        
        if not analytics_accounts:
            return {
                "customer": customer.name,
                "error": "No se encontraron cuentas de Google Analytics para este cliente."
            }
        
        # Calcular fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Obtener resumen de Analytics
        ga_summary = await self.analytics_service.get_analytics_summary(
            analytics_accounts, days
        )
        
        return {
            "customer": customer.name,
            "period": ga_summary.get("period", f"Últimos {days} días"),
            "total_sessions": ga_summary.get("total_sessions", 0),
            "total_transactions": ga_summary.get("total_transactions", 0),
            "total_revenue": ga_summary.get("total_revenue", 0),
            "conversion_rate": ga_summary.get("conversion_rate", 0),
            "channels": ga_summary.get("channels", []),
            "hourly_performance": ga_summary.get("hourly_performance", []),
        }
    
    def generate_trend_chart(self, df: pd.DataFrame, metric: str, title: str) -> str:
        """
        Genera un gráfico de tendencia para la métrica especificada.
        
        Args:
            df: DataFrame con los datos.
            metric: Métrica a graficar.
            title: Título del gráfico.
            
        Returns:
            Imagen codificada en base64.
        """
        plt.figure(figsize=(10, 6))
        
        # Agrupar por fecha y calcular la suma de la métrica
        if 'date' in df.columns and metric in df.columns:
            daily_data = df.groupby('date')[metric].sum()
            daily_data.plot(marker='o')
        
        plt.title(title)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Guardar el gráfico en un buffer en memoria
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Codificar en base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    def generate_platform_comparison_chart(self, df: pd.DataFrame, metric: str, title: str) -> str:
        """
        Genera un gráfico comparativo entre plataformas para la métrica especificada.
        
        Args:
            df: DataFrame con los datos.
            metric: Métrica a graficar.
            title: Título del gráfico.
            
        Returns:
            Imagen codificada en base64.
        """
        plt.figure(figsize=(10, 6))
        
        # Verificar que las columnas necesarias existen en el DataFrame
        if 'platform' in df.columns and metric in df.columns:
            # Agrupar por plataforma y calcular la suma de la métrica
            platform_data = df.groupby('platform')[metric].sum()
            platform_data.plot(kind='bar')
        
        plt.title(title)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Guardar el gráfico en un buffer en memoria
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Codificar en base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    def generate_hourly_chart(self, hourly_data: List[Dict], metric: str, title: str) -> str:
        """
        Genera un gráfico por hora del día para la métrica especificada.
        
        Args:
            hourly_data: Lista de diccionarios con datos por hora.
            metric: Métrica a graficar.
            title: Título del gráfico.
            
        Returns:
            Imagen codificada en base64.
        """
        plt.figure(figsize=(12, 6))
        
        if hourly_data:
            # Convertir la lista de diccionarios a DataFrame
            df = pd.DataFrame(hourly_data)
            
            if 'hour' in df.columns and metric in df.columns:
                # Ordenar por hora
                df = df.sort_values('hour')
                
                # Graficar
                plt.bar(df['hour'], df[metric])
                plt.xticks(range(0, 24))
                plt.xlabel('Hora del día')
                plt.ylabel(metric)
        
        plt.title(title)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Guardar el gráfico en un buffer en memoria
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Codificar en base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    async def generate_performance_report(
        self,
        customer_id: str,
        days: int = 30
    ) -> Dict:
        """
        Genera un informe completo de rendimiento incluyendo campañas y canales.
        
        Args:
            customer_id: ID del cliente.
            days: Número de días para el período (por defecto 30).
            
        Returns:
            Diccionario con el informe completo y gráficos codificados en base64.
        """
        # Obtener datos de rendimiento de campañas
        campaign_summary = await self.get_campaign_performance_summary(
            customer_id, days
        )
        
        # Obtener datos de rendimiento por canal
        channel_summary = await self.get_channel_performance_summary(
            customer_id, days
        )
        
        # Verificar si hay un error en alguno de los resúmenes
        if "error" in campaign_summary and "error" in channel_summary:
            return {
                "customer": campaign_summary.get("customer", ""),
                "error": "No se pudieron obtener datos para el cliente seleccionado.",
                "campaign_error": campaign_summary.get("error", ""),
                "channel_error": channel_summary.get("error", "")
            }
        
        # Generar gráficos si hay datos disponibles
        charts = {}
        
        # Obtener cliente para usar en generación de gráficos
        customer = await self.client_service.get_customer_by_id(customer_id)
        
        if customer:
            # Calcular fechas
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Obtener cuentas por plataforma
            google_ads_accounts = [
                account for account in customer.accounts 
                if account.provider.lower() == 'adwords'
            ]
            
            facebook_accounts = [
                account for account in customer.accounts 
                if account.provider.lower() == 'fb'
            ]
            
            analytics_accounts = [
                account for account in customer.accounts 
                if account.provider.lower() in ['analytics4']
            ]
            
            # Obtener datos combinados para gráficos
            combined_df = await self.get_combined_campaign_performance(
                customer_id, 
                google_ads_accounts,
                facebook_accounts,
                analytics_accounts,
                start_date,
                end_date
            )
            
            if not combined_df.empty:
                # Generar gráficos de tendencias
                charts["cost_trend"] = self.generate_trend_chart(
                    combined_df, 'cost', f'Tendencia de Costo - {customer.name}'
                )
                
                charts["revenue_trend"] = self.generate_trend_chart(
                    combined_df, 'revenue', f'Tendencia de Ingresos - {customer.name}'
                )
                
                charts["sessions_trend"] = self.generate_trend_chart(
                    combined_df, 'sessions', f'Tendencia de Sesiones - {customer.name}'
                )
                
                # Generar gráfico de comparación entre plataformas
                charts["platform_cost"] = self.generate_platform_comparison_chart(
                    combined_df, 'cost', f'Costo por Plataforma - {customer.name}'
                )
                
                charts["platform_clicks"] = self.generate_platform_comparison_chart(
                    combined_df, 'clicks', f'Clics por Plataforma - {customer.name}'
                )
            
            # Generar gráfico por hora si hay datos
            if "hourly_performance" in channel_summary and channel_summary["hourly_performance"]:
                charts["hourly_sessions"] = self.generate_hourly_chart(
                    channel_summary["hourly_performance"], 
                    'sessions', 
                    f'Sesiones por Hora del Día - {customer.name}'
                )
                
                charts["hourly_conversion_rate"] = self.generate_hourly_chart(
                    channel_summary["hourly_performance"], 
                    'conversion_rate', 
                    f'Tasa de Conversión por Hora del Día - {customer.name}'
                )
        
        # Combinar todos los resúmenes y gráficos
        report = {
            "customer": campaign_summary.get("customer", ""),
            "period": campaign_summary.get("period", f"Últimos {days} días"),
            "campaign_performance": {
                "total_cost": campaign_summary.get("total_cost", 0),
                "total_revenue": campaign_summary.get("total_revenue", 0),
                "total_roas": campaign_summary.get("total_roas", 0),
                "total_sessions": campaign_summary.get("total_sessions", 0),
                "total_transactions": campaign_summary.get("total_transactions", 0),
                "total_cr": campaign_summary.get("total_cr", 0),
                "campaigns": campaign_summary.get("campaigns", [])
            },
            "channel_performance": {
                "total_sessions": channel_summary.get("total_sessions", 0),
                "total_transactions": channel_summary.get("total_transactions", 0),
                "total_revenue": channel_summary.get("total_revenue", 0),
                "conversion_rate": channel_summary.get("conversion_rate", 0),
                "channels": channel_summary.get("channels", []),
                "hourly_performance": channel_summary.get("hourly_performance", [])
            },
            "charts": charts
        }
        
        return report