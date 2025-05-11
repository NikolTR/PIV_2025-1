import requests
import pandas as pd
from bs4 import BeautifulSoup
from logger import Logger
import os
from datetime import datetime
import locale


class Collector:
    def __init__(self, logger):
        self.url='https://finance.yahoo.com/quote/META/history/?period1=1337347800&period2=1746921077'
        self.logger = logger
        os.makedirs('src/piv/static/data', exist_ok=True)

    def collector_data(self):
        try:
            df = pd.DataFrame()
            headers = {
                'User-Agent':'Mozilla/5.0'
            }
            response = requests.get(self.url, headers=headers)
            if response.status_code != 200:
                self.logger.error("Collector", "collector_data", f"Error al consultar la url : {response.status_code}")
                return df
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.select_one('div[data-testid="history-table"] table')
            if table is None:
                self.logger.error("Collector", "collector_data", "Error al buscar la tabla data-testid=history-table")
                return df
            
            headers = [th.get_text(strip=True) for th in table.thead.find_all('th')]
            rows = []
            for tr in table.tbody.find_all('tr'):
                columns = [td.get_text(strip=True) for td in tr.find_all('td')]
                if len(columns) == len(headers):
                    rows.append(columns)
            
            df = pd.DataFrame(rows, columns=headers)
            
            self.logger.info("Collector", "collector_data", f"Datos brutos obtenidos exitosamente: {df.shape}")
            self.logger.info("Collector", "collector_data", f"Columnas originales: {list(df.columns)}")
            
            df_cleaned = self.clean_data(df)
            
            return df_cleaned
            
        except Exception as error:
            self.logger.error("Collector", "collector_data", f"Error al obtener los datos de la url {error}")
            return pd.DataFrame()
        
    def clean_data(self, df):
        """
        Limpia y transforma los datos del DataFrame.
        
        Args:
            df: DataFrame con los datos originales
            
        Returns:
            DataFrame: DataFrame con los datos limpios y transformados
        """
        try:
            if df.empty:
                self.logger.warning("Collector", "clean_data", "DataFrame vacío, no se puede procesar")
                return df
            
            df_clean = df.copy()
            
            self.logger.info("Collector", "clean_data", f"Iniciando limpieza de datos: {df_clean.shape}")
            self.logger.info("Collector", "clean_data", f"Columnas originales: {df_clean.columns.tolist()}")
            
            column_mapping = {
                'Date': 'Fecha',
                'Open': 'Apertura', 
                'High': 'Máximo',
                'Low': 'Mínimo',
                'Close': 'Cierre',
                'Adj Close': 'Cierre Ajustado',
                'Volume': 'Volumen'
            }
            
            columns_to_rename = {col: column_mapping.get(col, col) for col in df_clean.columns if col in column_mapping}
            df_clean = df_clean.rename(columns=columns_to_rename)
            
            self.logger.info("Collector", "clean_data", f"Columnas renombradas: {df_clean.columns.tolist()}")
            
            if 'Fecha' in df_clean.columns:
                if not pd.api.types.is_datetime64_any_dtype(df_clean['Fecha']):
                    try:
                        self.logger.info("Collector", "clean_data", f"Valores de ejemplo en Fecha: {df_clean['Fecha'].head().tolist()}")
                        
                        df_clean['Fecha'] = pd.to_datetime(df_clean['Fecha'], errors='coerce')
                        self.logger.info("Collector", "clean_data", "Columna Fecha convertida a datetime")
                    except Exception as e:
                        self.logger.error("Collector", "clean_data", f"Error al convertir la columna Fecha a datetime: {e}")
                        return df
                
                df_clean['Fecha_Formateada'] = df_clean['Fecha'].dt.strftime('%d/%m/%Y')
                
                meses_espanol = {
                    1: 'Enero',
                    2: 'Febrero',
                    3: 'Marzo',
                    4: 'Abril',
                    5: 'Mayo',
                    6: 'Junio',
                    7: 'Julio',
                    8: 'Agosto',
                    9: 'Septiembre',
                    10: 'Octubre',
                    11: 'Noviembre',
                    12: 'Diciembre'
                }
                
                df_clean['Dia'] = df_clean['Fecha'].dt.day
                df_clean['Mes'] = df_clean['Fecha'].dt.month.map(meses_espanol)
                df_clean['Año'] = df_clean['Fecha'].dt.year
                
                self.logger.info("Collector", "clean_data", "Columnas de fecha creadas exitosamente")
            else:
                self.logger.warning("Collector", "clean_data", "No se encontró la columna 'Fecha' en el DataFrame")
            
            numeric_columns = ['Apertura', 'Máximo', 'Mínimo', 'Cierre', 'Cierre Ajustado', 'Volumen']
            for col in numeric_columns:
                if col in df_clean.columns:
                    try:
                        df_clean[col] = df_clean[col].astype(str).str.replace(',', '')
                        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                        self.logger.info("Collector", "clean_data", f"Columna {col} convertida a numérico")
                    except Exception as e:
                        self.logger.warning("Collector", "clean_data", f"Error al convertir la columna {col} a numérico: {e}")
            
            self.logger.info("Collector", "clean_data", f"Limpieza de datos completada exitosamente: {df_clean.shape}")
            self.logger.info("Collector", "clean_data", f"Muestra de datos procesados: \n{df_clean.head(2)}")
            
            return df_clean
            
        except Exception as error:
            self.logger.error("Collector", "clean_data", f"Error durante la limpieza de datos: {error}")
            return df