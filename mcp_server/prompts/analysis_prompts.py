"""
Plantillas de prompts para análisis de datos de marketing.
"""

import logging
from typing import Dict, List, Optional, Any
from mcp.server.models import BaseModel
from mcp.server.fastmcp import Context

# Configuración de logging
logger = logging.getLogger(__name__)

# Plantillas de prompts

EXPLORATORY_ANALYSIS_PROMPT = """
# Análisis Exploratorio de Datos de Marketing Digital

Eres un analista de datos experto en marketing digital. Tu tarea es realizar un análisis exploratorio de los datos extraídos y proporcionar insights valiosos para la toma de decisiones.

## Contexto:
{context}

## Fuente de Datos:
- Plataforma: {platform}
- Periodo de análisis: {start_date} a {end_date}
- Métricas principales: {metrics}

## Objetivos del Análisis:
1. Proporcionar una comprensión general de los datos (estadísticas descriptivas)
2. Identificar tendencias y patrones
3. Detectar anomalías o valores atípicos
4. Evaluar el rendimiento de las campañas/canales
5. Ofrecer recomendaciones iniciales basadas en los hallazgos

## Instrucciones:
1. Utiliza la herramienta `list_dataframes` para verificar los DataFrames disponibles.
2. Utiliza la herramienta `run_script` para realizar el análisis exploratorio usando pandas, numpy, etc.
3. Asegúrate de guardar resultados intermedios utilizando el parámetro `save_to_memory`.
4. Para cada insight importante, genera una visualización apropiada usando plotly para facilitar la comprensión.
5. Estructura tu análisis de manera clara y concisa para facilitar la toma de decisiones.

## Análisis Sugerido:
1. **Exploración inicial de los datos**:
   - Dimensiones del dataset
   - Tipos de datos
   - Estadísticas descriptivas básicas
   - Valores faltantes o nulos

2. **Análisis univariado**:
   - Distribución de métricas clave (ej. impresiones, clics, conversiones)
   - Identificación de valores atípicos

3. **Análisis bivariado y multivariado**:
   - Correlaciones entre métricas
   - Relaciones entre variables de interés

4. **Análisis temporal** (si aplica):
   - Tendencias a lo largo del tiempo
   - Patrones estacionales o cíclicos
   - Comparativa de periodos

5. **Segmentación y agrupación**:
   - Análisis por campaña/canal/segmento
   - Identificación de grupos de rendimiento similar

6. **Insights y recomendaciones**:
   - Principales hallazgos del análisis
   - Recomendaciones iniciales basadas en datos
   - Áreas que requieren análisis más profundo

Por favor, comienza tu análisis comprobando los DataFrames disponibles.
"""

PERFORMANCE_COMPARISON_PROMPT = """
# Comparación de Rendimiento entre Plataformas de Marketing Digital

Eres un especialista en análisis de performance de marketing digital. Tu tarea es realizar una comparación exhaustiva del rendimiento entre diferentes plataformas de marketing digital para identificar oportunidades de optimización de presupuesto y estrategia.

## Plataformas a Comparar:
{platforms}

## Periodo de Comparación:
{start_date} a {end_date}

## Métricas Clave para Comparar:
{metrics}

## Objetivos del Análisis:
1. Comparar efectivamente el rendimiento entre plataformas
2. Identificar qué plataforma ofrece mejor ROI/eficiencia
3. Descubrir fortalezas y debilidades de cada plataforma
4. Proporcionar recomendaciones sobre asignación de presupuesto
5. Identificar oportunidades de sinergia entre plataformas

## Instrucciones:
1. Utiliza la herramienta `list_dataframes` para verificar los DataFrames disponibles.
2. Homogeniza los datos de diferentes plataformas para asegurar comparabilidad (usa `run_script`).
3. Realiza análisis comparativos usando métricas normalizadas y porcentuales.
4. Genera visualizaciones que faciliten la comparación entre plataformas.
5. Evalúa el rendimiento por diferentes dimensiones (campañas, audiencias, etc.).
6. Prioriza insights accionables para la optimización cross-platform.

## Análisis Sugerido:
1. **Normalización y preparación de datos**:
   - Unificar métricas entre plataformas
   - Ajustar por diferencias en estructura de datos
   - Crear KPIs comparables (CTR, CPC, ROAS, etc.)

2. **Análisis comparativo general**:
   - Comparación de KPIs principales entre plataformas
   - Análisis de tendencias paralelas
   - Identificación de outliers por plataforma

3. **Análisis de eficiencia**:
   - Comparación de costos relativos (CPC, CPM, CPA)
   - Análisis de conversion funnel por plataforma
   - Evaluación de ROI/ROAS

4. **Análisis segmentado**:
   - Rendimiento por tipo de campaña/objetivo
   - Rendimiento por audiencia/segmento
   - Análisis temporal comparativo

5. **Análisis de atribución cross-platform** (si es posible):
   - Evaluación de customer journey entre plataformas
   - Análisis de touchpoints complementarios
   - Identificación de canales de apoyo vs. canales de conversión

6. **Recomendaciones de optimización**:
   - Propuestas de reasignación de presupuesto
   - Oportunidades de mejora por plataforma
   - Estrategias de sinergia entre plataformas

Por favor, comienza tu análisis explorando los DataFrames disponibles y preparando los datos para la comparación.
"""

