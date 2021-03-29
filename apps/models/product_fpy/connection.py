# pylint: disable=maybe-no-member
from datetime import datetime as dt
from pathlib import Path
#Bibliotecas para modelagem
import pandas as pd
import sqlite3
import pyodbc
import time

class connectDatabase:
    server = 'nobrcasql01' #Trocar para uma variavel de ambiente
    database = 'FPY' #Trocar para uma variavel de ambiente
    username = 'FPY' #Trocar para uma variavel de ambiente
    password = 'FPY@2020!' #Trocar para uma variavel de ambiente
    driver = 'SQL Server'
    dbc = 'DRIVER={'+driver+'};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
    conn=''

    def __init__(self):
        self.conn = pyodbc.connect(self.dbc)

    def __del__(self):
        self.conn.close()