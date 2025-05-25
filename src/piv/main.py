from logger import Logger
from collector import Collector
from enricher import Enricher
import pandas as pd
import os

def main():
    logger = Logger()
    logger.info("Main", "main", "Inicializar clase Logger")

    # === 1. RECOLECTAR DATOS CRUDOS ===
    collector = Collector(logger)
    df = collector.collector_data()

    df = df.loc[:, ~df.columns.duplicated()]
    df['fecha'] = pd.to_datetime(df['fecha'], format='%m/%d/%Y', errors='coerce')
    df = df.dropna(subset=['fecha'])

    columnas_numericas = ['apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado', 'volumen']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # === 2. GUARDAR CSV CRUDOS ANTES DE ENRIQUECER ===
    df_crudo = df[['fecha', 'apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado', 'volumen']].copy()
    df_crudo['fecha'] = df_crudo['fecha'].dt.strftime('%m/%d/%Y')

    os.makedirs('src/piv/static/data', exist_ok=True)
    path_crudo = "src/piv/static/data/meta_history.csv"
    df_crudo.to_csv(path_crudo, index=False, float_format='%.2f')
    print(f"✅ CSV crudo guardado en: {path_crudo}")

    # === 3. ENRIQUECER CON KPIs ===
    enricher = Enricher(logger)

    df_enriched = enricher.calcular_kpi(df.copy())
    df_enriched['fecha'] = df_enriched['fecha'].dt.strftime('%m/%d/%Y')

    path_enriched = "src/piv/static/data/meta_data_enricher.csv"
    df_enriched.to_csv(path_enriched, index=False, float_format='%.4f')
    print(f"✅ CSV enriquecido guardado en: {path_enriched}")

if __name__ == "__main__":
    main()


