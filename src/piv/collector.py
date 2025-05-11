import requests
import pandas as pd
from bs4 import BeautifulSoup
from logger import Logger
import os


class Collector:
    def __init__(self):
        self.url='https://finance.yahoo.com/quote/META/history/?period1=1337347800&period2=1746921077'
        self.logger = Logger

    def collector_data(self):