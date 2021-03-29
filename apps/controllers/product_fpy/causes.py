# pylint: disable=maybe-no-member
from datetime import datetime as dt
from pathlib import Path
#Bibliotecas para modelagem
import pandas as pd
import sqlite3
import pyodbc
import time
#from apps.models.product_fpy.connection import Database
from apps.models.product_fpy.FPYQueries import queriesFPY

def get_causes_by_PA(start_date, end_date, PA):

    fetch = queriesFPY()

    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')

    df_update_data = fetch.queryFailCauses(startDate=start_date, endDate=end_date, PASelected=PA)

    dfREP = df_update_data[df_update_data.STATUS != 'A']

    dfttREP = dfREP.drop_duplicates(subset=['NS'], keep='first')

    dftest = dfttREP.groupby(['STEP','STATUS']).size().reset_index(name='Reprovações')

    dfFinal = dftest.sort_values(by=['Reprovações'], ascending=False)

    return dfFinal