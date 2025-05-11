from logger import Logger
from collector import Collector
import pandas as pd


def main():
    logger = Logger()
    df = pd.DataFrame()
    logger.info('Main','main','Inicializar clase Logger')

    collector = Collector(logger=logger)
    logger.info('Main', 'main', 'Inicializando recolección de datos')
    
    df = collector.collector_data()
    
    if df.empty:
        logger.error('Main', 'main', 'No se obtuvieron datos para guardar')
    else:
        logger.info('Main', 'main', f'Datos procesados: {df.shape[0]} filas, {len(df.columns)} columnas')
        logger.info('Main', 'main', f'Columnas disponibles: {df.columns.tolist()}')
        
        required_columns = ['Fecha', 'Dia', 'Mes', 'Año', 'Fecha_Formateada']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning('Main', 'main', f'Faltan columnas requeridas: {missing_columns}')
        else:
            logger.info('Main', 'main', 'Todas las columnas requeridas están presentes')
        
        try:
            file_path = "src/piv/static/data/Meta_Platforms_data.csv"
            df.to_csv(file_path, index=False)
            logger.info('Main', 'main', f'Datos guardados exitosamente en {file_path}')
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info('Main', 'main', f'Archivo creado correctamente. Tamaño: {file_size} bytes')
            else:
                logger.error('Main', 'main', 'No se pudo verificar la creación del archivo')
                
        except Exception as e:
            logger.error('Main', 'main', f'Error al guardar los datos: {e}')
            
if __name__ == "__main__":
    main()