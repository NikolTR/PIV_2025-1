from logger import Logger
from collector import Collector
import pandas as pd


def main():
    logger = Logger()
    df = pd.DataFrame()
    logger.info('Main','main','Inicializar clase Logger')
    collector = Collector(logger=logger)
    df =collector.collector_data()
    df.to_csv("/src/piv/static/data/Meta_Platforms_data.csv")



if __name__ == "__main__":
    main()