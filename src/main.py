"""
Punto de entrada principal para el servidor MCP de Pitágoras.
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
from io import BytesIO
from typing import Dict, List, Optional, Set, Union

import pandas as pd
from mcp.server.fastmcp import Context, FastMCP, Image

from api import (
    get_analytics_channel_report,
    get_analytics_hourly_report,
    get_analytics_report,
    get_customers,
    get_facebook_report,
    get_google_ads_report,
)
from config import TIME_PERIODS
from models import (
    Account,
    Customer,
    DateRange,
    GoogleAdsQuery,
    GoogleAnalyticsQuery,
    Provider,
)
from services import (
    AnalysisService,
    ClientService,
    FacebookAdsService,
    GoogleAdsService,
    GoogleAnalyticsService,
)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear instancia de FastMCP
mcp = FastMCP("Pitágoras Analytics", description="Servidor MCP para análisis de datos de Pitágoras API")

# Inicializar servicios
client_service = ClientService()
google_ads_service = GoogleAdsService()
facebook_ads_service = FacebookAdsService()
analytics_service = GoogleAnalyticsService()
analysis_service = AnalysisService()

# Diccionario para almacenar selecciones de cuentas por cliente
# Formato: {cliente_id: {"adwords": [account_ids], "fb": [account_ids], "analytics4": [account_ids]}}
selected_accounts = {}


# Herramientas para gestión de clientes
@mcp.tool()
async def listar_clientes() -> str:
    """Obtiene la lista de clientes disponibles."""
    try:
        clientes = await client_service.get_customers()
        
        if not clientes:
            return "No se encontraron clientes."
        
        resultado = "Clientes disponibles:\n\n"
        for cliente in clientes:
            resultado += f"- ID: {cliente.ID}\n"
            resultado += f"  Nombre: {cliente.name}\n"
            resultado += f"  Estado: {cliente.status or 'No especificado'}\n"
            resultado += f"  Cuentas: {len(cliente.accounts)}\n\n"
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error al listar clientes: {str(e)}")
        return f"Error al obtener la lista de clientes: {str(e)}"


@mcp.tool()
async def obtener_detalles_cliente(
    cliente_id: str = "",
    nombre_cliente: str = ""
) -> str:
    """
    Obtiene los detalles de un cliente específico.
    
    Args:
        cliente_id: ID del cliente.
        nombre_cliente: Nombre del cliente (alternativa a ID).
    """
    try:
        if not cliente_id and not nombre_cliente:
            return "Por favor, proporciona un ID o nombre de cliente."
        
        # Buscar por ID o por nombre
        cliente = None
        if cliente_id:
            cliente = await client_service.get_customer_by_id(cliente_id)
        else:
            cliente = await client_service.get_customer_by_name(nombre_cliente)
        
        if not cliente:
            return f"No se encontró el cliente con ID: {cliente_id} o nombre: {nombre_cliente}."
        
        # Contar cuentas por plataforma
        cuentas_por_plataforma = {}
        for cuenta in cliente.accounts:
            provider = cuenta.provider
            if provider not in cuentas_por_plataforma:
                cuentas_por_plataforma[provider] = 0
            cuentas_por_plataforma[provider] += 1
        
        # Generar respuesta
        resultado = f"Cliente: {cliente.name} (ID: {cliente.ID})\n"
        resultado += f"Estado: {cliente.status or 'No especificado'}\n\n"
        resultado += "Resumen de cuentas:\n"
        
        for provider, cantidad in cuentas_por_plataforma.items():
            resultado += f"- {provider}: {cantidad} cuenta(s)\n"
        
        resultado += "\nDetalle de cuentas:\n"
        
        for cuenta in cliente.accounts:
            resultado += f"\n- {cuenta.name} ({cuenta.provider})\n"
            resultado += f"  ID: {cuenta.accountID}\n"
            if cuenta.credentialEmail:
                resultado += f"  Email: {cuenta.credentialEmail}\n"
            if cuenta.objective:
                resultado += f"  Objetivo: {cuenta.objective}\n"
            if cuenta.currency:
                resultado += f"  Moneda: {cuenta.currency}\n"
            if cuenta.timezone:
                resultado += f"  Zona horaria: {cuenta.timezone}\n"
        
        # Mostrar cuentas seleccionadas si existen
        if cliente.ID in selected_accounts:
            resultado += "\nCuentas seleccionadas:\n"
            for provider, account_ids in selected_accounts[cliente.ID].items():
                if account_ids:
                    resultado += f"- {provider}: {len(account_ids)} cuenta(s)\n"
                    for account_id in account_ids:
                        # Buscar el nombre de la cuenta
                        for cuenta in cliente.accounts:
                            if cuenta.accountID == account_id and cuenta.provider == provider:
                                resultado += f"  • {cuenta.name} (ID: {account_id})\n"
                                break
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error al obtener detalles del cliente: {str(e)}")
        return f"Error al obtener detalles del cliente: {str(e)}"


@mcp.tool()
async def seleccionar_cuentas(
    cliente_id: str = "",
    nombre_cliente: str = "",
    provider: str = "",
    account_ids: str = ""
) -> str:
    """
    Selecciona las cuentas para análisis por proveedor.
    
    Args:
        cliente_id: ID del cliente.
        nombre_cliente: Nombre del cliente (alternativa a ID).
        provider: Proveedor (adwords, fb, analytics4).
        account_ids: IDs de cuentas separados por comas. Si está vacío, se deseleccionan.
    """
    try:
        if not cliente_id and not nombre_cliente:
            return "Por favor, proporciona un ID o nombre de cliente."
        
        # Buscar cliente
        cliente = None
        if cliente_id:
            cliente = await client_service.get_customer_by_id(cliente_id)
        else:
            cliente = await client_service.get_customer_by_name(nombre_cliente)
        
        if not cliente:
            return f"No se encontró el cliente con ID: {cliente_id} o nombre: {nombre_cliente}."
        
        # Validar proveedor
        valid_providers = ["adwords", "fb", "analytics4"]
        if provider and provider.lower() not in valid_providers:
            return f"Proveedor no válido. Use: {', '.join(valid_providers)}"
        
        # Inicializar selección para este cliente si no existe
        if cliente.ID not in selected_accounts:
            selected_accounts[cliente.ID] = {
                "adwords": [],
                "fb": [],
                "analytics4": []
            }
        
        # Si no se especifica proveedor, mostrar los disponibles
        if not provider:
            # Contar cuentas por proveedor
            cuentas_por_proveedor = {}
            for cuenta in cliente.accounts:
                prov = cuenta.provider
                if prov not in cuentas_por_proveedor:
                    cuentas_por_proveedor[prov] = []
                cuentas_por_proveedor[prov].append({
                    "id": cuenta.accountID,
                    "name": cuenta.name
                })
            
            resultado = f"Cuentas disponibles para {cliente.name}:\n\n"
            
            for prov, cuentas in cuentas_por_proveedor.items():
                resultado += f"Proveedor: {prov}\n"
                for cuenta in cuentas:
                    resultado += f"- {cuenta['name']} (ID: {cuenta['id']})\n"
                resultado += "\n"
            
            # Mostrar cuentas seleccionadas
            resultado += "\nCuentas actualmente seleccionadas:\n"
            for prov, ids in selected_accounts[cliente.ID].items():
                if ids:
                    resultado += f"{prov}: {', '.join(ids)}\n"
                else:
                    resultado += f"{prov}: ninguna\n"
            
            return resultado
        
        # Si se especifica proveedor pero no IDs, mostrar cuentas para ese proveedor
        if not account_ids:
            cuentas = [
                cuenta for cuenta in cliente.accounts 
                if cuenta.provider.lower() == provider.lower()
            ]
            
            if not cuentas:
                return f"No hay cuentas de {provider} para este cliente."
            
            resultado = f"Cuentas de {provider} para {cliente.name}:\n\n"
            for cuenta in cuentas:
                selected = "✓" if cuenta.accountID in selected_accounts[cliente.ID][provider.lower()] else " "
                resultado += f"[{selected}] {cuenta.name} (ID: {cuenta.accountID})\n"
            
            resultado += "\nPara seleccionar cuentas, use el parámetro account_ids con IDs separados por comas."
            return resultado
        
        # Seleccionar cuentas específicas
        ids_list = [id.strip() for id in account_ids.split(",") if id.strip()]
        
        # Verificar que los IDs existan para este proveedor
        cuentas_proveedor = [
            cuenta for cuenta in cliente.accounts 
            if cuenta.provider.lower() == provider.lower()
        ]
        
        ids_validos = []
        ids_invalidos = []
        
        for id in ids_list:
            if any(cuenta.accountID == id for cuenta in cuentas_proveedor):
                ids_validos.append(id)
            else:
                ids_invalidos.append(id)
        
        # Actualizar selección
        selected_accounts[cliente.ID][provider.lower()] = ids_validos
        
        # Generar respuesta
        resultado = f"Selección actualizada para {cliente.name} ({provider}):\n\n"
        
        if ids_validos:
            resultado += "Cuentas seleccionadas:\n"
            for id in ids_validos:
                # Buscar nombre de la cuenta
                for cuenta in cuentas_proveedor:
                    if cuenta.accountID == id:
                        resultado += f"- {cuenta.name} (ID: {id})\n"
                        break
        else:
            resultado += f"No se han seleccionado cuentas de {provider}.\n"
        
        if ids_invalidos:
            resultado += "\nIDs no válidos:\n"
            for id in ids_invalidos:
                resultado += f"- {id}\n"
            resultado += "\nVerifique que los IDs correspondan a cuentas existentes."
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error al seleccionar cuentas: {str(e)}")
        return f"Error al seleccionar cuentas: {str(e)}"


# Herramientas para análisis de rendimiento
@mcp.tool()
async def analizar_rendimiento_campañas(
    cliente_id: str = "",
    nombre_cliente: str = "",
    periodo_dias: int = 30
) -> str:
    """
    Analiza el rendimiento de las campañas publicitarias.
    
    Args:
        cliente_id: ID del cliente.
        nombre_cliente: Nombre del cliente (alternativa a ID).
        periodo_dias: Número de días para analizar (7, 14, 30).
    """
    try:
        if not cliente_id and not nombre_cliente:
            return "Por favor, proporciona un ID o nombre de cliente."
        
        # Validar período
        if periodo_dias not in [7, 14, 30]:
            periodo_dias = 30  # Valor por defecto
        
        # Obtener cliente
        cliente = None
        if cliente_id:
            cliente = await client_service.get_customer_by_id(cliente_id)
        else:
            cliente = await client_service.get_customer_by_name(nombre_cliente)
            
        if not cliente:
            return f"No se encontró el cliente con ID: {cliente_id} o nombre: {nombre_cliente}."
        
        cliente_id = cliente.ID
        
        # Verificar si hay cuentas seleccionadas
        if cliente_id not in selected_accounts:
            return f"No se han seleccionado cuentas para análisis. Use la herramienta 'seleccionar_cuentas' primero."
        
        # Obtener cuentas seleccionadas
        selected = selected_accounts[cliente_id]
        
        if not (selected["adwords"] or selected["fb"] or selected["analytics4"]):
            return f"No se han seleccionado cuentas para análisis. Use la herramienta 'seleccionar_cuentas' primero."
        
        # Filtrar cuentas por las seleccionadas
        google_ads_accounts = []
        facebook_accounts = []
        analytics_accounts = []
        
        # Obtener cuentas de Google Ads seleccionadas
        if selected["adwords"]:
            google_ads_accounts = [
                cuenta for cuenta in cliente.accounts 
                if cuenta.provider.lower() == 'adwords' and cuenta.accountID in selected["adwords"]
            ]
        
        # Obtener cuentas de Facebook seleccionadas
        if selected["fb"]:
            facebook_accounts = [
                cuenta for cuenta in cliente.accounts 
                if cuenta.provider.lower() == 'fb' and cuenta.accountID in selected["fb"]
            ]
        
        # Obtener cuentas de Analytics seleccionadas
        if selected["analytics4"]:
            analytics_accounts = [
                cuenta for cuenta in cliente.accounts 
                if cuenta.provider.lower() in ['analytics4', 'analytics'] and cuenta.accountID in selected["analytics4"]
            ]
        
        # Calcular fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=periodo_dias)
        
        # Obtener datos combinados
        combined_df = await analysis_service.get_combined_campaign_performance(
            cliente_id, 
            google_ads_accounts,
            facebook_accounts,
            analytics_accounts,
            start_date,
            end_date
        )
        
        if combined_df.empty:
            return f"No hay datos disponibles para las cuentas seleccionadas en el período de {periodo_dias} días."
        
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
        
        # Generar respuesta
        resultado = f"Análisis de Rendimiento de Campañas - {cliente.name}\n"
        resultado += f"Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}\n\n"
        
        # Mostrar cuentas utilizadas
        resultado += "CUENTAS ANALIZADAS:\n"
        if google_ads_accounts:
            resultado += "- Google Ads: " + ", ".join([a.name for a in google_ads_accounts]) + "\n"
        if facebook_accounts:
            resultado += "- Facebook: " + ", ".join([a.name for a in facebook_accounts]) + "\n"
        if analytics_accounts:
            resultado += "- Analytics: " + ", ".join([a.name for a in analytics_accounts]) + "\n"
        resultado += "\n"
        
        # Formatear métricas totales
        resultado += "RESUMEN TOTAL:\n"
        resultado += f"- Costo total: {total_cost:.2f}\n"
        resultado += f"- Ingresos totales: {total_revenue:.2f}\n"
        resultado += f"- ROAS: {total_roas:.2f}\n"
        resultado += f"- Sesiones: {total_sessions:.0f}\n"
        resultado += f"- Transacciones: {total_transactions:.0f}\n"
        resultado += f"- Tasa de conversión: {total_cr:.2f}%\n\n"
        
        # Mostrar rendimiento por campaña
        campañas = campaign_summary.to_dict('records')
        
        if not campañas:
            resultado += "No hay datos de campañas disponibles para el período seleccionado."
            return resultado
        
        resultado += "TOP CAMPAÑAS POR COSTO:\n"
        for i, campaña in enumerate(campañas[:10], 1):
            nombre = campaña.get("campaign_name", "Sin nombre")
            costo = campaña.get("cost", 0)
            revenue = campaña.get("revenue", 0)
            roas = campaña.get("roas", 0)
            cr = campaña.get("cr", 0)
            
            resultado += f"{i}. {nombre}\n"
            resultado += f"   Costo: {costo:.2f} | Ingresos: {revenue:.2f} | ROAS: {roas:.2f} | CR: {cr:.2f}%\n"
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en análisis de campañas: {str(e)}")
        return f"Error al analizar rendimiento de campañas: {str(e)}"


@mcp.tool()
async def analizar_rendimiento_canales(
    cliente_id: str = "",
    nombre_cliente: str = "",
    periodo_dias: int = 30
) -> str:
    """
    Analiza el rendimiento por canal de marketing.
    
    Args:
        cliente_id: ID del cliente.
        nombre_cliente: Nombre del cliente (alternativa a ID).
        periodo_dias: Número de días para analizar (7, 14, 30).
    """
    try:
        if not cliente_id and not nombre_cliente:
            return "Por favor, proporciona un ID o nombre de cliente."
        
        # Validar período
        if periodo_dias not in [7, 14, 30]:
            periodo_dias = 30  # Valor por defecto
        
        # Obtener cliente
        cliente = None
        if cliente_id:
            cliente = await client_service.get_customer_by_id(cliente_id)
        else:
            cliente = await client_service.get_customer_by_name(nombre_cliente)
            
        if not cliente:
            return f"No se encontró el cliente con ID: {cliente_id} o nombre: {nombre_cliente}."
        
        cliente_id = cliente.ID
        
        # Verificar si hay cuentas seleccionadas
        if cliente_id not in selected_accounts:
            return f"No se han seleccionado cuentas para análisis. Use la herramienta 'seleccionar_cuentas' primero."
        
        # Obtener cuentas de Analytics seleccionadas
        selected = selected_accounts[cliente_id]
        
        if not selected["analytics4"]:
            return f"No se han seleccionado cuentas de Google Analytics para análisis. Use la herramienta 'seleccionar_cuentas' primero."
        
        analytics_accounts = [
            cuenta for cuenta in cliente.accounts 
            if cuenta.provider.lower() in ['analytics4'] and cuenta.accountID in selected["analytics4"]
        ]
        
        if not analytics_accounts:
            return f"No se encontraron cuentas de Google Analytics válidas para el análisis."
        
        # Calcular fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=periodo_dias)
        
        # Obtener resumen de Analytics para las cuentas seleccionadas
        ga_summary = await analytics_service.get_analytics_summary(
            analytics_accounts, periodo_dias
        )
        
        # Formatear respuesta
        resultado = f"Análisis de Rendimiento por Canal - {cliente.name}\n"
        resultado += f"Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}\n\n"
        
        # Mostrar cuentas utilizadas
        resultado += "CUENTAS ANALIZADAS:\n"
        resultado += "- Analytics: " + ", ".join([a.name for a in analytics_accounts]) + "\n\n"
        
        # Formatear métricas totales
        total_sessions = ga_summary.get("total_sessions", 0)
        total_transactions = ga_summary.get("total_transactions", 0)
        total_revenue = ga_summary.get("total_revenue", 0)
        conversion_rate = ga_summary.get("conversion_rate", 0)
        
        resultado += "RESUMEN TOTAL:\n"
        resultado += f"- Sesiones totales: {total_sessions}\n"
        resultado += f"- Transacciones: {total_transactions}\n"
        resultado += f"- Ingresos totales: {total_revenue:.2f}\n"
        resultado += f"- Tasa de conversión: {conversion_rate:.2f}%\n\n"
        
        # Mostrar rendimiento por canal
        canales = ga_summary.get("channels", [])
        
        if not canales:
            resultado += "No hay datos de canales disponibles para el período seleccionado."
            return resultado
        
        resultado += "RENDIMIENTO POR CANAL:\n"
        for canal in canales:
            nombre = canal.get("channel", "Sin nombre")
            sessions = canal.get("sessions", 0)
            cr = canal.get("conversion_rate", 0)
            transactions = canal.get("transactions", 0)
            revenue = canal.get("revenue", 0)
            aov = canal.get("aov", 0)  # Average Order Value
            
            resultado += f"Canal: {nombre}\n"
            resultado += f"- Sesiones: {sessions} | Transacciones: {transactions} | CR: {cr:.2f}%\n"
            resultado += f"- Ingresos: {revenue:.2f} | AOV: {aov:.2f}\n\n"
        
        # Mostrar rendimiento por hora
        horas = ga_summary.get("hourly_performance", [])
        
        if horas:
            resultado += "RENDIMIENTO POR HORA DEL DÍA (Top 5 horas):\n"
            # Ordenar por sesiones
            horas_ordenadas = sorted(horas, key=lambda x: x.get("sessions", 0), reverse=True)
            
            for hora in horas_ordenadas[:5]:
                h = hora.get("hour", 0)
                sessions = hora.get("sessions", 0)
                cr = hora.get("conversion_rate", 0)
                revenue = hora.get("revenue", 0)
                
                resultado += f"Hora {h}:00: {sessions} sesiones | CR: {cr:.2f}% | Ingresos: {revenue:.2f}\n"
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en análisis de canales: {str(e)}")
        return f"Error al analizar rendimiento por canal: {str(e)}"


@mcp.tool()
async def generar_informe_rendimiento(
    cliente_id: str = "",
    nombre_cliente: str = "",
    periodo_dias: int = 30
) -> str:
    """
    Genera un informe completo de rendimiento con análisis integrado.
    
    Args:
        cliente_id: ID del cliente.
        nombre_cliente: Nombre del cliente (alternativa a ID).
        periodo_dias: Número de días para analizar (7, 14, 30).
    """
    try:
        if not cliente_id and not nombre_cliente:
            return "Por favor, proporciona un ID o nombre de cliente."
        
        # Validar período
        if periodo_dias not in [7, 14, 30]:
            periodo_dias = 30  # Valor por defecto
        
        # Obtener cliente
        cliente = None
        if cliente_id:
            cliente = await client_service.get_customer_by_id(cliente_id)
        else:
            cliente = await client_service.get_customer_by_name(nombre_cliente)
            
        if not cliente:
            return f"No se encontró el cliente con ID: {cliente_id} o nombre: {nombre_cliente}."
        
        cliente_id = cliente.ID
        
        # Verificar si hay cuentas seleccionadas
        if cliente_id not in selected_accounts:
            return f"No se han seleccionado cuentas para análisis. Use la herramienta 'seleccionar_cuentas' primero."
        
        # Obtener cuentas seleccionadas
        selected = selected_accounts[cliente_id]
        
        if not (selected["adwords"] or selected["fb"] or selected["analytics4"]):
            return f"No se han seleccionado cuentas para análisis. Use la herramienta 'seleccionar_cuentas' primero."
        
        # Filtrar cuentas por las seleccionadas
        google_ads_accounts = []
        facebook_accounts = []
        analytics_accounts = []
        
        # Obtener cuentas de Google Ads seleccionadas
        if selected["adwords"]:
            google_ads_accounts = [
                cuenta for cuenta in cliente.accounts 
                if cuenta.provider.lower() == 'adwords' and cuenta.accountID in selected["adwords"]
            ]
        
        # Obtener cuentas de Facebook seleccionadas
        if selected["fb"]:
            facebook_accounts = [
                cuenta for cuenta in cliente.accounts 
                if cuenta.provider.lower() == 'fb' and cuenta.accountID in selected["fb"]
            ]
        
        # Obtener cuentas de Analytics seleccionadas
        if selected["analytics4"]:
            analytics_accounts = [
                cuenta for cuenta in cliente.accounts 
                if cuenta.provider.lower() in ['analytics4', 'analytics'] and cuenta.accountID in selected["analytics4"]
            ]
        
        # Calcular fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=periodo_dias)
        
        # Obtener datos para generar el informe
        combined_df = None
        ga_summary = None
        
        # Obtener datos combinados de costos si hay cuentas de ads
        if google_ads_accounts or facebook_accounts:
            combined_df = await analysis_service.get_combined_campaign_performance(
                cliente_id, 
                google_ads_accounts,
                facebook_accounts,
                analytics_accounts,
                start_date,
                end_date
            )
        
        # Obtener datos de analytics si hay cuentas de GA
        if analytics_accounts:
            ga_summary = await analytics_service.get_analytics_summary(
                analytics_accounts, periodo_dias
            )
        
        # Verificar si hay datos para el informe
        if (combined_df is None or combined_df.empty) and (ga_summary is None or "error" in ga_summary):
            return f"No hay datos disponibles para las cuentas seleccionadas en el período de {periodo_dias} días."
        
        # Generar informe textual
        resultado = f"INFORME DE RENDIMIENTO DIGITAL - {cliente.name}\n"
        resultado += f"Período de análisis: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}\n\n"
        
        # Mostrar cuentas utilizadas
        resultado += "CUENTAS ANALIZADAS:\n"
        if google_ads_accounts:
            resultado += "- Google Ads: " + ", ".join([a.name for a in google_ads_accounts]) + "\n"
        if facebook_accounts:
            resultado += "- Facebook: " + ", ".join([a.name for a in facebook_accounts]) + "\n"
        if analytics_accounts:
            resultado += "- Analytics: " + ", ".join([a.name for a in analytics_accounts]) + "\n"
        resultado += "\n"
        
        # Resumen ejecutivo con datos de campañas y costos
        campaign_metrics = {}
        
        if combined_df is not None and not combined_df.empty:
            # Calcular totales
            total_cost = combined_df['cost'].sum()
            total_revenue = combined_df['revenue'].sum()
            total_sessions = combined_df['sessions'].sum()
            total_transactions = combined_df['transactions'].sum()
            
            # Calcular métricas derivadas
            total_roas = total_revenue / total_cost if total_cost > 0 else 0
            total_cr = total_transactions / total_sessions * 100 if total_sessions > 0 else 0
            
            campaign_metrics = {
                "total_cost": total_cost,
                "total_revenue": total_revenue,
                "total_roas": total_roas,
                "total_sessions": total_sessions,
                "total_transactions": total_transactions,
                "total_cr": total_cr
            }
            
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
            
            # Agregar campañas al diccionario
            campaign_metrics["campaigns"] = campaign_summary.to_dict('records')
        
        # Obtener métricas de canales de Analytics
        channel_metrics = {}
        if ga_summary is not None and "error" not in ga_summary:
            channel_metrics = {
                "total_sessions": ga_summary.get("total_sessions", 0),
                "total_transactions": ga_summary.get("total_transactions", 0),
                "total_revenue": ga_summary.get("total_revenue", 0),
                "conversion_rate": ga_summary.get("conversion_rate", 0),
                "channels": ga_summary.get("channels", []),
                "hourly_performance": ga_summary.get("hourly_performance", [])
            }
        
        # RESUMEN EJECUTIVO
        resultado += "RESUMEN EJECUTIVO:\n"
        
        # Agregar datos de costos si están disponibles
        if campaign_metrics:
            resultado += f"- Inversión total: {campaign_metrics.get('total_cost', 0):.2f}\n"
            resultado += f"- Ingresos totales: {campaign_metrics.get('total_revenue', 0):.2f}\n"
            resultado += f"- ROAS: {campaign_metrics.get('total_roas', 0):.2f}\n"
            resultado += f"- Sesiones: {campaign_metrics.get('total_sessions', 0):.0f}\n"
            resultado += f"- Transacciones: {campaign_metrics.get('total_transactions', 0):.0f}\n"
            resultado += f"- Tasa de conversión: {campaign_metrics.get('total_cr', 0):.2f}%\n\n"
        # Si no hay datos de costos pero sí de analytics
        elif channel_metrics:
            resultado += f"- Sesiones totales: {channel_metrics.get('total_sessions', 0)}\n"
            resultado += f"- Transacciones: {channel_metrics.get('total_transactions', 0)}\n"
            resultado += f"- Ingresos totales: {channel_metrics.get('total_revenue', 0):.2f}\n"
            resultado += f"- Tasa de conversión: {channel_metrics.get('conversion_rate', 0):.2f}%\n\n"
        
        # Análisis de campañas
        if campaign_metrics and "campaigns" in campaign_metrics:
            resultado += "ANÁLISIS DE CAMPAÑAS:\n"
            campañas = campaign_metrics.get("campaigns", [])
            
            if not campañas:
                resultado += "No hay datos de campañas disponibles para el período seleccionado.\n\n"
            else:
                # Top 5 campañas por costo
                resultado += "Top 5 campañas por inversión:\n"
                for i, campaña in enumerate(campañas[:5], 1):
                    nombre = campaña.get("campaign_name", "Sin nombre")
                    costo = campaña.get("cost", 0)
                    revenue = campaña.get("revenue", 0)
                    roas = campaña.get("roas", 0)
                    
                    resultado += f"{i}. {nombre}\n"
                    resultado += f"   Costo: {costo:.2f} | Ingresos: {revenue:.2f} | ROAS: {roas:.2f}\n"
                
                resultado += "\n"
                
                # Top 5 campañas por ROAS (si tienen costo > 0)
                campañas_con_costo = [c for c in campañas if c.get("cost", 0) > 0]
                campañas_por_roas = sorted(campañas_con_costo, key=lambda x: x.get("roas", 0), reverse=True)
                
                if campañas_por_roas:
                    resultado += "Top 5 campañas por ROAS:\n"
                    for i, campaña in enumerate(campañas_por_roas[:5], 1):
                        nombre = campaña.get("campaign_name", "Sin nombre")
                        costo = campaña.get("cost", 0)
                        revenue = campaña.get("revenue", 0)
                        roas = campaña.get("roas", 0)
                        
                        resultado += f"{i}. {nombre}\n"
                        resultado += f"   ROAS: {roas:.2f} | Costo: {costo:.2f} | Ingresos: {revenue:.2f}\n"
                    
                    resultado += "\n"
        
        # Análisis de canales
        if channel_metrics and "channels" in channel_metrics:
            resultado += "ANÁLISIS DE CANALES:\n"
            canales = channel_metrics.get("channels", [])
            
            if not canales:
                resultado += "No hay datos de canales disponibles para el período seleccionado.\n\n"
            else:
                # Ordenar canales por sesiones
                canales_ordenados = sorted(canales, key=lambda x: x.get("sessions", 0), reverse=True)
                
                for canal in canales_ordenados[:5]:
                    nombre = canal.get("channel", "Sin nombre")
                    sessions = canal.get("sessions", 0)
                    cr = canal.get("conversion_rate", 0)
                    transactions = canal.get("transactions", 0)
                    revenue = canal.get("revenue", 0)
                    
                    resultado += f"Canal: {nombre}\n"
                    resultado += f"- Sesiones: {sessions} | Transacciones: {transactions} | CR: {cr:.2f}%\n"
                    resultado += f"- Ingresos: {revenue:.2f}\n"
                
                resultado += "\n"
        
        # Análisis por hora
        if channel_metrics and "hourly_performance" in channel_metrics:
            resultado += "ANÁLISIS POR HORA DEL DÍA:\n"
            horas = channel_metrics.get("hourly_performance", [])
            
            if not horas:
                resultado += "No hay datos horarios disponibles para el período seleccionado.\n\n"
            else:
                # Horas con mayor tráfico
                horas_por_sesiones = sorted(horas, key=lambda x: x.get("sessions", 0), reverse=True)
                top_horas_sesiones = [h.get("hour", 0) for h in horas_por_sesiones[:3]]
                
                # Horas con mayor tasa de conversión
                horas_con_sesiones = [h for h in horas if h.get("sessions", 0) > 0]
                horas_por_cr = sorted(horas_con_sesiones, key=lambda x: x.get("conversion_rate", 0), reverse=True)
                top_horas_cr = [h.get("hour", 0) for h in horas_por_cr[:3]]
                
                resultado += f"Horas con mayor tráfico: {', '.join([f'{h}:00' for h in top_horas_sesiones])}\n"
                resultado += f"Horas con mejor tasa de conversión: {', '.join([f'{h}:00' for h in top_horas_cr])}\n\n"
        
        # Conclusiones y recomendaciones
        resultado += "CONCLUSIONES Y RECOMENDACIONES:\n"
        
        # Conclusiones basadas en datos disponibles
        conclusiones = []
        
        # Rendimiento general basado en ROAS
        if campaign_metrics and "total_roas" in campaign_metrics:
            total_roas = campaign_metrics.get("total_roas", 0)
            if total_roas >= 1:
                conclusiones.append("• El rendimiento general es positivo, con un ROAS favorable.")
            else:
                conclusiones.append("• El ROAS general está por debajo de 1, lo que indica oportunidades de optimización.")
        
        # Análisis de campañas
        if campaign_metrics and "campaigns" in campaign_metrics:
            campañas = campaign_metrics.get("campaigns", [])
            if campañas:
                campañas_negativas = [c for c in campañas if c.get("roas", 0) < 1 and c.get("cost", 0) > 0]
                if campañas:
                    porcentaje_negativas = len(campañas_negativas) / len(campañas) * 100
                    if porcentaje_negativas > 50:
                        conclusiones.append("• Un porcentaje significativo de campañas tiene ROAS menor a 1. Se recomienda revisar y optimizar.")
                
                # Mejores campañas
                campañas_con_costo = [c for c in campañas if c.get("cost", 0) > 0]
                campañas_por_roas = sorted(campañas_con_costo, key=lambda x: x.get("roas", 0), reverse=True)
                if campañas_por_roas:
                    mejor_campaña = campañas_por_roas[0]
                    conclusiones.append(f"• La campaña '{mejor_campaña.get('campaign_name')}' muestra el mejor rendimiento. Considerar aumentar presupuesto.")
                
                # Peores campañas
                peores_campañas = [c for c in campañas if c.get("roas", 0) < 0.5 and c.get("cost", 0) > 100]
                if peores_campañas:
                    conclusiones.append(f"• Revisar o pausar campañas de bajo rendimiento como '{peores_campañas[0].get('campaign_name')}'.")
        
        # Canales
        if channel_metrics and "channels" in channel_metrics:
            canales = channel_metrics.get("channels", [])
            if canales:
                canales_por_cr = sorted(canales, key=lambda x: x.get("conversion_rate", 0), reverse=True)
                if canales_por_cr:
                    mejor_canal = canales_por_cr[0]
                    conclusiones.append(f"• El canal '{mejor_canal.get('channel')}' muestra la mejor tasa de conversión. Enfocar esfuerzos aquí.")
        
        # Recomendación horaria
        if channel_metrics and "hourly_performance" in channel_metrics:
            horas = channel_metrics.get("hourly_performance", [])
            if horas:
                horas_con_sesiones = [h for h in horas if h.get("sessions", 0) > 0]
                horas_por_cr = sorted(horas_con_sesiones, key=lambda x: x.get("conversion_rate", 0), reverse=True)
                top_horas_cr = [h.get("hour", 0) for h in horas_por_cr[:3]]
                if top_horas_cr:
                    conclusiones.append(f"• Se recomienda concentrar inversión en las horas con mejor conversión: {', '.join([f'{h}:00' for h in top_horas_cr])}.")
        
        # Agregar conclusiones al resultado
        if conclusiones:
            resultado += "\n".join(conclusiones)
        else:
            resultado += "• No hay suficientes datos para generar conclusiones específicas."
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error al generar informe: {str(e)}")
        return f"Error al generar informe de rendimiento: {str(e)}"


@mcp.tool()
async def obtener_roas_por_campaña(
    cliente_id: str = "",
    nombre_cliente: str = "",
    periodo_dias: int = 30
) -> str:
    """
    Obtiene el ROAS (Return on Ad Spend) por campaña.
    
    Args:
        cliente_id: ID del cliente.
        nombre_cliente: Nombre del cliente (alternativa a ID).
        periodo_dias: Número de días para analizar (7, 14, 30).
    """
    try:
        if not cliente_id and not nombre_cliente:
            return "Por favor, proporciona un ID o nombre de cliente."
        
        # Validar período
        if periodo_dias not in [7, 14, 30]:
            periodo_dias = 30  # Valor por defecto
        
        # Obtener cliente
        cliente = None
        if cliente_id:
            cliente = await client_service.get_customer_by_id(cliente_id)
        else:
            cliente = await client_service.get_customer_by_name(nombre_cliente)
            
        if not cliente:
            return f"No se encontró el cliente con ID: {cliente_id} o nombre: {nombre_cliente}."
        
        cliente_id = cliente.ID
        
        # Verificar si hay cuentas seleccionadas
        if cliente_id not in selected_accounts:
            return f"No se han seleccionado cuentas para análisis. Use la herramienta 'seleccionar_cuentas' primero."
        
        # Obtener cuentas seleccionadas
        selected = selected_accounts[cliente_id]
        
        if not (selected["adwords"] or selected["fb"]):
            return f"No se han seleccionado cuentas de Google Ads o Facebook para análisis. Use la herramienta 'seleccionar_cuentas' primero."
        
        # Filtrar cuentas por las seleccionadas
        google_ads_accounts = []
        facebook_accounts = []
        analytics_accounts = []
        
        # Obtener cuentas de Google Ads seleccionadas
        if selected["adwords"]:
            google_ads_accounts = [
                cuenta for cuenta in cliente.accounts 
                if cuenta.provider.lower() == 'adwords' and cuenta.accountID in selected["adwords"]
            ]
        
        # Obtener cuentas de Facebook seleccionadas
        if selected["fb"]:
            facebook_accounts = [
                cuenta for cuenta in cliente.accounts 
                if cuenta.provider.lower() == 'fb' and cuenta.accountID in selected["fb"]
            ]
        
        # Obtener cuentas de Analytics seleccionadas (para datos de conversión)
        if selected["analytics4"]:
            analytics_accounts = [
                cuenta for cuenta in cliente.accounts 
                if cuenta.provider.lower() in ['analytics4', 'analytics'] and cuenta.accountID in selected["analytics4"]
            ]
        
        # Calcular fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=periodo_dias)
        
        # Obtener datos combinados
        combined_df = await analysis_service.get_combined_campaign_performance(
            cliente_id, 
            google_ads_accounts,
            facebook_accounts,
            analytics_accounts,
            start_date,
            end_date
        )
        
        if combined_df.empty:
            return f"No hay datos disponibles para las cuentas seleccionadas en el período de {periodo_dias} días."
        
        # Calcular totales
        total_cost = combined_df['cost'].sum()
        total_revenue = combined_df['revenue'].sum()
        
        # Calcular ROAS
        total_roas = total_revenue / total_cost if total_cost > 0 else 0
        
        # Agrupar por campaña
        campaign_summary = combined_df.groupby('campaign_name').agg({
            'cost': 'sum',
            'revenue': 'sum',
            'platform': 'first'  # Para identificar la plataforma principal
        }).reset_index()
        
        # Calcular ROAS por campaña
        campaign_summary['roas'] = campaign_summary['revenue'] / campaign_summary['cost']
        campaign_summary['roas'] = campaign_summary['roas'].replace([np.inf, -np.inf], 0)
        
        # Filtrar campañas con costo > 0
        campañas_con_costo = campaign_summary[campaign_summary['cost'] > 0]
        
        # Ordenar por ROAS (de mayor a menor)
        campañas_ordenadas = campañas_con_costo.sort_values('roas', ascending=False)
        
        # Generar respuesta
        resultado = f"ROAS por Campaña - {cliente.name}\n"
        resultado += f"Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}\n\n"
        
        # Mostrar cuentas utilizadas
        resultado += "CUENTAS ANALIZADAS:\n"
        if google_ads_accounts:
            resultado += "- Google Ads: " + ", ".join([a.name for a in google_ads_accounts]) + "\n"
        if facebook_accounts:
            resultado += "- Facebook: " + ", ".join([a.name for a in facebook_accounts]) + "\n"
        if analytics_accounts:
            resultado += "- Analytics: " + ", ".join([a.name for a in analytics_accounts]) + "\n"
        resultado += "\n"
        
        # Métricas totales
        resultado += f"ROAS General: {total_roas:.2f} (Inversión: {total_cost:.2f}, Ingresos: {total_revenue:.2f})\n\n"
        
        # Verificar si hay datos de campañas
        if campañas_ordenadas.empty:
            resultado += "No hay datos de campañas con inversión para el período seleccionado."
            return resultado
        
        # Tabla de campañas
        resultado += "CAMPAÑA | ROAS | INVERSIÓN | INGRESOS\n"
        resultado += "--------|------|-----------|----------\n"
        
        for _, campaña in campañas_ordenadas.iterrows():
            nombre = campaña.get("campaign_name", "Sin nombre")
            costo = campaña.get("cost", 0)
            revenue = campaña.get("revenue", 0)
            roas = campaña.get("roas", 0)
            
            # Limitar longitud del nombre para formato tabular
            nombre_corto = nombre[:40] + "..." if len(nombre) > 40 else nombre
            
            resultado += f"{nombre_corto} | {roas:.2f} | {costo:.2f} | {revenue:.2f}\n"
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error al obtener ROAS: {str(e)}")
        return f"Error al obtener ROAS por campaña: {str(e)}"


# Ejecutar el servidor MCP
if __name__ == "__main__":
    mcp.run()