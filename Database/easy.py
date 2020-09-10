import pandas as pd
import sqlite3

PATH4 = "C:\\Users\\gely\\dash_plotly\\test\\StructuredProject\\Database\\data\\fpy_mockup2.db"
db_conn = sqlite3.connect(PATH4)

c = db_conn.cursor()

c.execute(
    """
    CREATE TABLE SZ2 (
        Z2_FILIAL INTEGER,
        Z2_SERIE INTEGER
    );
    """
    )