import dash
import dash_table
from app import app

import pandas as pd

dfo = pd.read_csv('apps\dataset\data.csv')
dfo.columns =[column.replace(" ", "_") for column in dfo.columns]

##dfoq = data.query('')

#Retorna todos equipamentos Aprovados em alguma das etapas.
dfap = dfo.loc[(dfo['Status'] == "APROVADO")].drop_duplicates(subset = ["SERIAL_EQUIP"])

#Retorna todas as reprovações únicas.
dfrep = dfo.loc[(dfo['Status'] == "REPROVADO")].drop_duplicates(subset = ["SERIAL_EQUIP"])
#Cria um novo dataframe com apenas a coluna SERIAL_EQUIP
SNRep = dfrep.filter(['SERIAL_EQUIP'], axis=1)
#Remove do dataframe de aprovados os produtos que aparecem na lista de reprovados, ficando apenas os que foram aprovados em todas as etapas
#na primeira tentativa
dfRlyApproved = dfap[~dfap.SERIAL_EQUIP.isin(SNRep.SERIAL_EQUIP)]

#Tentativa: Pegar o número de OP's únicas, verificar quais nomes de produtos únicos existem. Este número será considerado a 
#quantidade de etapas de calibração existente. Então pegar o número de série e verificar se ele possui os "X" testes Aprovados



df = dfRlyApproved

layout = dash_table.DataTable(
    data=df.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in df.columns],
    page_size=20
)