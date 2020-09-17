import pandas as pd
import sqlite3

PATH1 = "C:\\Users\\gely\\dash_plotly\\test\\StructuredProject\\Database\\Excel\\ZZ8u.csv"
ZZ8 = pd.read_csv(PATH1, delimiter=";", encoding = "ISO-8859-1")

PATH2 = "C:\\Users\\gely\\dash_plotly\\test\\StructuredProject\\Database\\Excel\\ZZ9u.csv"
ZZ9 = pd.read_csv(PATH2, delimiter=";", encoding = "ISO-8859-1")

PATH3 = "C:\\Users\\gely\\dash_plotly\\test\\StructuredProject\\Database\\Excel\\SZ2u.csv"
SZ2 = pd.read_csv(PATH3, delimiter=";", encoding = "ISO-8859-1")

ZZ9['ZZ9_DATE'] = pd.to_datetime(ZZ9['ZZ9_DATE'], format='%Y%m%d')
ZZ8['ZZ8_DATE'] = pd.to_datetime(ZZ8['ZZ8_DATE'], format='%Y%m%d')

ZZ8 = ZZ8.sort_values(by=['ZZ8_DATE'])
print(ZZ8['ZZ8_DATE'])
