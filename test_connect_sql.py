import pyodbc
import pandas as pd
server = 'nobrpoaerp01' 
database = 'FPY' 
username = 'FPY' 
password = 'FPY@2020!' 
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

df_update_data = pd.read_sql_query(
            """
                SELECT * FROM FPY.information_schema.tables
            """, cnxn)

#cursor.execute("SELECT TRY_CONVERT(date,MIN(ZZ9_DATE)) from ZZ9990") 
#row = cursor.fetchone() 
#while row: 
#    print(row[0])
#    row = cursor.fetchone()

print(df_update_data)