import dash
import dash_table
from app import app

import pandas as pd

dfo = pd.read_csv('apps\dataset\data.csv')
dfo.columns =[column.replace(" ", "_") for column in dfo.columns]

#dfoq = data.query('')

#Retorna todos equipamentos Aprovados em alguma das etapas.
dfap = dfo.loc[(dfo['Status'] == "APROVADO")].drop_duplicates(subset = ["SERIAL_EQUIP"])

#Retorna todas as reprovações únicas.
dfrep = dfo.loc[(dfo['Status'] == "REPROVADO")].drop_duplicates(subset = ["SERIAL_EQUIP"])


dfmerge = pd.merge(dfap, dfrep, how='outer', indicator=True)
print(dfmerge)
print (dfmerge.loc[dfmerge._merge == 'left_only', ['SERIAL_EQUIP']])
#Tentativa: Pegar o número de OP's únicos, verificar quais nomes de produtos únicos existem. Este número será considerado a 
#quantidade de etapas de calibração existente. Então pegar o número de série e verificar se ele possui os "X" testes Aprovados

dfremove = dfrep[['SERIAL_EQUIP']]
print(dfremove)

print(dfap.loc[~dfap.index.isin(dfap.merge(dfremove.assign(a='key'),how='left').dropna().index)])
#Retorna um Numpy com a quantidade de equipamentos únicos reprovados por OP
#print(df.drop_duplicates().ORDEM_PROD.value_counts())

df = dfap

layout = dash_table.DataTable(
    data=df.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in df.columns],
    page_size=20
)