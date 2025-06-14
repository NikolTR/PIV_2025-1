from logger import Logger
from collector import Collector
from enricher import Enricher
from modeller import Modeller 

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def main():
    logger = Logger()
    logger.info("Main", "main", "Inicializar clase Logger")

    # Obtener datos
    collector = Collector(logger)
    df = collector.collector_data()

    # Quitar columnas duplicadas y limpiar fechas
    df = df.loc[:, ~df.columns.duplicated()]
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])

    columnas_numericas = ['apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado', 'volumen']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # ========== GUARDAR META_HISTORY.CSV ==========
    columnas_base = ['fecha'] + columnas_numericas
    df_crudo = df[columnas_base].copy()
    df_crudo['fecha'] = df_crudo['fecha'].dt.strftime('%m/%d/%Y')
    path_crudo = "src/piv/static/data/meta_history.csv"
    df_crudo.to_csv(path_crudo, index=False, float_format='%.2f')
    print(f"CSV crudo guardado: {path_crudo}")

    # ========== ENRIQUECER Y GUARDAR META_DATA_ENRICHER.CSV ==========
    enricher = Enricher(logger)
    df_enriched = enricher.calcular_kpi(df_crudo.copy())

    columnas_finales = columnas_base + ['dia', 'mes', 'año', 'retorno_diario', 'retorno_acumulado',
                                        'tasa_variacion_ac', 'media_movil_5d', 'volatilidad']

    df_enriched['fecha'] = pd.to_datetime(df_enriched['fecha']).dt.strftime('%m/%d/%Y')
    df_enriched_final = df_enriched[columnas_finales].copy()
    path_enriched = "src/piv/static/data/meta_data_enricher.csv"
    df_enriched_final.to_csv(path_enriched, index=False, float_format='%.4f')
    print(f"CSV enriquecido guardado: {path_enriched}")

    # ========== ENTRENAR Y GUARDAR MODELO ==========
    modeller = Modeller(logger)
    
    # Convertir fechas de vuelta a datetime para el entrenamiento
    df_para_modelo = df_crudo.copy()
    df_para_modelo['fecha'] = pd.to_datetime(df_para_modelo['fecha'])
    
    resultado_entrenamiento = modeller.entrenar(df_para_modelo)

    if resultado_entrenamiento:
        print("Modelo entrenado y guardado correctamente.")
        
        # ========== GENERAR PREDICCIONES ==========
        generar_archivo_predicciones(df_para_modelo, modeller, enricher, logger)
        
    else:
        print("Error al entrenar o guardar el modelo.")

    # Control visual
    print("\n--- Vista previa crudo ---")
    print(df_crudo.head())
    print("\n--- Vista previa enriquecido ---")
    print(df_enriched_final.head())


