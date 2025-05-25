from logger import Logger
from collector import Collector
import pandas as pd
from enricher import Enricher
from datetime import datetime

def main():
    logger = Logger()
    logger.info("Main", "main", "Inicializar clase Logger")

    collector = Collector(logger)
    df = collector.collector_data()

    # ========== LIMPIEZA DE DATOS ==========

    # Quitar columnas duplicadas
    df = df.loc[:, ~df.columns.duplicated()]

    # Convertir columna de fecha y eliminar filas sin fecha
    df['fecha'] = pd.to_datetime(df['fecha'], format='%m/%d/%Y', errors='coerce')
    df = df.dropna(subset=['fecha'])

    # Convertir columnas numéricas en el DataFrame crudo
    columnas_numericas = ['apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado', 'volumen']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # ========== DATAFRAME CRUDO ==========

    columnas_base = ['fecha', 'apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado', 'volumen']
    df_crudo = df[columnas_base].copy()

    # Formato fecha para archivo crudo
    df_crudo['fecha'] = df_crudo['fecha'].dt.strftime('%m/%d/%Y')

    # Guardar archivo crudo
    csv_path_crudo = "src/piv/static/data/meta_history.csv"
    df_crudo.to_csv(csv_path_crudo, index=False, float_format='%.2f')
    print(f"CSV crudo guardado en: {csv_path_crudo}")

    # ========== DATAFRAME ENRIQUECIDO ==========

    enricher = Enricher(logger)
    df_enriched = enricher.calcular_kpi(df_crudo.copy())

    columnas_enriched = ['fecha', 'apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado', 
                        'volumen', 'dia', 'mes', 'año', 'retorno_diario', 'retorno_acumulado', 
                        'tasa_variacion_ac', 'media_movil_5d', 'volatilidad']

    df_enriched_final = df_enriched[columnas_enriched].copy()

    # Formato fecha para archivo enriquecido
    df_enriched_final['fecha'] = pd.to_datetime(df_enriched_final['fecha']).dt.strftime('%m/%d/%Y')

    # Guardar archivo enriquecido
    csv_path_enriched = "src/piv/static/data/meta_data_enricher.csv"
    df_enriched_final.to_csv(csv_path_enriched, index=False, float_format='%.4f')
    print(f"CSV enriquecido guardado en: {csv_path_enriched}")

    # ========== IMPRESIÓN DE CONTROL ==========
    print("\n--- DataFrame crudo (primeras filas) ---")
    print(df_crudo.head())
    print(f"Columnas: {df_crudo.columns.tolist()}")

    print("\n--- DataFrame enriquecido (primeras filas) ---")
    print(df_enriched_final.head())
    print(f"Columnas: {df_enriched_final.columns.tolist()}")
    
if __name__ == "__main__":
    main()

