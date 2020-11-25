# pylint: disable=maybe-no-member
from datetime import datetime as dt
from pathlib import Path
#Bibliotecas para modelagem
import pandas as pd
import sqlite3
import pyodbc
import time

def get_causes_by_PA(start_date, end_date, PA):
    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')

    server = 'nobrpoaerp01' 
    database = 'FPY' 
    username = 'FPY' 
    password = 'FPY@2020!' 
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        
    df_update_data = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z9.ZZ9_SERIAL as NS, z9.ZZ9_STEP as STEP,
                z9.ZZ9_TIPO as TIPO, z9.ZZ9_STATUS as STATUS,
                TRY_CONVERT(date,(z9.ZZ9_DATE)) as DATA
                FROM SZ2990 AS z2 
                INNER JOIN ZZ9990 AS z9 ON z2.Z2_SERIE=z9.ZZ9_SERIAL
                WHERE z2.Z2_PRODUTO = (?) AND z9.ZZ9_DATE BETWEEN (?) AND (?) ORDER BY DATA
            """, conn, params=(PA, start_date, end_date))

    dfREP = df_update_data[df_update_data.STATUS != 'A']

    dftest = dfREP.groupby(['STEP','STATUS']).size().reset_index(name='Reprovações')

    dfFinal = dftest.sort_values(by=['Reprovações'], ascending=False)

    return dfFinal