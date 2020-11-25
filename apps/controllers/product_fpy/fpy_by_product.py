# pylint: disable=maybe-no-member
from datetime import datetime as dt
from pathlib import Path
#Bibliotecas para modelagem
import pandas as pd
import sqlite3
import pyodbc
import time

def get_fpy_by_Date(start_date, end_date, Filter, PA_selection, limit_High, limit_Low):

    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')

    server = 'nobrpoaerp01' 
    database = 'FPY' 
    username = 'FPY' 
    password = 'FPY@2020!' 
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    
    if PA_selection == None or PA_selection == '':
        df_update_data = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                TRY_CONVERT(date,(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA
                FROM SZ2990 AS z2 
                INNER JOIN ZZ8990 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY DATA
            """, conn, params=(start_date, end_date))
    else:
        PA_selection = PA_selection.replace(' ', '')
        if PA_selection.isdigit()!= True:
            while len(PA_selection) < 15:
                PA_selection += ' '

        df_update_data = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                TRY_CONVERT(date,(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA
                FROM SZ2990 AS z2 
                INNER JOIN ZZ8990 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z2.Z2_PRODUTO = (?) AND z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY DATA
            """, conn, params=(PA_selection, start_date, end_date))

    df_products = df_update_data.drop_duplicates(subset = ["PA"])
    df_products['PA'] = df_products['PA'].map(str)
    df_products = df_products.set_index('PA')

    dfrep = df_update_data.loc[(df_update_data['STATUS'] == "R")].drop_duplicates(subset = ["NS"])

    SNRep = dfrep.filter(['NS'], axis=1)

    dfRlyApproved = df_update_data[~df_update_data.NS.isin(SNRep.NS)].drop_duplicates(subset = ["NS"])

    dftest = dfrep.groupby(['PA']).size().reset_index(name='counts')

    dfApprTest = dfRlyApproved.groupby(['PA']).size().reset_index(name='counts')

    dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='PA').fillna(0)

    dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

    dfFinal['Produzido'] = dfFinal['counts_y'] + dfFinal['counts_x']

    dfFinal.rename(columns={"counts_y": "Aprovadas", "counts_x": "Reprovadas"}, inplace=True)

    dfFinal[['PA', 'fpy']].fillna(0)

    dfFinal = dfFinal.sort_values(by=['fpy'])

    dfFinal.fpy[dfFinal.fpy == 0] = 0.005

    dfFinal = dfFinal[(dfFinal['fpy'] >= float(limit_Low)/100.0) & (dfFinal['fpy'] <= float(limit_High)/100.0)]

    dfFinal['PA'] = dfFinal['PA'].map(str)

    dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

    dfFinal = dfFinal[dfFinal['Produzido']>10]

    dfFinal = dfFinal.join(df_products, on='PA')

    return dfFinal