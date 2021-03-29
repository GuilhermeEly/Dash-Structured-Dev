# pylint: disable=maybe-no-member
from datetime import datetime as dt
from pathlib import Path
#Bibliotecas para modelagem
import pandas as pd
import sqlite3
import pyodbc
import time

class Database:
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

    def queryFpyByDate(self, startDate, endDate):

        sql = """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                TRY_CONVERT(date,(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA
                FROM SZ2990 AS z2 
                INNER JOIN ZZ8990 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY DATA
            """

        df = pd.read_sql_query(sql, self.conn, params=(startDate, endDate))

        return df

    def queryFpyByDateAndPA(self, startDate, endDate, PASelected):

        PASelected = PASelected.replace(' ', '')
        if PASelected.isdigit()!= True:
            while len(PASelected) < 15:
                PASelected += ' '

        sql = """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                TRY_CONVERT(date,(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA
                FROM SZ2990 AS z2 
                INNER JOIN ZZ8990 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z2.Z2_PRODUTO = (?) AND z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY DATA
            """

        df = pd.read_sql_query(sql, self.conn, params=(PASelected, startDate, endDate))

        return df

    def queryFailCauses(self, startDate, endDate, PASelected):

        sql = """
                SELECT z2.Z2_PRODUTO as PA, z9.ZZ9_SERIAL as NS, z9.ZZ9_STEP as STEP,
                z9.ZZ9_TIPO as TIPO, z9.ZZ9_STATUS as STATUS,z9.R_E_C_N_O_ as RECNO,
                TRY_CONVERT(date,(z9.ZZ9_DATE)) as DATA
                FROM SZ2990 AS z2 
                INNER JOIN ZZ9990 AS z9 ON z2.Z2_SERIE=z9.ZZ9_SERIAL
                WHERE z2.Z2_PRODUTO = (?) AND z9.ZZ9_DATE BETWEEN (?) AND (?) ORDER BY RECNO
            """

        df = pd.read_sql_query(sql, self.conn, params=(PASelected, startDate, endDate))

        return df

    def queryDailyFpyByPA(self, startDate, endDate, PASelected):

        sql = """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                TRY_CONVERT(date,(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA
                FROM SZ2990 AS z2 
                INNER JOIN ZZ8990 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z2.Z2_PRODUTO=(?) AND z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY NS, DATA, HORA
            """


        df = pd.read_sql_query(sql, self.conn, params=(str(PASelected),startDate, endDate))

        return df