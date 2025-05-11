import requests
import pandas as pd
from bs4 import BeautifulSoup
from logger import Logger
import os

class Collector:
    def __init__(self):
        self.url='https://finance.yahoo.com/quote/META/history/?period1=1337347800&period2=1746921077'
        self.logger = Logger()
        if not os.path.exists('/src/piv/static'):
            os.makedirs('/src/piv/static')
        if not os.path.exists('/src/piv/static/data'):
            os.makedirs('/src/piv/static/data')

    def collector_data(self):
        class_name = self.__class__.__name__
        function_name = 'collector_data'
    
        try:
          df = pd.DataFrame()
          headers= {
             'User-Agent':'Mozilla/5.0'
          }
          response = requests.get(self.url,headers=headers)
          if response.status_code != 200:
             self.logger.error(class_name, function_name, "Error al consultar la url : {}".format(response.status_code))
             return df
          
          soup = BeautifulSoup(response.text,'html.parser')
          table = soup.select_one('div[data-testid="history-table"] table')
          if table is None:
             self.logger.error(class_name, function_name, "Error al buscar la tabla data-testid=history-table")
             return df
          
          headers = [th.get_text(strip=True) for th in table.thead.find_all('th')]
          rows=[]
          for tr in table.tbody.find_all('tr'):
              colums = [td.get_text(strip=True) for td in tr.find_all('td')]
              if len(colums) == len(headers):
                  rows.append(colums)
          df = pd.DataFrame(rows,columns=headers).rename(columns={
                'Fecha':'fecha',
                'Abrir':'abrir',
                'Máx.':'max',
                'Mín.':'min',
                'Precio de cierre ajustado por divisiones.':'cerca',
                'Precio de cierre ajustado por divisiones y distribuciones de dividendos y/o ganancias de capital.':'adj_cerrar',
                'Volumen':'volumen'
            })
          self.logger.info("Datos obtenidos exitosamente {}".format(df.shape))
          return df
        except Exception as error:
          self.logger.error(class_name, function_name, "Error al obtener los datos de la url {error}")
          return df
          
