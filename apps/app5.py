import dash
import dash_table
from app import app

import pandas as pd

dfo = pd.read_csv('apps\dataset\data.csv')
dfo.columns =[column.replace(" ", "_") for column in dfo.columns]

#Retorna todos equipamentos Aprovados em alguma das etapas.
dfap = dfo.loc[(dfo['Status'] == "APROVADO")].drop_duplicates(subset = ["SERIAL_EQUIP"])

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


#Retorna todas as Etapas dos equipamentos reprovados, inclusive as aprovadas
dfReproved_AllSteps = dfo[dfo.SERIAL_EQUIP.isin(SNRep.SERIAL_EQUIP)]



#Tentativa: Pegar o número de OP's únicas, verificar quais nomes de produtos únicos existem. Este número será considerado a 
#quantidade de etapas de calibração existente. Então pegar o número de série e verificar se ele possui os "X" testes Aprovados

df = dfReproved_AllSteps

layout = dash_table.DataTable(
    data=df.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in df.columns],
    page_size=20
)