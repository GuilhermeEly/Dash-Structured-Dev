# pylint: disable=maybe-no-member
from datetime import datetime as dt
from pathlib import Path
#Bibliotecas para modelagem
import pandas as pd
import sqlite3
import pyodbc
import time
from apps.models.product_fpy.FPYQueries import queriesFPY

def get_fpy_by_Date(start_date, end_date, Filter, PA_selection, limit_High, limit_Low):

    fetch = queriesFPY()

    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')
    
    if PA_selection == None or PA_selection == '':
        df_update_data = fetch.queryFpyByDate(startDate=start_date, endDate=end_date)
    else:
        df_update_data = fetch.queryFpyByDateAndPA(startDate=start_date, endDate=end_date, PASelected=PA_selection)

    df_products = df_update_data.drop_duplicates(subset = ["PA"])

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

    dfFinal.loc[(dfFinal['fpy'] == 0), 'fpy'] = 0.005

    dfFinal = dfFinal[(dfFinal['fpy'] >= float(limit_Low)/100.0) & (dfFinal['fpy'] <= float(limit_High)/100.0)]

    dfFinal['PA'] = dfFinal['PA'].map(str)

    dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

    dfFinal = dfFinal[dfFinal['Produzido']>10]

    dfFinal = dfFinal.join(df_products, on='PA')

    return dfFinal