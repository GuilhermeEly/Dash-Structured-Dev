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
from dash.dependencies import Input, Output, State
import plotly.express as px
#Bibliotecas para modelagem
import sqlite3
#Caminho da aplicação
from app import app
#funcoes
from apps.function.queries_database import get_fpy_by_Date, get_causes_by_PA, get_timeseries_by_PA, get_fpy_geral

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
                        min_date_allowed=dt(2020, 8, 1),
                        max_date_allowed=dt(2020, 8, 31),
                        start_date_placeholder_text='Data início',
                        end_date_placeholder_text='Data fim',
                        display_format='DD/MM/YYYY'
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
            html.Div(id='fixed-text', children='First Pass Yield Geral:',style={'display': 'inline','margin-left': '150px', 'padding':'6px 24px','font':'Arial'}),
            html.Div(id='output-fpy-button', children='    ',style={'display': 'inline','margin-left': '0px', 'background-color': '#ffffff', 'padding':'6px 24px','font':'Arial', 'border': '2px solid #ccc', 'border-radius': '50px 20px'})
        ]
    ),
    
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
    html.Div([
        html.Div([
            dcc.Loading(id = "loading-fpy-causes", 
                    children=
                    [
                        html.Div([
                            dcc.Graph(id='fpy-causes'),
                        ], style={'display': 'inline-block'}),
                    ], type="graph"),
        ],style={'width': '50%'}),
        html.Div([
            dcc.Loading(id = "loading-time-series-fpy", 
                    children=
                    [
                        html.Div([
                            dcc.Graph(id='time-series-fpy'),
                        ], style={'display': 'inline-block'}),
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

@app.callback(
    Output('crossfilter-indicator-scatter-fpy', 'figure'),
    [Input('submit-button-state', 'n_clicks')],
    [State('crossfilter-yaxis-type-fpy', 'value'),
     State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('PA-Selection', 'value')])
def update_table(n_clicks,Filter,start_date,end_date,PA_selection):

    if Filter!= 'not selected' and start_date!=None and end_date!=None:
        
        data = get_fpy_by_Date(start_date, end_date, Filter, PA_selection)

        fig = px.bar(data, x="PA", y="fpy", title='First Pass Yield',hover_name="NOME", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
        fig.update_xaxes(type='category')
        fig.update_layout(hovermode="x")
        fig.update_layout(clickmode='event+select')

        fig.update_layout(margin={'l': 0, 'b': 0, 't': 50, 'r': 0}, hovermode='closest')
        return fig
    
    else:
        return dash.no_update

@app.callback(
    Output('fpy-causes', 'figure'),
    [Input('crossfilter-indicator-scatter-fpy', 'clickData'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')])
def update_causes(clickData, start_date, end_date):

    if clickData is not None:
        PA_Selected = clickData['points'][0]['x']
    else:
        PA_Selected = "not selected"

    if PA_Selected != "not selected":

        df_causes= get_causes_by_PA(start_date, end_date, PA_Selected)

        title = '<b>{} - Causas</b>'.format(PA_Selected)

        fig = px.bar(df_causes, x="STEP", y="Reprovações", title=title,hover_name="STEP")
        fig.update_xaxes(type='category')

        return fig
    else: 
        return dash.no_update

@app.callback(
    Output('time-series-fpy', 'figure'),
    [Input('crossfilter-indicator-scatter-fpy', 'clickData'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('crossfilter-yaxis-type-fpy', 'value')])
def update_x_timeseries(clickData, start_date, end_date, Filter):

    if clickData is not None:
        PA_Selected = clickData['points'][0]['x']
    else:
        PA_Selected = "not selected"

    if PA_Selected != "not selected":

        df_timeseries= get_timeseries_by_PA(start_date, end_date, PA_Selected, Filter)

        title = '<b>{} - {}</b>'.format(PA_Selected, Filter)
        if Filter == 'Diario':
            fig = px.bar(df_timeseries, x="DateTime", y="fpy", title=title, hover_name="fpy", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
        else:
            fig = px.bar(df_timeseries, x="DateTime", y="fpy", title=title, hover_name="fpy", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
            fig.update_layout(xaxis_type='category')

        return fig
    
    else: 
        return dash.no_update

@app.callback(
    Output('output-fpy-button', 'children'),
    [Input('submit-button-state', 'n_clicks')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('PA-Selection', 'value')])
def update_total_fpy(n_clicks,start_date,end_date,PA_selection):

    if start_date!=None and end_date!=None:
        
        data = get_fpy_geral(start_date, end_date, PA_selection)

        return '{}%'.format(data)
    else:
        return ''