import os
import pickle
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class Modeller:
    def __init__(self, logger):
        self.logger = logger
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(base_dir, "static", "data", "models")
        self.model_file = os.path.join(self.model_path, "model.pkl")

        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

    def mean_absolute_percentage_error(self, y_true, y_pred):
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def entrenar(self, df):
        try:
            df = df.copy()
            df = df.dropna(subset=["cierre_ajustado"])

            # Entrenar modelo ARIMA
            series = df["cierre_ajustado"]
            model = ARIMA(series, order=(1, 1, 1))
            model_fit = model.fit()

            # Predicciones y métricas
            pred = model_fit.fittedvalues
            y_valid = series[-len(pred):]

            mae = mean_absolute_error(y_valid, pred)
            rmse = np.sqrt(mean_squared_error(y_valid, pred))
            r2 = r2_score(y_valid, pred)

            self.logger.info("Modeller", "entrenar", f"MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.2f}")

            with open(self.model_file, "wb") as f:
                pickle.dump(model_fit, f)

            return True

        except Exception as e:
            self.logger.error("Modeller", "entrenar", f"Error en entrenamiento: {str(e)}")
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
            self.logger.info("Modeller", "predecir", f"Predicción para {steps} paso(s): {forecast.tolist()}")
            return forecast.tolist()

        except Exception as e:
            self.logger.error("Modeller", "predecir", f"Error en predicción: {str(e)}")
            return []
