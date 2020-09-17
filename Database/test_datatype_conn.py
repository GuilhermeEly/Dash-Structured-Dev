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

base_path = Path(__file__).parent
database = (base_path / r"..\Database\data\fpy_mockup2.db").resolve()

conn = sqlite3.connect(database)
    
start_time = time.time()
df_update_data = pd.read_sql_query(
    """
        SELECT z2.Z2_PRODUTO as PA, z8.ZZ8_NUMEQ as NS, z8.ZZ8_PNAME as NOME,
        z8.ZZ8_TIPO as TIPO, z8.ZZ8_NUMBER as NS_JIGA, z8.ZZ8_STATUS as STATUS,
        z8.ZZ8_DATE as DATA, z8.ZZ8_HOUR as HORA
        FROM SZ2 AS z2 
        INNER JOIN ZZ8 AS z8 ON z2.Z2_SERIE=z8.ZZ8_NUMEQ
        ORDER BY DATA
    """, conn)

print(df_update_data)