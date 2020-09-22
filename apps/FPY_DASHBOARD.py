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
import pandas as pd
import sqlite3
#Caminho da aplicação
from app import app

def get_timeseries_by_PA(start_date, end_date, PA):
    start_date = dt.strptime(start_date, "%Y-%m-%d")
    end_date = dt.strptime(end_date, "%Y-%m-%d")

    base_path = Path(__file__).parent
    database = (base_path / r"..\Database\data\fpy_mockup2.db").resolve()
    conn = sqlite3.connect(database)

    df_update_data = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                (date(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA
                FROM SZ2 AS z2 
                INNER JOIN ZZ8 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z2.Z2_PRODUTO=(?) AND z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY NS, DATA, HORA
            """, conn, params=(str(PA),start_date, end_date))

    #Pega todos os produtos reprovados pelo menos em uma etapa, removendo os duplicados
    dfrep = df_update_data.loc[(df_update_data['STATUS'] == "R")].drop_duplicates(subset = ["NS"])

    #Retorna apenas o número de série dos produtos reprovados
    SNRep = dfrep.filter(['NS'], axis=1)
    
    #Remove todos os registros de produtos reprovados, inclusive posterior aprovação
    dfRlyApproved = df_update_data[~df_update_data.NS.isin(SNRep.NS)].drop_duplicates(subset = ["NS"])

    #Agrupa REPROVADOS por DATA e faz a contagem das REPROVAÇÕES
    dftest = dfrep.groupby(['DATA']).size().reset_index(name='counts')

    #Agrupa APROVADOS por DATA e faz a contagem das APROVAÇÕES
    dfApprTest = dfRlyApproved.groupby(['DATA']).size().reset_index(name='counts')

    #Junta a tabela de reprovados com aprovados, usando como referência a data. Retorna 0 para valores NaN.
    dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='DATA').fillna(0)

    #Calcula o indicador First Pass Yield
    dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

    #Calcula total produzido
    dfFinal['Produzido'] = dfFinal['counts_y'] + dfFinal['counts_x']

    #Renomeia as colunas da tabela
    dfFinal.rename(columns={"counts_y": "Aprovadas", "counts_x": "Reprovadas"}, inplace=True)

    #Retorna 0 para valores NaN de First Pass Yield
    dfFinal[['DATA', 'fpy']].fillna(0)

    #Ordena a tabela conforme a DATA
    dfFinal = dfFinal.sort_values(by=['DATA'])

    #Para melhor visualizar os dias com FPY de 0% foi determinado o valor abaixo para ser plotado
    dfFinal.fpy[dfFinal.fpy == 0] = 0.005

    #Converte a coluna para o formato YYYY-MM-DD para realizar o plot
    dfFinal['DateTime'] = pd.to_datetime(dfFinal['DATA'].astype(str), format='%Y-%m-%d')

    #Formata o indicador First Pass Yield como porcentagem
    dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

    return dfFinal

def get_causes_by_PA(start_date, end_date, PA):
    start_date = dt.strptime(start_date, "%Y-%m-%d")
    end_date = dt.strptime(end_date, "%Y-%m-%d")

    base_path = Path(__file__).parent
    database = (base_path / r"..\Database\data\fpy_mockup2.db").resolve()
    conn = sqlite3.connect(database)
        
    df_update_data = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z9.ZZ9_SERIAL as NS, z9.ZZ9_STEP as STEP,
                z9.ZZ9_TIPO as TIPO, z9.ZZ9_STATUS as STATUS,
                (date(z9.ZZ9_DATE)) as DATA
                FROM SZ2 AS z2 
                INNER JOIN ZZ9 AS z9 ON z2.Z2_SERIE=z9.ZZ9_SERIAL
                WHERE PA = (?) AND z9.ZZ9_DATE BETWEEN (?) AND (?) ORDER BY DATA
            """, conn, params=(PA, start_date, end_date))

    dfREP = df_update_data[df_update_data.STATUS != 'A']

    dftest = dfREP.groupby(['STEP','STATUS']).size().reset_index(name='Reprovações')

    dfFinal = dftest.sort_values(by=['Reprovações'], ascending=False)

    return dfFinal

def get_fpy_by_Date(start_date, end_date, Filter, PA_selection):

    start_date = dt.strptime(start_date, "%Y-%m-%d")
    end_date = dt.strptime(end_date, "%Y-%m-%d")

    base_path = Path(__file__).parent
    database = (base_path / r"..\Database\data\fpy_mockup2.db").resolve()
    conn = sqlite3.connect(database)
    
    if PA_selection == None or PA_selection == '':
        df_update_data = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                (date(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA, (strftime("%Y", z8.ZZ8_DATE) || strftime("%W", z8.ZZ8_DATE)) as SEMANA
                FROM SZ2 AS z2 
                INNER JOIN ZZ8 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY DATA
            """, conn, params=(start_date, end_date))
    else:
        ###############################################################################################
        #################Possível Bug entre a conversão do Excel para o banco de dados#################
        ###############################################################################################
        PA_selection = PA_selection.replace(' ', '')
        while len(PA_selection) < 15:
            PA_selection += ' '
        ###############################################################################################
        #################Possível Bug entre a conversão do Excel para o banco de dados#################
        ###############################################################################################

        df_update_data = pd.read_sql_query(
            """
                SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
                z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
                (date(z8.ZZ8_DATE)) as DATA, z8.ZZ8_HOUR as HORA, (strftime("%Y", z8.ZZ8_DATE) || strftime("%W", z8.ZZ8_DATE)) as SEMANA
                FROM SZ2 AS z2 
                INNER JOIN ZZ8 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
                WHERE z2.Z2_PRODUTO = (?) AND z8.ZZ8_DATE BETWEEN (?) AND (?) ORDER BY DATA
            """, conn, params=(PA_selection, start_date, end_date))

    df_products = df_update_data.drop_duplicates(subset = ["PA"])
    df_products['PA'] = df_products['PA'].map(str)
    df_products = df_products.set_index('PA')

    dfrep = df_update_data.loc[(df_update_data['STATUS'] == "R")].drop_duplicates(subset = ["NS"])

    SNRep = dfrep.filter(['NS'], axis=1)

    dfRlyApproved = df_update_data[~df_update_data.NS.isin(SNRep.NS)].drop_duplicates(subset = ["NS"])

    dftest = dfrep.groupby(['PA']).size().reset_index(name='counts')

    dfApprTest = dfRlyApproved.groupby(['PA']).size().reset_index(name='counts')

    dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='PA').fillna(0)

    dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

    dfFinal['Produzido'] = dfFinal['counts_y'] + dfFinal['counts_x']

    dfFinal.rename(columns={"counts_y": "Aprovadas", "counts_x": "Reprovadas"}, inplace=True)

    dfFinal[['PA', 'fpy']].fillna(0)

    dfFinal = dfFinal.sort_values(by=['fpy'])

    dfFinal.fpy[dfFinal.fpy == 0] = 0.005

    dfFinal['PA'] = dfFinal['PA'].map(str)

    dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

    dfFinal = dfFinal.join(df_products, on='PA')

    return dfFinal

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
            )
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
    dash.dependencies.Output('fpy-causes', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter-fpy', 'clickData'),
     dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date')])
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
    dash.dependencies.Output('time-series-fpy', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter-fpy', 'clickData'),
     dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date')])
def update_x_timeseries(clickData, start_date, end_date):

    if clickData is not None:
        PA_Selected = clickData['points'][0]['x']
    else:
        PA_Selected = "not selected"
    
    

    if PA_Selected != "not selected":

        df_timeseries= get_timeseries_by_PA(start_date, end_date, PA_Selected)

        title = '<b>{} - Tempo</b>'.format(PA_Selected)

        fig = px.bar(df_timeseries, x="DateTime", y="fpy", title=title, hover_name="fpy", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
        #fig.update_xaxes(type='category')

        return fig
    
    else: 
        return dash.no_update