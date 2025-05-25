from logger import Logger
from collector import Collector
import pandas as pd
from enricher import Enricher
import os

def main():
    logger = Logger()
    logger.info("Main", "main", "Inicializar clase Logger")

    collector = Collector(logger)
    df = collector.collector_data()

    # ========== LIMPIEZA DE DATOS ==========

    df = df.loc[:, ~df.columns.duplicated()]
    df['fecha'] = pd.to_datetime(df['fecha'], format='%m/%d/%Y', errors='coerce')
    df = df.dropna(subset=['fecha'])

    columnas_numericas = ['apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado', 'volumen']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Seleccionar solo columnas crudas
    columnas_crudas = ['fecha', 'apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado', 'volumen']
    df_crudo = df[columnas_crudas].copy()

    # ========== ENRIQUECER DATOS CON KPIs ==========
    enricher = Enricher(logger)
    df_enriched = enricher.calcular_kpi(df_crudo.copy())  # Importante: enriquecer solo desde crudo

    # ========== GUARDADO DE CSVs ==========
    os.makedirs('src/piv/static/data', exist_ok=True)

    # Guardar CSV crudo
    df_crudo['fecha'] = df_crudo['fecha'].dt.strftime('%m/%d/%Y')
    df_crudo.to_csv("src/piv/static/data/meta_history.csv", index=False, float_format='%.2f')
    print("✅ CSV crudo guardado en: src/piv/static/data/meta_history.csv")

    # Guardar CSV enriquecido
    df_enriched['fecha'] = pd.to_datetime(df_enriched['fecha'], errors='coerce').dt.strftime('%m/%d/%Y')
    df_enriched.to_csv("src/piv/static/data/meta_data_enricher.csv", index=False, float_format='%.4f')
    print("✅ CSV enriquecido guardado en: src/piv/static/data/meta_data_enricher.csv")

if __name__ == "__main__":
    main()

