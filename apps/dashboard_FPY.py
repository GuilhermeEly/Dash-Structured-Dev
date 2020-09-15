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

dfsql = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME, 
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                z8.ZZ8_DATE as DATA, z8.ZZ8_HOUR as HORA
                FROM SZ2 AS z2 
                INNER JOIN ZZ8 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z2.Z2_PRODUTO=8024009080
            """, conn)

print(dfsql)

df_update_data = pd.read_csv(r'apps\dataset\data.csv')
df_update_data.columns =[column.replace(" ", "_") for column in df_update_data.columns]

#Transforma a coluna Data_Calibra em datetime
df_update_data['Data_Calibra'] = pd.to_datetime(df_update_data['Data_Calibra'],format=r'%d/%m/%Y')

Available_Filters = df_update_data.drop('Data_Calibra', 1)

layout = html.Div([
    html.Div([

        html.Div([
        #    dcc.DatePickerRange(
        #    id='date-picker-range',
        #    start_date_placeholder_text='Data início',
        #    end_date_placeholder_text='Data fim'
        #),
        'Busca por PA: ',
            dcc.Input(
                id='PA',
                placeholder='Busque um PA',
                type='number'
            )  
        ],
        style={'width': '48%', 'display': 'inline-block'}),
        html.Button(id='submit-button-state', n_clicks=0, children='Submit'),

        #dcc.Graph(id='indicator-graphic'),

        html.Div([
            dash_table.DataTable(
                id="Datatable_FPY",
                data=dfsql.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in dfsql.columns],
                page_size=20
            )
        ]),

        # html.Div([
        #     dcc.Dropdown(
        #         id='Filter-SubAggregation',
        #         options=[{'label': i, 'value': i} for i in available_indicators],
        #     )
        # ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
])

@app.callback(
    Output('Datatable_FPY', 'data'),
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
        print(df_update_data)
        print(dfrep)

        SNRep = dfrep.filter(['NS'], axis=1)

        dfRlyApproved = df_update_data[~df_update_data.NS.isin(SNRep.NS)].drop_duplicates(subset = ["NS"])

        print(dfRlyApproved)

        dftest = dfrep.groupby(['DATA']).size().reset_index(name='counts')

        print(dftest)

        #dfApprTest = dfRlyApproved.groupby(['DATA'])['DATA'].value_counts()
        dfApprTest = dfRlyApproved.groupby(['DATA']).size().reset_index(name='counts')

        print(dfApprTest)

        dft = dftest['counts']/(dftest['counts']+dfApprTest['counts'])

        dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='DATA').fillna(0)

        print(dfFinal)

        dfFinal['fpy'] = dfFinal['counts_x'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

        dfFinal[['DATA', 'fpy']].fillna(0)

        print(dfFinal)

        return df_update_data.to_dict('records')
    