OPTIMIZATION_RECOMMENDATIONS_PROMPT = """
# Recomendaciones de Optimización para Campañas de Marketing Digital

Eres un estratega de marketing digital especializado en optimización de campañas. Tu tarea es analizar los datos de rendimiento y proporcionar recomendaciones específicas y accionables para mejorar los resultados de las campañas.

## Contexto:
{context}

## Plataforma/Canal:
{platform}

## Periodo de Análisis:
{start_date} a {end_date}

## Métricas de Rendimiento Actuales:
{metrics}

## Objetivos de Optimización:
1. Mejorar la eficiencia de inversión (reducir costos manteniendo resultados)
2. Incrementar las conversiones y/o el retorno de inversión
3. Optimizar la segmentación y targeting
4. Mejorar la relevancia y calidad de los anuncios/contenidos
5. Identificar oportunidades de escalado o áreas a reducir

## Instrucciones:
1. Utiliza la herramienta `list_dataframes` para verificar los DataFrames disponibles.
2. Implementa análisis detallado mediante `run_script` para identificar áreas de mejora.
3. Estructura tus recomendaciones en orden de impacto potencial y facilidad de implementación.
4. Justifica cada recomendación con evidencia basada en datos.
5. Incluye visualizaciones que refuercen tus recomendaciones.
6. Sugiere métricas de seguimiento para evaluar el impacto de las optimizaciones.

## Análisis Sugerido:
1. **Diagnóstico de rendimiento actual**:
   - Identificación de KPIs por debajo del benchmark
   - Análisis de tendencias recientes
   - Detección de ineficiencias y cuellos de botella

2. **Análisis de rentabilidad**:
   - Evaluación de ROI/ROAS por campaña, grupo de anuncios, keywords, etc.
   - Análisis de distribution of spend vs. results
   - Identificación de áreas de alto costo y bajo rendimiento

3. **Análisis de audiencia y segmentación**:
   - Evaluación de performance por segmento/audiencia
   - Oportunidades de refinamiento de targeting
   - Identificación de nuevos segmentos de valor

4. **Análisis creativo y de mensajes** (si aplica):
   - Evaluación de relevancia y calidad de anuncios/contenidos
   - Análisis A/B testing o variantes creativas
   - Recomendaciones de mejora de copy y creatividades

5. **Análisis de estructura de campañas**:
   - Evaluación de configuración actual
   - Oportunidades de reorganización o consolidación
   - Optimización de configuraciones técnicas

6. **Recomendaciones concretas**:
   - Top 5-10 acciones accionables inmediatas
   - Optimizaciones a medio plazo
   - Estrategias de crecimiento/escalado a largo plazo

Por favor, comienza tu análisis explorando los datos disponibles para identificar las principales áreas de oportunidad.
"""

async def exploratory_analysis_prompt(
    context: str,
    platform: str,
    start_date: str,
    end_date: str,
    metrics: str,
    ctx: Context
) -> List[BaseModel]:
    """
    Genera un prompt para análisis exploratorio de datos.
    
    Args:
        context: Contexto del análisis
        platform: Plataforma analizada
        start_date: Fecha de inicio
        end_date: Fecha de fin
        metrics: Métricas principales
        ctx: Contexto de la petición
        
    Returns:
        Mensajes del prompt
    """
    logger.info(f"Generando prompt de análisis exploratorio para plataforma: {platform}")
    
    prompt = EXPLORATORY_ANALYSIS_PROMPT.format(
        context=context,
        platform=platform,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics
    )
    
    return [BaseModel(role="user", content=BaseModel(type="text", text=prompt))]

async def performance_comparison_prompt(
    platforms: str,
    start_date: str,
    end_date: str,
    metrics: str,
    ctx: Context
) -> List[BaseModel]:
    """
    Genera un prompt para comparación de rendimiento entre plataformas.
    
    Args:
        platforms: Plataformas a comparar
        start_date: Fecha de inicio
        end_date: Fecha de fin
        metrics: Métricas a comparar
        ctx: Contexto de la petición
        
    Returns:
        Mensajes del prompt
    """
    logger.info(f"Generando prompt de comparación de rendimiento para plataformas: {platforms}")
    
    prompt = PERFORMANCE_COMPARISON_PROMPT.format(
        platforms=platforms,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics
    )
    
    return [BaseModel(role="user", content=BaseModel(type="text", text=prompt))]

async def optimization_recommendations_prompt(
    context: str,
    platform: str,
    start_date: str,
    end_date: str,
    metrics: str,
    ctx: Context
) -> List[BaseModel]:
    """
    Genera un prompt para recomendaciones de optimización.
    
    Args:
        context: Contexto del análisis
        platform: Plataforma analizada
        start_date: Fecha de inicio
        end_date: Fecha de fin
        metrics: Métricas actuales
        ctx: Contexto de la petición
        
    Returns:
        Mensajes del prompt
    """
    logger.info(f"Generando prompt de recomendaciones de optimización para plataforma: {platform}")
    
    prompt = OPTIMIZATION_RECOMMENDATIONS_PROMPT.format(
        context=context,
        platform=platform,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics
    )
    
    return [BaseModel(role="user", content=BaseModel(type="text", text=prompt))]