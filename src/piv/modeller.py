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
        """Cálculo de MAPE: útil para interpretar el error como porcentaje relativo"""
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def entrenar(self, df):
        """
        Entrena un modelo ARIMA, guarda el artefacto y calcula métricas de evaluación.

        Justificación de las métricas elegidas:
        - MAE (Error Absoluto Medio): permite interpretar directamente el promedio de error en las mismas unidades que la variable. Es simple, robusta frente a valores atípicos.
        - RMSE (Raíz del Error Cuadrático Medio): penaliza más los errores grandes, útil si los errores grandes son más costosos. Da una idea de la magnitud del error.
        - R² (Coeficiente de Determinación): mide qué proporción de la variabilidad de la variable dependiente está explicada por el modelo.
        - MAPE (Error Porcentual Absoluto Medio): expresa el error en términos porcentuales, útil cuando se necesita interpretar el error relativo.
        """

        try:
            df = df.copy()
            df = df.dropna(subset=["cierre_ajustado"])
            series = df["cierre_ajustado"]

            # Entrenamiento del modelo ARIMA
            model = ARIMA(series, order=(1, 1, 1))
            model_fit = model.fit()

            # Predicciones y subconjunto de validación
            pred = model_fit.fittedvalues
            y_valid = series[-len(pred):]

            # Cálculo de métricas
            mae = mean_absolute_error(y_valid, pred)
            rmse = np.sqrt(mean_squared_error(y_valid, pred))
            r2 = r2_score(y_valid, pred)
            mape = self.mean_absolute_percentage_error(y_valid, pred)

            # Mostrar métricas
            print(f"\n=== Métricas de Evaluación del Modelo ARIMA ===")
            print(f"MAE  (Error Absoluto Medio): {mae:.2f} → indica promedio de error absoluto.")
            print(f"RMSE (Raíz del Error Cuadrático Medio): {rmse:.2f} → penaliza errores grandes.")
            print(f"R²   (Coeficiente de Determinación): {r2:.2f} → explica la variabilidad de los datos.")
            print(f"MAPE (Error Porcentual Absoluto Medio): {mape:.2f}% → error relativo en porcentaje.\n")

            # Logging con justificación de métricas
            self.logger.info(
                "Modeller",
                "entrenar",
                (
                    f"Entrenamiento exitoso.\n"
                    f"MAE: {mae:.2f} (error promedio absoluto), "
                    f"RMSE: {rmse:.2f} (penaliza errores grandes), "
                    f"R²: {r2:.2f} (explicación de varianza), "
                    f"MAPE: {mape:.2f}% (error relativo porcentual)."
                )
            )

            # Guardar modelo entrenado
            with open(self.model_file, "wb") as f:
                pickle.dump(model_fit, f)

            return True

        except Exception as e:
            self.logger.error("Modeller", "entrenar", f"Error en entrenamiento: {str(e)}")
            return False

    def predecir(self, df, steps=1):
        """
        Carga el modelo desde disco y realiza predicción futura.
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

