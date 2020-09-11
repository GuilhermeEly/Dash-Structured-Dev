import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
from app import app
import sqlite3
import dash_table

import pandas as pd

database = r"C:\Users\gely\dash_plotly\test\StructuredProject\Database\data\fpy_mockup.db"
conn = sqlite3.connect(database)

cur = conn.cursor()

query = """
            SELECT z2.Z2_PRODUTO, z8.ZZ8_NUMEQ, z8.ZZ8_PNAME, z8.ZZ8_TIPO, z8.ZZ8_NUMBER
            FROM SZ2 AS z2 
            INNER JOIN ZZ8 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
            WHERE z8.ZZ8_NUMBER=16420930
        """

dfsql = pd.read_sql_query(query, conn)


print(dfsql)

dfo = pd.read_csv(r'apps\dataset\data.csv')
dfo.columns =[column.replace(" ", "_") for column in dfo.columns]

#Transforma a coluna Data_Calibra em datetime
dfo['Data_Calibra'] = pd.to_datetime(dfo['Data_Calibra'],format=r'%d/%m/%Y')

Available_Filters = dfo.drop('Data_Calibra', 1)

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
        database = r"C:\Users\gely\dash_plotly\test\StructuredProject\Database\data\fpy_mockup.db"
        conn = sqlite3.connect(database)

        query2 = """
                SELECT z2.Z2_PRODUTO, z8.ZZ8_NUMEQ, z8.ZZ8_PNAME, z8.ZZ8_TIPO, z8.ZZ8_NUMBER
                FROM SZ2 AS z2 
                INNER JOIN ZZ8 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z2.Z2_PRODUTO="""+str(PA_Filter)

        print(query2)

        dfsql2 = pd.read_sql_query(query2, conn)
        dfsql2.ZZ8_TIPO[dfsql2.ZZ8_TIPO == 1] = 'Calibração'
        dfsql2.ZZ8_TIPO[dfsql2.ZZ8_TIPO == 2] = 'Validação'
        print(dfsql2)

        return dfsql2.to_dict('records')
    