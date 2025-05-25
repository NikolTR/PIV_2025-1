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

    # Quitar columnas duplicadas
    df = df.loc[:, ~df.columns.duplicated()]

    # Convertir columna de fecha
    df['fecha'] = pd.to_datetime(df['fecha'], format='%m/%d/%Y', errors='coerce')
    df = df.dropna(subset=['fecha'])  # Eliminar filas sin fecha

    # Convertir columnas numéricas sin punto decimal explícito
    columnas_numericas = ['apertura', 'alto', 'bajo', 'cerrar', 'cierre_ajustado', 'volumen']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # ========== ENRIQUECER DATOS CON KPIs ==========
    enricher = Enricher(logger)
    df = enricher.calcular_kpi(df)  # Aquí actualizamos directamente df

    # ========== MOSTRAR DATOS LIMPIOS ==========

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)

    print("\n Vista previa de los datos limpios y enriquecidos:")
    print(df.head())
    print(f"\n Dimensión final: {df.shape}")
    print(f" Columnas: {df.columns.tolist()}")

    # ========== FORMATO DE FECHA Y GUARDADO CSV ==========

    df['fecha'] = df['fecha'].dt.strftime('%m/%d/%Y')

    # Asegurarse que la carpeta existe
    os.makedirs('src/piv/static/data', exist_ok=True)

    csv_path = "src/piv/static/data/meta_history.csv"
    df.to_csv(csv_path, index=False, float_format='%.2f')  # exporta con punto decimal
    print(f"\n CSV guardado en: {csv_path}")

    csv_path_enriched = "src/piv/static/data/meta_data_enricher.csv"
    df.to_csv(csv_path_enriched, index=False, float_format='%.4f')
    print(f"CSV enriquecido guardado en: {csv_path_enriched}")

if __name__ == "__main__":
    main()