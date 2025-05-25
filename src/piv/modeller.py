import os
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


class Modeller:
    def __init__(self, logger):
        self.logger = logger
        self.model_ruta = "src/edu_piv/static/models/"
        self.pkl_ruta = os.path.join(self.model_ruta, "dolar_model.pkl")

        if not os.path.exists(self.model_ruta):
            os.makedirs(self.model_ruta)

    def preparar_df(self, df=pd.DataFrame()):
        df = df.copy()
        try:
            df['year'] = df['fecha'].dt.year
            df['month'] = df['fecha'].dt.month
            df['day'] = df['fecha'].dt.day
            df['dayofweek'] = df['fecha'].dt.dayofweek

            # Definimos X y y
            X = df[['year', 'month', 'day', 'dayofweek']]
            y = df['cierre_ajustado']

            return (X, y), True
        except Exception as e:
            self.logger.log_error(f"Error al preparar el DataFrame: {str(e)}")
            return (pd.DataFrame(), pd.Series()), False

    def entrenar_df(self, df=pd.DataFrame()):
        df = df.copy()
        try:
            (X, y), exito = self.preparar_df(df)
            if not exito:
                return None, False

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)

            # Guardar modelo
            with open(self.pkl_ruta, 'wb') as f:
                pickle.dump(model, f)

            # Evaluación
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            self.logger.log_info(f"Modelo entrenado. MSE: {mse:.2f}, R2: {r2:.4f}")

            return model, True
        except Exception as e:
            self.logger.log_error(f"Error al entrenar modelo: {str(e)}")
            return None, False

    def predecir_df(self, df=pd.DataFrame()):
        df = df.copy()
        try:
            if not os.path.exists(self.pkl_ruta):
                self.logger.log_error("Modelo no encontrado para predicción.")
                return df, False, None, None, None

            with open(self.pkl_ruta, 'rb') as f:
                model = pickle.load(f)

            # Obtener última fila (última fecha conocida)
            df = df.sort_values(by='fecha')
            ultima_fecha = df['fecha'].max()
            nueva_fecha = ultima_fecha + pd.Timedelta(days=1)

            nueva_fila = {
                'fecha': nueva_fecha,
                'year': nueva_fecha.year,
                'month': nueva_fecha.month,
                'day': nueva_fecha.day,
                'dayofweek': nueva_fecha.dayofweek
            }

            df_nuevo = pd.DataFrame([nueva_fila])
            X_new = df_nuevo[['year', 'month', 'day', 'dayofweek']]
            valor_predicho = model.predict(X_new)[0]

            self.logger.log_info(f"Predicción para {nueva_fecha.date()}: {valor_predicho:.2f}")
            return df, True, valor_predicho, nueva_fecha, df.shape[0] - 1
        except Exception as e:
            self.logger.log_error(f"Error al predecir: {str(e)}")
            return df, False, None, None, None
