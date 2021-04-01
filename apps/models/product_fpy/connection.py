# pylint: disable=maybe-no-member
from datetime import datetime as dt
from pathlib import Path
#Bibliotecas para modelagem
import pandas as pd
import sqlite3
import pyodbc
import time

class connectDatabase:

    connectionType = 'test'

    testData = "C:\\Users\\gely\\Projects\\Dash-Structured\\testdatabase\\testdb.db"

    server = 'nobrcasql01' #Trocar para uma variavel de ambiente
    database = 'FPY' #Trocar para uma variavel de ambiente
    username = 'FPY' #Trocar para uma variavel de ambiente
    password = 'FPY@2020!' #Trocar para uma variavel de ambiente
    driver = 'SQL Server'
    dbc = 'DRIVER={'+driver+'};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password

    realDBZZ8 = "TRY_CONVERT(date,(z8.ZZ8_DATE))"
    realDBZZ9 = "TRY_CONVERT(date,(z9.ZZ9_DATE))"
    testDBZZ8 = "date(z8.ZZ8_DATE)"
    testDBZZ9 = "date(z9.ZZ9_DATE)"



    conn = ''
    choosenDBZZ8 = ''
    choosenDBZZ9 = ''

    def __init__(self):
        if self.connectionType == 'test':
            self.conn = sqlite3.connect(self.testData)
            self.choosenDBZZ8 = self.testDBZZ8
            self.choosenDBZZ9 = self.testDBZZ9
        else:
            self.conn = pyodbc.connect(self.dbc)
            self.choosenDBZZ8 = self.realDBZZ8
            self.choosenDBZZ9 = self.realDBZZ9

    def __del__(self):
        self.conn.close()