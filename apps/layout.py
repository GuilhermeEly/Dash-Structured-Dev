# pylint: disable=maybe-no-member
#Bibliotecas do Sistema
from datetime import datetime as dt
import time
import os
from pathlib import Path
#Bibliotecas Web/Gráficas
import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.express as px

import apps.callback

layout = html.Div([
    html.Div(
        className='Header-Style',
        children=
        [
            html.Div(
                className='Header-Disposition',
                children =
                [
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date_placeholder_text='Data início',
                        end_date_placeholder_text='Data fim',
                        display_format='DD/MM/YYYY',
                        minimum_nights=0
                    ),
                    html.Div([
                        dcc.Input(
                            className = 'PA-Input',
                            id='PA-Selection',
                            placeholder='Busque um PA',
                            type='text',
                        )
                    ],style={'display': 'inline-block'}),
                    html.Button(
                        id='submit-button-state', 
                        n_clicks=0, 
                        children='Submit',
                        className = 'Submit-Button'
                    ),
                    
                ]
            ),
            html.Div(className = 'fpy-header-filter', id='fixed-text', children=[
                                    'FPY de',
                                    html.Div([
                                        dcc.Input(
                                            className = 'fpy-filter',
                                            id='fpy-filter-low',
                                            value='0',
                                            type='number',
                                            min='0',
                                            max='100'
                                        )
                                    ],style={'display': 'inline'}),
                                    'à',
                                    html.Div([
                                        dcc.Input(
                                            className = 'fpy-filter',
                                            id='fpy-filter-high',
                                            value='100',
                                            type='number',
                                            min='0',
                                            max='100'
                                        )
                                    ],style={'display': 'inline'}),
                                    'First Pass Yield Geral:'
                                    ],style={'display': 'inline','margin-left': '10px', 'padding':'6px 24px','font':'Arial'}),
            html.Div(id='output-fpy-button', children='    ',style={'display': 'inline','margin-left': '0px', 'background-color': '#ffffff', 'padding':'6px 24px','font':'Arial', 'border': '2px solid #ccc', 'border-radius': '50px 20px'})
        ]
    ),
    html.Div([
        dcc.Loading(id = "loading-indicator-scatter-fpy", 
                children=
                [
                    html.Div([
                        dcc.Graph(
                            id='crossfilter-indicator-scatter-fpy',
                            hoverData={'points': [{'x': 'not selected'}]}
                        )
                    ], style={'width': '100%', 'padding': '0 20'}),
                ], type="graph"),
    ],style={'width': '100%'}),
    html.Div([
        html.Div([
            dcc.Loading(id = "loading-fpy-causes", 
                    children=
                    [
                        html.Div([
                            dcc.Graph(id='fpy-causes'),
                        ], style={'display': 'inline-block','width': '100%'}),
                    ], type="graph"),
        ],style={'width': '50%'}),
        html.Div([
            dcc.Loading(id = "loading-time-series-fpy", 
                    children=
                    [
                        html.Div([
                            dcc.Graph(id='time-series-fpy'),
                        ], style={'display': 'inline-block','width': '100%'}),
                    ], type="graph"),
        ],style={'width': '50%'})
    ],style={'display': 'flex', 'width': '100%'}),
    
    html.Div([
            dcc.RadioItems(
                id='crossfilter-yaxis-type-fpy',
                options=[{'label': i, 'value': i} for i in ['Diario', 'Semanal', 'Mensal', 'Anual']],
                value='Diario',
                labelStyle={'display': 'inline-block'}
            ),
        ], style={
            'width': '34%', 
            'float': 'right', 
            'display': 'inline-block',
            })
])