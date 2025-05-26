from logger import Logger
from collector import Collector
from enricher import Enricher
from modeller import Modeller 

import pandas as pd


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
    resultado_entrenamiento = modeller.entrenar(df_crudo)

    if resultado_entrenamiento:
        print("Modelo entrenado y guardado correctamente.")
    else:
        print("Error al entrenar o guardar el modelo.")

    # Control visual
    print("\n--- Vista previa crudo ---")
    print(df_crudo.head())
    print("\n--- Vista previa enriquecido ---")
    print(df_enriched_final.head())


if __name__ == "__main__":
    main()

