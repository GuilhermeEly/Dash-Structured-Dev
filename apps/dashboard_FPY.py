import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from app import app

import pandas as pd

dfo = pd.read_csv(r'apps\dataset\data.csv')
dfo.columns =[column.replace(" ", "_") for column in dfo.columns]

#Transforma a coluna Data_Calibra em datetime
dfo['Data_Calibra'] = pd.to_datetime(dfo['Data_Calibra'],format=r'%d/%m/%Y')

Available_Filters = dfo.drop('Data_Calibra', 1)

layout = html.Div([
    html.Div([

        html.Div([
            dcc.DatePickerRange(
            id='date-picker-range',
            start_date_placeholder_text='Data início',
            end_date_placeholder_text='Data fim'
        ),
            dcc.Input(
                id='OP',
                placeholder='Busque uma OP',
                type='text',
                value=''
            )  
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        # html.Div([
        #     dcc.Dropdown(
        #         id='Filter-SubAggregation',
        #         options=[{'label': i, 'value': i} for i in available_indicators],
        #     )
        # ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),




])