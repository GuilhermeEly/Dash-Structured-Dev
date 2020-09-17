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

def get_fpy_by_PA(start_date, end_date, Filter):

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

    dfrep = df_update_data.loc[(df_update_data['STATUS'] == "R")].drop_duplicates(subset = ["NS"])

    SNRep = dfrep.filter(['NS'], axis=1)

    dfRlyApproved = df_update_data[~df_update_data.NS.isin(SNRep.NS)].drop_duplicates(subset = ["NS"])

    dftest = dfrep.groupby(['PA']).size().reset_index(name='counts')

    dfApprTest = dfRlyApproved.groupby(['PA']).size().reset_index(name='counts')

    dfFinal = pd.merge(dftest, dfApprTest, how='outer', on='PA').fillna(0)

    dfFinal['fpy'] = dfFinal['counts_y'] /( dfFinal['counts_y'] + dfFinal['counts_x'])

    dfFinal['Produzido'] = dfFinal['counts_y'] + dfFinal['counts_x']

    print(dfFinal)

    dfFinal.rename(columns={"counts_y": "Aprovadas", "counts_x": "Reprovadas"}, inplace=True)

    print(dfFinal)

    dfFinal[['PA', 'fpy']].fillna(0)

    dfFinal = dfFinal.sort_values(by=['fpy'])

    dfFinal.fpy[dfFinal.fpy == 0] = 0.005

    dfFinal['PA'] = dfFinal['PA'].map(str)

    dfFinal['fpy'] = dfFinal['fpy'].astype(float).map("{:.2%}".format)

    return dfFinal

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
        dcc.Graph(id='crossfilter-indicator-scatter-fpy')
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series-fpy'),
        dcc.Graph(id='y-time-series-fpy'),
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
        
        data = get_fpy_by_PA(start_date, end_date, Filter)

        fig = px.bar(data, x="PA", y="fpy", title='First Pass Yield',hover_name="PA", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
        fig.update_xaxes(type='category')
        fig.update_layout(hovermode="x")

        fig.update_layout(margin={'l': 0, 'b': 0, 't': 50, 'r': 0}, hovermode='closest')
        return fig
    
    else:
        return dash.no_update

@app.callback(
    dash.dependencies.Output('x-time-series-fpy', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata']
    dff = df[df['Country Name'] == country_name]
    dff = dff[dff['Indicator Name'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)