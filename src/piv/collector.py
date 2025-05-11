import requests
import pandas as pd
from bs4 import BeautifulSoup
from logger import Logger
import os
from datetime import datetime


class Collector:
    def __init__(self, logger):
        self.url='https://finance.yahoo.com/quote/META/history/?period1=1337347800&period2=1746921077'
        self.logger = logger

    os.makedirs('src/piv/static/data', exist_ok=True)

    def collector_data(self):
        try:
          df = pd.DataFrame()
          headers= {
             'User-Agent':'Mozilla/5.0'
             }
          response = requests.get(self.url,headers=headers)
          if response.status_code != 200:
             self.logger.error("Collector", "collector_data", f"Error al consultar la url : {response.status_code}")
             return df
          
          soup = BeautifulSoup(response.text,'html.parser')
          table = soup.select_one('div[data-testid="history-table"] table')
          if table is None:
             self.logger.error("Collector", "collector_data", "Error al buscar la tabla data-testid=history-table")
             return df
          
          headers = [th.get_text(strip=True) for th in table.thead.find_all('th')]
          rows=[]
          for tr in table.tbody.find_all('tr'):
              colums = [td.get_text(strip=True) for td in tr.find_all('td')]
              if len(colums) == len(headers):
                  rows.append(colums)
          df = pd.DataFrame(rows,columns=headers)

          df = self.clean_data(df)

          self.logger.info("Collector", "collector_data", f"Datos obtenidos exitosamente {df.shape}")
          return df
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
            
            if 'Fecha' in df_clean.columns:
                if not pd.api.types.is_datetime64_any_dtype(df_clean['Fecha']):
                    try:
                        df_clean['Fecha'] = pd.to_datetime(df_clean['Fecha'])
                        self.logger.info("Collector", "clean_data", "Columna Fecha convertida a datetime")
                    except Exception as e:
                        self.logger.error("Collector", "clean_data", f"Error al convertir la columna Fecha a datetime: {e}")
                        return df
                
                df_clean['Fecha_Formateada'] = df_clean['Fecha'].dt.strftime('%d/%m/%Y')
                
                df_clean['Dia'] = df_clean['Fecha'].dt.day
                df_clean['Mes'] = df_clean['Fecha'].dt.month
                df_clean['Año'] = df_clean['Fecha'].dt.year
                
                self.logger.info("Collector", "clean_data", "Columnas de fecha creadas exitosamente")
            else:
                self.logger.warning("Collector", "clean_data", "No se encontró la columna 'Fecha' en el DataFrame")
            
            numeric_columns = ['Apertura', 'Máximo', 'Mínimo', 'Cierre', 'Cierre Ajustado', 'Volumen']
            for col in numeric_columns:
                if col in df_clean.columns:
                    try:
                        df_clean[col] = pd.to_numeric(df_clean[col].astype(str).str.replace(',', ''), errors='coerce')
                        self.logger.info("Collector", "clean_data", f"Columna {col} convertida a numérico")
                    except Exception as e:
                        self.logger.warning("Collector", "clean_data", f"Error al convertir la columna {col} a numérico: {e}")
            
            self.logger.info("Collector", "clean_data", f"Limpieza de datos completada exitosamente: {df_clean.shape}")
            return df_clean
            
        except Exception as error:
            self.logger.error("Collector", "clean_data", f"Error durante la limpieza de datos: {error}")
            return df