# pylint: disable=maybe-no-member
from datetime import datetime as dt
from pathlib import Path
#Bibliotecas para modelagem
import pandas as pd
import sqlite3
import pyodbc
import time

from apps.models.product_fpy.FPYQueries import queriesFPY

def get_timeseries_by_PA(start_date, end_date, PA, Filterx):
    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')

    fetch = queriesFPY()

    df_update_data = fetch.queryDailyFpyByPA(startDate=start_date, endDate=end_date, PASelected=PA)
    df_update_data['DATA'] = pd.to_datetime(df_update_data['DATA'])

    if Filterx == 'Semanal':
        df_update_data['Filtro'] = df_update_data['DATA'].dt.strftime('%Y-%U')
    if Filterx == 'Mensal':
        df_update_data['Filtro'] = df_update_data['DATA'].dt.strftime('%Y-%m')
    if Filterx == 'Anual':
        df_update_data['Filtro'] = df_update_data['DATA'].dt.strftime('%Y')
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

    else:
        
        #Agrupa REPROVADOS por DATA e faz a contagem das REPROVAÇÕES
        dftest = dfrep.groupby(['Filtro']).size().reset_index(name='counts')

        #Agrupa APROVADOS por DATA e faz a contagem das APROVAÇÕES
        dfApprTest = dfRlyApproved.groupby(['Filtro']).size().reset_index(name='counts')

        #Junta a tabela de reprovados com aprovados, usando como referência a data. Retorna 0 para valores NaN.
        dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='Filtro').fillna(0)

        #Calcula o indicador First Pass Yield
        dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

        #Calcula total produzido
        dfFinal['Produzido'] = dfFinal['counts_y'] + dfFinal['counts_x']

        #Renomeia as colunas da tabela
        dfFinal.rename(columns={"counts_y": "Aprovadas", "counts_x": "Reprovadas"}, inplace=True)

        #Retorna 0 para valores NaN de First Pass Yield
        dfFinal[['Filtro', 'fpy']].fillna(0)

        #Ordena a tabela conforme a DATA
        dfFinal = dfFinal.sort_values(by=['Filtro'])

        #Para melhor visualizar os dias com FPY de 0% foi determinado o valor abaixo para ser plotado
        dfFinal.fpy[dfFinal.fpy == 0] = 0.005

        #Converte a coluna para o formato YYYY-MM-DD para realizar o plot
        dfFinal['DateTime'] = dfFinal['Filtro'].astype(str)

        #Formata o indicador First Pass Yield como porcentagem
        dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

    dfFinal = dfFinal[dfFinal['Produzido']>10]

    return dfFinal