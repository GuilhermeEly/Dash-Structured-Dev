import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output
from app import app

import pandas as pd

dfo = pd.read_csv(r'apps\dataset\data.csv')
dfo.columns =[column.replace(" ", "_") for column in dfo.columns]

#Transforma a coluna Data_Calibra em datetime
dfo['Data_Calibra'] = pd.to_datetime(dfo['Data_Calibra'],format=r'%d/%m/%Y')

#Retorna todas as reprovações únicas.
dfrep = dfo.loc[(dfo['Status'] == "REPROVADO")].drop_duplicates(subset = ["SERIAL_EQUIP"])

#Cria um novo dataframe com apenas a coluna SERIAL_EQUIP
SNRep = dfrep.filter(['SERIAL_EQUIP'], axis=1)

#Remove do dataframe original os produtos que aparecem na lista de reprovados, ficando apenas os que foram aprovados em todas as etapas
#na primeira tentativa
dfRlyApproved = dfo[~dfo.SERIAL_EQUIP.isin(SNRep.SERIAL_EQUIP)]

#Retorna todas as Etapas dos equipamentos aprovados
SNRlyApproved = dfRlyApproved.filter(['SERIAL_EQUIP'], axis=1)
dfRlyApproved_AllSteps = dfRlyApproved[dfRlyApproved.SERIAL_EQUIP.isin(SNRlyApproved.SERIAL_EQUIP)]

#Retorna todos equipamentos Aprovados, apenas uma etapa por linha.
dfap = dfRlyApproved_AllSteps.loc[(dfRlyApproved_AllSteps['Status'] == "APROVADO")].drop_duplicates(subset = ["SERIAL_EQUIP"])

#Retorna todas as Etapas dos equipamentos reprovados, inclusive as aprovadas
dfReproved_AllSteps = dfo[dfo.SERIAL_EQUIP.isin(SNRep.SERIAL_EQUIP)]

##SEPARA OS DADOS POR DATA
print(len(SNRep.index))
print(dfrep.groupby('Data_Calibra')['Data_Calibra'].value_counts())

#Tentativa: Pegar o número de OP's únicas, verificar quais nomes de produtos únicos existem. Este número será considerado a 
#quantidade de etapas de calibração existente. Então pegar o número de série e verificar se ele possui os "X" testes Aprovados

df = dfReproved_AllSteps

#Transforma e formata a coluna Data_Calibra para uma STRING com o formato BR de data
df['Data_Calibra'] = df['Data_Calibra'].dt.strftime(r'%d/%m/%Y')

layout = html.Div([
    html.Div([
        html.Div([
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date_placeholder_text='Data início',
                end_date_placeholder_text='Data fim'
            ),
        ]),

        dcc.Graph(id='indicator-graphic'),

        html.Div([
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in df.columns],
                page_size=20
            )
        ]),
    ])
])




# @app.callback(
#     Output('indicator-graphic', 'figure'),
#     [Input('date-picker-range', 'start_date'),
#     Input('date-picker-range', 'end_date')])

# def update_graph(start_date,end_date ):

#     #Entre datas Filtro
#     start_date = pd.to_datetime(start_date)
#     end_date = pd.to_datetime(end_date)

#     dfDate_Filter = dfo.loc[(dfo['Data_Calibra'] > start_date) & (dfo['Data_Calibra'] < end_date)]

# #     fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
# #                      y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
# #                      hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])