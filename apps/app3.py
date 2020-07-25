import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

from app import app


from datetime import datetime as dt

d = {'Day': ['05-23-2020', '05-24-2020', '05-25-2020', '05-26-2020'], 'FPY': [0.5, 0.4, 0.5, 0.6]}

df = pd.DataFrame(data=d)

layout = html.Div(
    [
        html.Div([
            html.H3('App 3'),
            dcc.DatePickerRange(
                id='date-picker-range',
                display_format='DD/MM/YYYY',
                start_date_placeholder_text='Data início',
                end_date_placeholder_text='Data fim'
            ),
            html.Br(),
            html.Br(),
            dcc.Link('Go to Homepage', href='/')
        ]),
        html.Div([
            html.H3('App 3'),
            dcc.Graph(
                id='example-graph',
                figure={
                    'data': [
                        {'x': df['Day'], 'y': df['FPY'], 'type': 'bar', 'name': 'FPY'},
                    ],
                    'layout': {
                        'title': 'Dash Data Visualization'
                    }
                }
            )
        ]),
    ]
)