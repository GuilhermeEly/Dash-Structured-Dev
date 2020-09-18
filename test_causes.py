from datetime import datetime as dt
import time

import os
from pathlib import Path
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import sqlite3

start_date = dt.strptime("2020-08-01", "%Y-%m-%d")
end_date = dt.strptime("2020-08-30", "%Y-%m-%d")
PA_Filter = "8806030306"

base_path = Path(__file__).parent
database = (base_path / r".\Database\data\fpy_mockup2.db").resolve()

conn = sqlite3.connect(database)

df_update_data = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                (date(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA
                FROM SZ2 AS z2 
                INNER JOIN ZZ8 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z2.Z2_PRODUTO=(?) AND z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY NS, DATA, HORA
            """, conn, params=(str(PA_Filter),start_date, end_date))

print(df_update_data)
dfrep = df_update_data.loc[(df_update_data['STATUS'] == "R")].drop_duplicates(subset = ["NS"])

SNRep = dfrep.filter(['NS'], axis=1)

dfRlyApproved = df_update_data[~df_update_data.NS.isin(SNRep.NS)].drop_duplicates(subset = ["NS"])

dftest = dfrep.groupby(['DATA']).size().reset_index(name='counts')

dfApprTest = dfRlyApproved.groupby(['DATA']).size().reset_index(name='counts')

dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='DATA').fillna(0)

dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

dfFinal[['DATA', 'fpy']].fillna(0)

dfFinal = dfFinal.sort_values(by=['DATA'])

dfFinal.fpy[dfFinal.fpy == 0] = 0.005

dfFinal['DateTime'] = pd.to_datetime(dfFinal['DATA'].astype(str), format='%Y-%m-%d')

dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

        
print(dfFinal)