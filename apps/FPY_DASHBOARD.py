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
import pandas as pd
#Caminho da aplicação
from app import app
#funcoes
from apps.function.dashboard.queries_dashboard import get_fpy_by_Date, get_causes_by_PA, get_timeseries_by_PA, get_fpy_geral

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

@app.callback(
    Output('crossfilter-indicator-scatter-fpy', 'figure'),
    [Input('submit-button-state', 'n_clicks')],
    [State('crossfilter-yaxis-type-fpy', 'value'),
     State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('PA-Selection', 'value'),
     State('fpy-filter-low', 'value'),
     State('fpy-filter-high', 'value')])
def update_table(n_clicks,Filter,start_date,end_date,PA_selection,limit_Low,limit_High):

    if float(limit_High)<float(limit_Low):
        limit_High = 100
        limit_Low = 0

    if limit_High==None or str(limit_High).isdigit()==False:
        limit_High = 100
    if limit_Low==None or str(limit_Low).isdigit()==False:
        limit_Low = 0

    if Filter!= 'not selected' and start_date!=None and end_date!=None:
        
        data = get_fpy_by_Date(start_date, end_date, Filter, PA_selection, limit_High, limit_Low)

        fig = px.bar(data, x="PA", y="fpy", title='First Pass Yield',hover_name="NOME", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
        fig.update_xaxes(type='category')
        fig.update_layout(
            hovermode="x",
            clickmode='event+select',
            font=dict(
                family="Arial",
                size=20
            ),
            margin={'l': 0, 'b': 0, 't': 50, 'r': 0},
            hoverlabel=dict(
                bgcolor="white",
                font_size=20,
                font_family="Rockwell"
            )
        )
        fig.update_layout(
            hovermode="closest"
        )
        return fig
    
    else:
        return dash.no_update

@app.callback(
    Output('fpy-causes', 'figure'),
    [Input('crossfilter-indicator-scatter-fpy', 'clickData')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date')])
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

        fig.update_layout(
            font=dict(
                family="Arial",
                size=20
            ),
            margin={'t': 50},
            hoverlabel=dict(
                bgcolor="white",
                font_size=20,
                font_family="Rockwell"
            )
        )

        return fig
    else: 
        return dash.no_update

@app.callback(
    Output('time-series-fpy', 'figure'),
    [Input('crossfilter-indicator-scatter-fpy', 'clickData')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('crossfilter-yaxis-type-fpy', 'value')])
def update_x_timeseries(clickData, start_date, end_date, Filter):

    if clickData is not None:
        PA_Selected = clickData['points'][0]['x']
    else:
        PA_Selected = "not selected"
    
    if PA_Selected != "not selected":

        df_timeseries= get_timeseries_by_PA(start_date, end_date, PA_Selected, Filter)

        title = '<b>{} - {}</b>'.format(PA_Selected, Filter)
        if Filter == 'Diario':

            # dt_all = pd.date_range(start=df_timeseries['DateTime'].iloc[0],end=df_timeseries['DateTime'].iloc[-1])
            # dt_obs = [d.strftime("%Y-%m-%d") for d in df_timeseries['DateTime']]
            # dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]

            # df_timeseries['Width'] = 0.1
            # print(df_timeseries['Width'].to_numpy())
            # print(df_timeseries)
            # print(dt_breaks)
            # print(df_timeseries['Width'].to_list())
            fig = px.bar(df_timeseries, x="DateTime", y="fpy", title=title, hover_name="fpy", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
            # fig.update_xaxes(
            #                 rangebreaks=[dict(values=dt_breaks)] # hide dates with no values
            #             )
            # fig.update_traces(width = df_timeseries['Width'].to_list())
        else:
            fig = px.bar(df_timeseries, x="DateTime", y="fpy", title=title, hover_name="fpy", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
            fig.update_layout(xaxis_type='category')

        fig.update_layout(
            font=dict(
                family="Arial",
                size=20
            ),
            margin={'t': 50},
            hoverlabel=dict(
                bgcolor="white",
                font_size=20,
                font_family="Rockwell"
            )
        )

        return fig
    
    else: 
        return dash.no_update

@app.callback(
    Output('output-fpy-button', 'children'),
    [Input('submit-button-state', 'n_clicks')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('PA-Selection', 'value'),
     State('fpy-filter-low', 'value'),
     State('fpy-filter-high', 'value')])
def update_total_fpy(n_clicks,start_date,end_date,PA_selection,limit_Low,limit_High):

    if float(limit_High)<float(limit_Low):
        limit_High = 100
        limit_Low = 0

    if limit_High==None or str(limit_High).isdigit()==False:
        limit_High = 100

    if limit_Low==None or str(limit_Low).isdigit()==False:
        limit_Low = 0

    if start_date!=None and end_date!=None:
        
        data = get_fpy_geral(start_date, end_date, PA_selection, limit_High, limit_Low)

        return '{}%'.format(data)
    else:
        return ''