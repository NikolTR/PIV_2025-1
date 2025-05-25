import requests
import pandas as pd
from bs4 import BeautifulSoup
from logger import Logger
import os
import re

class Collector:
    def __init__(self, logger):
        self.url = 'https://es.finance.yahoo.com/quote/META/history/'
        self.logger = logger
        os.makedirs('src/piv/static/data', exist_ok=True)

    def collector_data(self):
        df = pd.DataFrame()

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(self.url, headers=headers)

            if response.status_code != 200:
                self.logger.error("Collector", "collector_data", f"Error al consultar la URL: {response.status_code}")
                return df

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.select_one('div[data-testid="history-table"] table')

            if table is None:
                self.logger.error("Collector", "collector_data", "No se encontró la tabla con data-testid='history-table'")
                # Debug: intentar encontrar cualquier tabla
                tables = soup.find_all('table')
                self.logger.info("Collector", "collector_data", f"Se encontraron {len(tables)} tablas en total")
                if tables:
                    table = tables[0]  # Usar la primera tabla encontrada
                else:
                    return df

            headerss = [th.get_text(strip=True) for th in table.thead.find_all('th')]
            self.logger.info("Collector", "collector_data", f"Headers encontrados: {headerss}")
            
            rows = []
            for tr in table.tbody.find_all('tr'):
                columnas = [td.get_text(strip=True) for td in tr.find_all('td')]
                if len(columnas) == len(headerss):
                    rows.append(columnas)

            self.logger.info("Collector", "collector_data", f"Se encontraron {len(rows)} filas de datos")
            df = pd.DataFrame(rows, columns=headerss)

            # Limpieza de encabezados con texto adicional
            df.columns = df.columns.str.split('Precio de cierre ajustado').str[0]
            df.columns = df.columns.str.replace(r'[^\w\s]', '', regex=True).str.strip().str.lower()
            
            self.logger.info("Collector", "collector_data", f"Columnas después de limpieza: {df.columns.tolist()}")

            # Renombrar columnas
            df.rename(columns={
                'fecha': 'fecha',
                'open': 'apertura',
                'abrir': 'apertura',
                'high': 'alto',
                'máx': 'alto',
                'low': 'bajo',
                'mín': 'bajo',
                'close': 'cerrar',
                'adj close': 'cierre_ajustado',
                'cierre ajustado': 'cierre_ajustado',
                'volume': 'volumen',
                'volumen': 'volumen'
            }, inplace=True)

            self.logger.info("Collector", "collector_data", f"Columnas después de renombrar: {df.columns.tolist()}")

            # Limpieza de valores numéricos
            columnas_flotantes = ['apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado']
            for col in columnas_flotantes:
                if col in df.columns:
                    df[col] = df[col].astype(str).apply(lambda x: re.sub(r'[^\d.,-]', '', x))
                    df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            if 'volumen' in df.columns:
                df['volumen'] = df['volumen'].astype(str).apply(lambda x: re.sub(r'[^\d]', '', x))
                df['volumen'] = pd.to_numeric(df['volumen'], errors='coerce', downcast='integer')

            # Formatear la columna fecha como MM/DD/YYYY
            if 'fecha' in df.columns:
                # Primero intentar convertir sin formato específico
                df['fecha'] = pd.to_datetime(df['fecha'], format='%m/%d/%Y', errors='coerce')
                # Luego formatear
                df['fecha'] = df['fecha'].dt.strftime('%m/%d/%Y')

            # Eliminar filas completamente vacías
            df = df.dropna(how='all')

            self.logger.info("Collector", "collector_data", f"Datos obtenidos exitosamente {df.shape}")
            if not df.empty:
                self.logger.info("Collector", "collector_data", f"Muestra de datos:\n{df.head(2).to_string()}")
            
            return df

        except Exception as error:
            self.logger.error("Collector", "collector_data", f"Error al obtener los datos: {error}")
            return df