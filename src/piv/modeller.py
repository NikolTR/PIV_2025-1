import os
import pickle
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class Modeller:
    def __init__(self, logger):
        self.logger = logger
        self.model_path = "static/models/model.pkl"
        self.model_file = os.path.join(self.model_path, "model.pkl")

        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

    def mean_absolute_percentage_error(self, y_true, y_pred):
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def entrenar(self, df):
        """
        Entrena un modelo ARIMA(1,1,1) con la columna 'cierre_ajustado',
        calcula métricas y guarda el modelo en un archivo .pkl
        """
        try:
            df = df.copy()
            y = df['cierre_ajustado'].dropna()

            # Entrenar modelo ARIMA (ejemplo orden fijo)
            model = ARIMA(y, order=(1, 1, 1))
            model_fit = model.fit()

            # Calcular métricas con fittedvalues alineadas
            pred = model_fit.fittedvalues
            y_valid = y.iloc[1:]  # porque ARIMA(1,1,1) pierde una observación

            mae = mean_absolute_error(y_valid, pred)
            rmse = np.sqrt(mean_squared_error(y_valid, pred))
            r2 = r2_score(y_valid, pred)
            mape = self.mean_absolute_percentage_error(y_valid, pred)

            self.logger.info(f"MAE: {mae:.2f}")
            self.logger.info(f"RMSE: {rmse:.2f}")
            self.logger.info(f"MAPE: {mape:.2f}%")
            self.logger.info(f"R²: {r2:.2f}")
            self.logger.info("Modelo entrenado y métricas calculadas correctamente.")

            # Guardar modelo
            with open(self.model_file, 'wb') as f:
                pickle.dump(model_fit, f)
            self.logger.info(f"Modelo guardado en {self.model_file}")

            return True
        except Exception as e:
            self.logger.error(f"Error en entrenamiento: {str(e)}")
            return False

    def predecir(self, df, steps=1):
        """
        Carga modelo desde .pkl y genera predicción (por defecto 1 paso adelante)
        """
        try:
            df = df.copy()
            with open(self.model_file, 'rb') as f:
                model_fit = pickle.load(f)

            forecast = model_fit.forecast(steps=steps)
            self.logger.info(f"Predicción para {steps} paso(s): {forecast.tolist()}")
            return forecast.tolist()
        except Exception as e:
            self.logger.error(f"Error en predicción: {str(e)}")
            return []