def generar_archivo_predicciones(df_historico, modeller, enricher, logger):
    """
    Genera solo el archivo de predicciones
    """
    try:
        # Configuración de predicciones
        dias_prediccion = 30  # Predecir 30 días hacia el futuro
        
        # Obtener la última fecha del dataset histórico
        ultima_fecha = df_historico['fecha'].max()
        
        # Generar predicciones usando el modelo ARIMA
        predicciones = modeller.predecir(df_historico, steps=dias_prediccion)
        
        if not predicciones:
            print("No se pudieron generar predicciones")
            return
        
        # Crear fechas futuras (excluyendo fines de semana para datos financieros)
        fechas_futuras = []
        fecha_actual = ultima_fecha + timedelta(days=1)
        
        while len(fechas_futuras) < dias_prediccion:
            # Solo agregar días laborables (lunes a viernes)
            if fecha_actual.weekday() < 5:  # 0=lunes, 4=viernes
                fechas_futuras.append(fecha_actual)
            fecha_actual += timedelta(days=1)
        
        # Obtener estadísticas del último mes para generar valores realistas
        ultimo_mes = df_historico.tail(20)  # Últimos 20 días de trading
        
        # Calcular promedios y volatilidades para generar valores coherentes
        promedio_volumen = ultimo_mes['volumen'].mean()
        volatilidad_precio = ultimo_mes['cerrar'].std()
        ultimo_precio = ultimo_mes['cierre_ajustado'].iloc[-1]
        
        # Crear DataFrame base de predicciones
        df_predicciones = pd.DataFrame()
        df_predicciones['fecha'] = fechas_futuras
        
        # Usar las predicciones del modelo ARIMA para cierre_ajustado y cerrar
        df_predicciones['cierre_ajustado'] = predicciones
        df_predicciones['cerrar'] = predicciones
        
        # Generar valores sintéticos pero realistas para otras columnas
        np.random.seed(42)  # Para reproducibilidad
        
        apertura_values = []
        alto_values = []
        bajo_values = []
        volumen_values = []
        
        for i, precio_cierre in enumerate(predicciones):
            # Generar apertura con pequeña variación del cierre anterior
            if i == 0:
                apertura = ultimo_precio * (1 + np.random.normal(0, 0.005))
            else:
                apertura = predicciones[i-1] * (1 + np.random.normal(0, 0.005))
            
            # Alto y bajo basados en volatilidad histórica
            volatilidad_diaria = volatilidad_precio * np.random.uniform(0.5, 1.5)
            alto = max(apertura, precio_cierre) * (1 + abs(np.random.normal(0, volatilidad_diaria/precio_cierre)))
            bajo = min(apertura, precio_cierre) * (1 - abs(np.random.normal(0, volatilidad_diaria/precio_cierre)))
            
            # Volumen con variación realista
            volumen = int(promedio_volumen * np.random.uniform(0.7, 1.3))
            
            apertura_values.append(apertura)
            alto_values.append(alto)
            bajo_values.append(bajo)
            volumen_values.append(volumen)
        
        df_predicciones['apertura'] = apertura_values
        df_predicciones['alto'] = alto_values
        df_predicciones['bajo'] = bajo_values
        df_predicciones['volumen'] = volumen_values
        
        # ========== ENRIQUECER DATOS DE PREDICCIONES ==========
        # Aplicar enriquecimiento a las predicciones
        df_predicciones_enriquecido = enricher.calcular_kpi(df_predicciones.copy())
        
        # Agregar columna tipo para identificar como predicción
        df_predicciones_enriquecido['tipo'] = 'prediccion'
        
        # Formatear fecha para consistencia
        df_predicciones_enriquecido['fecha'] = pd.to_datetime(df_predicciones_enriquecido['fecha']).dt.strftime('%m/%d/%Y')
        
        # ========== GUARDAR ARCHIVO DE PREDICCIONES ==========
        path_predicciones = "src/piv/static/data/meta_predicciones.csv"
        df_predicciones_enriquecido.to_csv(path_predicciones, index=False, float_format='%.4f')
        
        print(f"\n=== Archivo de Predicciones Generado ===")
        print(f"CSV predicciones: {path_predicciones}")
        print(f"Días predichos: {dias_prediccion}")
        print(f"Rango de fechas predichas: {fechas_futuras[0].strftime('%Y-%m-%d')} a {fechas_futuras[-1].strftime('%Y-%m-%d')}")
        print(f"Total registros de predicción: {len(df_predicciones_enriquecido)}")
        
        # Mostrar muestra de las predicciones
        print("\n--- Vista previa predicciones ---")
        print(df_predicciones_enriquecido.head(3)[['fecha', 'cerrar', 'retorno_diario', 'tipo']])
        
        # Log de éxito
        logger.info("Main", "generar_archivo_predicciones", 
                   f"Archivo de predicciones generado exitosamente. Total: {len(df_predicciones_enriquecido)} registros")
        
    except Exception as e:
        print(f"Error al generar archivo de predicciones: {str(e)}")
        logger.error("Main", "generar_archivo_predicciones", f"Error: {str(e)}")


if __name__ == "__main__":
    main()