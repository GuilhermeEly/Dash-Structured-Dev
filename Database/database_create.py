import pandas as pd
import sqlite3

PATH1 = "C:\\Users\\gely\\dash_plotly\\test\\StructuredProject\\Database\\Excel\\ZZ8u.csv"
ZZ8 = pd.read_csv(PATH1, delimiter=";", encoding = "ISO-8859-1")

PATH2 = "C:\\Users\\gely\\dash_plotly\\test\\StructuredProject\\Database\\Excel\\ZZ9u.csv"
ZZ9 = pd.read_csv(PATH2, delimiter=";", encoding = "ISO-8859-1")

PATH3 = "C:\\Users\\gely\\dash_plotly\\test\\StructuredProject\\Database\\Excel\\SZ2u.csv"
SZ2 = pd.read_csv(PATH3, delimiter=";", encoding = "ISO-8859-1")

PATH4 = "C:\\Users\\gely\\dash_plotly\\test\\StructuredProject\\Database\\data\\fpy_mockup.db"
db_conn = sqlite3.connect(PATH4)

c = db_conn.cursor()

c.execute(
    """
    CREATE TABLE SZ2 (
        Z2_FILIAL INTEGER,
        Z2_SERIE INTEGER,
        Z2_PRODUTO INTEGER,
        Z2_OP INTEGER,
        Z2_PEDIDO TEXT,
        Z2_NF INTEGER,
        Z2_VOLUME INTEGER,
        Z2_DTGERAD INTEGER,
        Z2_GERADOR TEXT,
        Z2_DTINTEG TEXT,
        Z2_HORAINT TEXT,
        Z2_OPERINT TEXT,
        Z2_DTCALIB TEXT,
        Z2_HORACAL TEXT,
        Z2_OPERCAL TEXT,
        Z2_DTEXPED INTEGER,
        Z2_HORAEXP TIME,
        Z2_PEDIDOP TEXT,
        Z2_PRODT TEXT,
        Z2_ITEMP INTEGER,
        Z2_LOCPROD TEXT,
        Z2_OBS TEXT,
        Z2_RELCALI TEXT,
        Z2_STATUS TEXT,
        Z2_HISTOR TEXT,
        Z2_SERNF INTEGER,
        Z2_ITEMNF INTEGER,
        D_E_L_E_T_ TEXT,
        R_E_C_N_O_ INTEGER,
        Z2_IMP INTEGER,
        Z2_CXM INTEGER,
        Z2_NFDEV TEXT,
        Z2_FILPED INTEGER,
        Z2_FILNF INTEGER,
        Z2_FILEST INTEGER,
        Z2_USREXP TEXT,
        Z2_PLATAFO TEXT,
        R_E_C_D_E_L_ INTEGER,
        PRIMARY KEY(R_E_C_N_O_)
        );
    """)

c.execute(
    """
    CREATE TABLE ZZ8 (
        ZZ8_FILIAL INTEGER ,
        ZZ8_SOFT TEXT,
        ZZ8_FIRM INTEGER,
        ZZ8_NUMBER INTEGER,
        ZZ8_PNAME TEXT,
        ZZ8_FIRMPR INTEGER,
        ZZ8_NUMEQ INTEGER,
        ZZ8_MAC INTEGER,
        ZZ8_NAMEOP TEXT,
        ZZ8_ORDNUM INTEGER,
        ZZ8_OPNUM INTEGER,
        ZZ8_DATE INTEGER,
        ZZ8_HOUR TIME,
        ZZ8_STATUS TEXT,
        ZZ8_TIPO INTEGER,
        D_E_L_E_T_ TEXT,
        R_E_C_N_O_ INTEGER,
        ZZ8_REVISA TEXT,
        ZZ8_DURATI TEXT,
        ZZ8_MAC1 INTEGER,
        ZZ8_MAC2 INTEGER,
        ZZ8_MAC3 INTEGER,
        ZZ8_MAC4 INTEGER,
        ZZ8_MAC5 INTEGER,
        ZZ8_MEI INTEGER,
        PRIMARY KEY(R_E_C_N_O_),
        FOREIGN KEY(ZZ8_NUMEQ) REFERENCES SZ2(Z2_SERIE)
        );
    """)

c.execute(
    """
    CREATE TABLE ZZ9 (
        ZZ9_FILIAL INTEGER ,
        ZZ9_STEP TEXT,
        ZZ9_OFFSET FLOAT,
        ZZ9_GAIN FLOAT,
        ZZ9_CONTB INTEGER,
        ZZ9_CONTA INTEGER,
        ZZ9_VALR FLOAT,
        ZZ9_ERRO FLOAT,
        ZZ9_STATUS TEXT,
        ZZ9_SERIAL INTEGER,
        ZZ9_DATE INTEGER,
        ZZ9_HOUR TIME,
        ZZ9_TIPO INTEGER,
        ZZ9_GAIN2 FLOAT,
        R_E_C_N_O_ INTEGER,
        D_E_L_E_T_ TEXT,
        PRIMARY KEY(R_E_C_N_O_),
        FOREIGN KEY(ZZ9_SERIAL) REFERENCES SZ2(Z2_SERIE)
        );
    """)

SZ2.to_sql('SZ2', db_conn, if_exists='append', index=False)
ZZ9.to_sql('ZZ9', db_conn, if_exists='append', index=False)
ZZ8.to_sql('ZZ8', db_conn, if_exists='append', index=False)
