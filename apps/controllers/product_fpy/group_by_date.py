# pylint: disable=maybe-no-member
from datetime import datetime as dt
from pathlib import Path
#Bibliotecas para modelagem
import pandas as pd
import sqlite3
import pyodbc
import time

def get_timeseries_by_PA(start_date, end_date, PA, Filterx):
    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')

    server = 'nobrcasql01' 
    database = 'FPY' 
    username = 'FPY' 
    password = 'FPY@2020!' 
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    df_update_data = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                TRY_CONVERT(date,(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA
                FROM SZ2990 AS z2 
                INNER JOIN ZZ8990 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z2.Z2_PRODUTO=(?) AND z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY NS, DATA, HORA
            """, conn, params=(str(PA),start_date, end_date))
    print('query terminada')
    #Pega todos os produtos reprovados pelo menos em uma etapa, removendo os duplicados
    dfrep = df_update_data.loc[(df_update_data['STATUS'] == "R")].drop_duplicates(subset = ["NS"])

    #Retorna apenas o número de série dos produtos reprovados
    SNRep = dfrep.filter(['NS'], axis=1)
    
    #Remove todos os registros de produtos reprovados, inclusive posterior aprovação
    dfRlyApproved = df_update_data[~df_update_data.NS.isin(SNRep.NS)].drop_duplicates(subset = ["NS"])

    if Filterx == 'Diario':

        #Agrupa REPROVADOS por DATA e faz a contagem das REPROVAÇÕES
        dftest = dfrep.groupby(['DATA']).size().reset_index(name='counts')

        #Agrupa APROVADOS por DATA e faz a contagem das APROVAÇÕES
        dfApprTest = dfRlyApproved.groupby(['DATA']).size().reset_index(name='counts')

        #Junta a tabela de reprovados com aprovados, usando como referência a data. Retorna 0 para valores NaN.
        dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='DATA').fillna(0)

        #Calcula o indicador First Pass Yield
        dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

        #Calcula total produzido
        dfFinal['Produzido'] = dfFinal['counts_y'] + dfFinal['counts_x']

        #Renomeia as colunas da tabela
        dfFinal.rename(columns={"counts_y": "Aprovadas", "counts_x": "Reprovadas"}, inplace=True)

        #Retorna 0 para valores NaN de First Pass Yield
        dfFinal[['DATA', 'fpy']].fillna(0)

        #Ordena a tabela conforme a DATA
        dfFinal = dfFinal.sort_values(by=['DATA'])

        #Para melhor visualizar os dias com FPY de 0% foi determinado o valor abaixo para ser plotado
        dfFinal.fpy[dfFinal.fpy == 0] = 0.005

        #Converte a coluna para o formato YYYY-MM-DD para realizar o plot
        dfFinal['DateTime'] = pd.to_datetime(dfFinal['DATA'].astype(str), format='%Y-%m-%d')

        #Formata o indicador First Pass Yield como porcentagem
        dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

    if Filterx == 'Semanal':
        
        #Agrupa REPROVADOS por DATA e faz a contagem das REPROVAÇÕES
        dftest = dfrep.groupby(['SEMANA']).size().reset_index(name='counts')

        #Agrupa APROVADOS por DATA e faz a contagem das APROVAÇÕES
        dfApprTest = dfRlyApproved.groupby(['SEMANA']).size().reset_index(name='counts')

        #Junta a tabela de reprovados com aprovados, usando como referência a data. Retorna 0 para valores NaN.
        dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='SEMANA').fillna(0)

        #Calcula o indicador First Pass Yield
        dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

        #Calcula total produzido
        dfFinal['Produzido'] = dfFinal['counts_y'] + dfFinal['counts_x']

        #Renomeia as colunas da tabela
        dfFinal.rename(columns={"counts_y": "Aprovadas", "counts_x": "Reprovadas"}, inplace=True)

        #Retorna 0 para valores NaN de First Pass Yield
        dfFinal[['SEMANA', 'fpy']].fillna(0)

        #Ordena a tabela conforme a DATA
        dfFinal = dfFinal.sort_values(by=['SEMANA'])

        #Para melhor visualizar os dias com FPY de 0% foi determinado o valor abaixo para ser plotado
        dfFinal.fpy[dfFinal.fpy == 0] = 0.005

        #Converte a coluna para o formato YYYY-MM-DD para realizar o plot
        dfFinal['DateTime'] = dfFinal['SEMANA'].astype(str)

        #Formata o indicador First Pass Yield como porcentagem
        dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

    if Filterx == 'Mensal':

        #Agrupa REPROVADOS por DATA e faz a contagem das REPROVAÇÕES
        dftest = dfrep.groupby(['MES']).size().reset_index(name='counts')

        #Agrupa APROVADOS por DATA e faz a contagem das APROVAÇÕES
        dfApprTest = dfRlyApproved.groupby(['MES']).size().reset_index(name='counts')

        #Junta a tabela de reprovados com aprovados, usando como referência a data. Retorna 0 para valores NaN.
        dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='MES').fillna(0)

        #Calcula o indicador First Pass Yield
        dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

        #Calcula total produzido
        dfFinal['Produzido'] = dfFinal['counts_y'] + dfFinal['counts_x']

        #Renomeia as colunas da tabela
        dfFinal.rename(columns={"counts_y": "Aprovadas", "counts_x": "Reprovadas"}, inplace=True)

        #Retorna 0 para valores NaN de First Pass Yield
        dfFinal[['MES', 'fpy']].fillna(0)

        #Ordena a tabela conforme a DATA
        dfFinal = dfFinal.sort_values(by=['MES'])

        #Para melhor visualizar os dias com FPY de 0% foi determinado o valor abaixo para ser plotado
        dfFinal.fpy[dfFinal.fpy == 0] = 0.005

        #Converte a coluna para o formato YYYY-MM-DD para realizar o plot
        dfFinal['DateTime'] = dfFinal['MES'].astype(str)

        #Formata o indicador First Pass Yield como porcentagem
        dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

    if Filterx == 'Anual':

        #Agrupa REPROVADOS por DATA e faz a contagem das REPROVAÇÕES
        dftest = dfrep.groupby(['ANO']).size().reset_index(name='counts')

        #Agrupa APROVADOS por DATA e faz a contagem das APROVAÇÕES
        dfApprTest = dfRlyApproved.groupby(['ANO']).size().reset_index(name='counts')

        #Junta a tabela de reprovados com aprovados, usando como referência a data. Retorna 0 para valores NaN.
        dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='ANO').fillna(0)

        #Calcula o indicador First Pass Yield
        dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

        #Calcula total produzido
        dfFinal['Produzido'] = dfFinal['counts_y'] + dfFinal['counts_x']

        #Renomeia as colunas da tabela
        dfFinal.rename(columns={"counts_y": "Aprovadas", "counts_x": "Reprovadas"}, inplace=True)

        #Retorna 0 para valores NaN de First Pass Yield
        dfFinal[['ANO', 'fpy']].fillna(0)

        #Ordena a tabela conforme a DATA
        dfFinal = dfFinal.sort_values(by=['ANO'])

        #Para melhor visualizar os dias com FPY de 0% foi determinado o valor abaixo para ser plotado
        dfFinal.fpy[dfFinal.fpy == 0] = 0.005

        #Converte a coluna para o formato YYYY-MM-DD para realizar o plot
        dfFinal['DateTime'] = dfFinal['ANO'].astype(str)

        #Formata o indicador First Pass Yield como porcentagem
        dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

    dfFinal = dfFinal[dfFinal['Produzido']>10]

    return dfFinal