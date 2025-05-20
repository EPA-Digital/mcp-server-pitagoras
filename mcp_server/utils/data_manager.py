"""
Módulo para gestionar los datos y dataframes.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
import pandas as pd
import numpy as np
from io import StringIO
import sys

# Configuración de logging
logger = logging.getLogger(__name__)

class DataManager:
    """
    Clase para gestionar datos y dataframes en memoria.
    """
    
    def __init__(self):
        """Inicializa el gestor de datos."""
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.logs: List[str] = []
        self.df_counter = 0
    
    def generate_df_name(self, prefix: str = "df") -> str:
        """
        Genera un nombre único para un dataframe.
        
        Args:
            prefix: Prefijo para el nombre del dataframe
            
        Returns:
            Nombre único para el dataframe
        """
        self.df_counter += 1
        return f"{prefix}_{self.df_counter}"
    
    def add_log(self, message: str) -> None:
        """
        Añade un mensaje al log.
        
        Args:
            message: Mensaje a añadir
        """
        self.logs.append(message)
        logger.info(message)
    
    def store_dataframe(self, df: pd.DataFrame, name: Optional[str] = None) -> str:
        """
        Almacena un dataframe en memoria.
        
        Args:
            df: Dataframe a almacenar
            name: Nombre para el dataframe (opcional)
            
        Returns:
            Nombre asignado al dataframe
        """
        if name is None:
            name = self.generate_df_name()
        
        self.dataframes[name] = df
        self.add_log(f"Dataframe '{name}' almacenado con {df.shape[0]} filas y {df.shape[1]} columnas")
        return name
    
    def get_dataframe(self, name: str) -> Optional[pd.DataFrame]:
        """
        Obtiene un dataframe almacenado.
        
        Args:
            name: Nombre del dataframe
            
        Returns:
            Dataframe almacenado o None si no existe
        """
        if name not in self.dataframes:
            self.add_log(f"Error: Dataframe '{name}' no encontrado")
            return None
        return self.dataframes[name]
    
    def list_dataframes(self) -> List[Tuple[str, Tuple[int, int]]]:
        """
        Lista los dataframes almacenados con sus dimensiones.
        
        Returns:
            Lista de tuplas (nombre, (filas, columnas))
        """
        return [(name, df.shape) for name, df in self.dataframes.items()]
    
    def convert_api_data_to_dataframe(self, data: Dict[str, Any], df_name: Optional[str] = None) -> str:
        """
        Convierte datos de la API a un dataframe y lo almacena.
        
        Args:
            data: Datos de la API
            df_name: Nombre para el dataframe (opcional)
            
        Returns:
            Nombre asignado al dataframe
        """
        if "headers" not in data or "rows" not in data:
            self.add_log("Error: Los datos no tienen el formato esperado (headers y rows)")
            raise ValueError("Los datos no tienen el formato esperado")
        
        headers = data["headers"]
        rows = data["rows"]
        
        # Crear dataframe
        df = pd.DataFrame(rows, columns=headers)
        
        # Convertir tipos de datos
        for col in df.columns:
            # Intentar convertir a numérico si es posible
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    pass  # Mantener como objeto si no se puede convertir
        
        # Almacenar el dataframe
        name = self.store_dataframe(df, df_name)
        
        if "errors" in data and data["errors"]:
            for error in data["errors"]:
                self.add_log(f"Advertencia: {error}")
        
        return name
    
    def run_script(self, script: str, save_to_memory: Optional[List[str]] = None) -> str:
        """
        Ejecuta un script de Python y captura su salida.
        
        Args:
            script: Script de Python a ejecutar
            save_to_memory: Lista de nombres de variables a guardar como dataframes
            
        Returns:
            Salida del script
        """
        # Preparar variables locales con los dataframes almacenados
        local_vars = {**self.dataframes}
        
        # Capturar la salida estándar
        stdout_capture = StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout_capture
        
        try:
            self.add_log(f"Ejecutando script:\n{script}")
            
            # Ejecutar el script
            exec(script, {
                'pd': pd, 
                'np': np, 
                'scipy': __import__('scipy'),
                'statsmodels': __import__('statsmodels'),
                'sklearn': __import__('sklearn'),
                'plt': __import__('matplotlib.pyplot'),
                'sns': __import__('seaborn')
            }, local_vars)
            
            # Capturar la salida
            output = stdout_capture.getvalue()
            
            # Guardar variables en memoria si se solicita
            if save_to_memory:
                for var_name in save_to_memory:
                    if var_name in local_vars and isinstance(local_vars[var_name], pd.DataFrame):
                        self.store_dataframe(local_vars[var_name], var_name)
                    else:
                        self.add_log(f"Advertencia: No se pudo guardar '{var_name}' - no es un DataFrame o no existe")
            
            return output if output else "Ejecución completada sin salida."
        
        except Exception as e:
            error_msg = f"Error al ejecutar script: {str(e)}"
            self.add_log(error_msg)
            return error_msg
        
        finally:
            # Restaurar la salida estándar
            sys.stdout = original_stdout
    
    def get_logs(self) -> str:
        """
        Obtiene los logs almacenados.
        
        Returns:
            Logs como string
        """
        return "\n".join(self.logs)