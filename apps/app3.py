import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app


from datetime import datetime as dt

layout = html.Div(
    [
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
    ]
)