import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

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

            # ✅ Cálculo de métricas de evaluación si existen las columnas necesarias
            if {'valor_real', 'valor_predicho'}.issubset(df.columns):
                mae = mean_absolute_error(df['valor_real'], df['valor_predicho'])
                rmse = mean_squared_error(df['valor_real'], df['valor_predicho'], squared=False)
                r2 = r2_score(df['valor_real'], df['valor_predicho'])
                mape = np.mean(np.abs((df['valor_real'] - df['valor_predicho']) / df['valor_real'])) * 100

                # Se añaden como columnas constantes para que puedan ser exportadas o inspeccionadas
                df['MAE'] = mae
                df['RMSE'] = rmse
                df['R2'] = r2
                df['MAPE'] = mape

                self.logger.info("Enricher", "calcular_kpi", f"Métricas calculadas: MAE={mae:.2f}, RMSE={rmse:.2f}, R2={r2:.2f}, MAPE={mape:.2f}%")
            else:
                self.logger.warning("Enricher", "calcular_kpi", "No se encontraron columnas 'valor_real' y 'valor_predicho', se omitieron métricas.")

            self.logger.info("Enricher", "calcular_kpi", "KPIs calculados correctamente")
            return df

        except Exception as e:
            self.logger.error("Enricher", "calcular_kpi", f"Error al enriquecer datos: {e}")
            return pd.DataFrame()
