import os
from pathlib import Path
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
from app import app
import sqlite3
import dash_table

import pandas as pd

base_path = Path(__file__).parent
database = (base_path / r"..\Database\data\fpy_mockup.db").resolve()
conn = sqlite3.connect(database)

cur = conn.cursor()

layout = html.Div([
    html.Div([
        html.Div([
        'Busca por PA: ',
            dcc.Input(
                id='PA',
                placeholder='Busque um PA',
                type='text'
            )  
        ],
        style={'width': '48%', 'display': 'inline-block'}),
        html.Button(id='submit-button-state', n_clicks=0, children='Submit'),

        dcc.Graph(id='indicator-graphic-FPY'),
    ]),
])

@app.callback(
    Output('indicator-graphic-FPY', 'figure'),
    [Input('submit-button-state', 'n_clicks')],
    [State('PA', 'value')])
def update_table(n_clicks,PA_Filter):

    if PA_Filter!= None:

        base_path = Path(__file__).parent
        database = (base_path / r"..\Database\data\fpy_mockup.db").resolve()

        conn = sqlite3.connect(database)

        df_update_data = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                z8.ZZ8_DATE as DATA, z8.ZZ8_HOUR as HORA
                FROM SZ2 AS z2 
                INNER JOIN ZZ8 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z2.Z2_PRODUTO=(?) ORDER BY NS, DATA, HORA
            """, conn, params=(str(PA_Filter),))

        df_update_data.TIPO[df_update_data.TIPO == 1] = 'Calibração'
        df_update_data.TIPO[df_update_data.TIPO == 2] = 'Validação'
        df_update_data.STATUS[df_update_data.STATUS == 'A'] = 'Aprovado'
        df_update_data.STATUS[df_update_data.STATUS == 'R'] = 'Reprovado'

        dfrep = df_update_data.loc[(df_update_data['STATUS'] == "Reprovado")].drop_duplicates(subset = ["NS"])

        SNRep = dfrep.filter(['NS'], axis=1)

        dfRlyApproved = df_update_data[~df_update_data.NS.isin(SNRep.NS)].drop_duplicates(subset = ["NS"])

        dftest = dfrep.groupby(['DATA']).size().reset_index(name='counts')

        dfApprTest = dfRlyApproved.groupby(['DATA']).size().reset_index(name='counts')

        dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='DATA').fillna(0)

        dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

        dfFinal[['DATA', 'fpy']].fillna(0)

        dfFinal = dfFinal.sort_values(by=['DATA'])

        dfFinal.fpy[dfFinal.fpy == 0] = 0.005

        dfFinal['DateTime'] = pd.to_datetime(dfFinal['DATA'].astype(str), format='%Y%m%d')

        dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

        

        print(dfFinal)

        fig = px.bar(dfFinal, x='DateTime', y=dfFinal["fpy"], title='First Pass Yield')

        return fig
    
    else:
        return dash.no_update