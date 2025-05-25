import numpy as np
import pandas as pd

class Enricher:
    def __init__(self, logger):
        self.logger = logger

    def calcular_kpi(self, df=pd.DataFrame()):
        try:
            df = df.copy()
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df = df.dropna(subset=['fecha'])
            df = df.sort_values('fecha')

            df['dia'] = df['fecha'].dt.day

            meses = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }

            df['mes'] = df['fecha'].dt.month.map(meses)
            df['año'] = df['fecha'].dt.year

            df['año_mes'] = df['fecha'].dt.to_period('M').astype(str)
            
            cols_num = ['apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado', 'volumen']
            for col in cols_num:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df['retorno_diario'] = df['cerrar'].pct_change().fillna(0)
            df['tasa_variacion_ac'] = (df['cerrar'] - df['apertura']) / df['apertura']
            df['retorno_acumulado'] = (1 + df['retorno_diario']).cumprod() - 1
            df['media_movil_5d'] = df['cerrar'].rolling(window=5).mean().fillna(0)
            df['volatilidad'] = df['cerrar'].rolling(window=5).std().fillna(0)

            self.logger.info("Enricher", "calcular_kpi", "KPIs calculados correctamente")
            return df

        except Exception as e:
            self.logger.error("Enricher", "calcular_kpi", f"Error al enriquecer datos: {e}")
            return pd.DataFrame()