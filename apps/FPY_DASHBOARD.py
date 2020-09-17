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
from app import app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def get_fpy(start_date, end_date, Filter):

    start_date = dt.strptime(start_date, "%Y-%m-%d")
    end_date = dt.strptime(end_date, "%Y-%m-%d")

    base_path = Path(__file__).parent
    database = (base_path / r"..\Database\data\fpy_mockup2.db").resolve()
    conn = sqlite3.connect(database)
    
    df_update_data = pd.read_sql_query(
        """
            SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
            z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
            (date(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA, (strftime("%Y", z8.ZZ8_DATE) || strftime("%W", z8.ZZ8_DATE)) as SEMANA
            FROM SZ2 AS z2 
            INNER JOIN ZZ8 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
            WHERE z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY DATA
        """, conn, params=(start_date, end_date))

    return df_update_data

layout = html.Div([
    html.Div([

        html.Div([
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=dt(2020, 8, 1),
                max_date_allowed=dt(2020, 8, 31),
                start_date_placeholder_text='Data início',
                end_date_placeholder_text='Data fim',
                display_format='DD/MM/YYYY'
            ),
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([

            dcc.RadioItems(
                id='crossfilter-yaxis-type-fpy',
                options=[{'label': i, 'value': i} for i in ['Diario', 'Semanal', 'Mensal', 'Anual']],
                value='not selected',
                labelStyle={'display': 'inline-block'}
            ),
            html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),
    

    html.Div([
        dcc.Graph(id='crossfilter-indicator-scatter-fpy',
                  hoverData={'points': [{'customdata': 'Japan'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '49%'}),
])

@app.callback(
    Output('crossfilter-indicator-scatter-fpy', 'figure'),
    [Input('submit-button-state', 'n_clicks')],
    [State('crossfilter-yaxis-type-fpy', 'value'),
     State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date')])
def update_table(n_clicks,Filter,start_date,end_date):

    if Filter!= 'not selected' and start_date!=None and end_date!=None:
        
        print(get_fpy(start_date, end_date, Filter))

        return dash.no_update
    
    else:
        return dash.no_update
