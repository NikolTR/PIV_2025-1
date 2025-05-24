from logger import Logger
from collector import Collector
import pandas as pd
from datetime import datetime

def main():
    logger = Logger()
    logger.info("Main", "main", "Inicializar clase Logger")

    collector = Collector(logger)
    df = collector.collector_data()
    print(f"Columnas después de la recolección: {df.columns.tolist()}")

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

    # ========== EXTRAER DÍA, MES Y AÑO DE LA FECHA ==========
    
    # Añadir columnas de día, mes (en número) y año
    df['dia'] = df['fecha'].dt.day
    
    # Crear una columna para el mes en formato texto en español
    meses = {
        1: 'Enero',
        2: 'Febrero',
        3: 'Marzo',
        4: 'Abril',
        5: 'Mayo',
        6: 'Junio',
        7: 'Julio',
        8: 'Agosto',
        9: 'Septiembre',
        10: 'Octubre',
        11: 'Noviembre',
        12: 'Diciembre'
    }
    
    # Extraer el mes como número y luego convertirlo a texto
    df['mes_num'] = df['fecha'].dt.month
    df['mes'] = df['mes_num'].map(meses)
    
    # Eliminar la columna temporal de mes_num
    df.drop('mes_num', axis=1, inplace=True)
    
    # Añadir columna de año
    df['año'] = df['fecha'].dt.year

    # ========== MOSTRAR DATOS LIMPIOS ==========

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)

    print("\n Vista previa de los datos limpios:")
    print(df.head())
    print(f"\n Dimensión final: {df.shape}")
    print(f" Columnas: {df.columns.tolist()}")

    # ========== FORMATO DE FECHA Y GUARDADO CSV ==========

    df['fecha'] = df['fecha'].dt.strftime('%m/%d/%Y')

    csv_path = "src/piv/static/data/meta_history.csv"
    df.to_csv(csv_path, index=False, float_format='%.2f')  # exporta con punto decimal
    print(f"\n CSV guardado en: {csv_path}")
    
if __name__ == "__main__":
    main()
