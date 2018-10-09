import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

c.execute("SELECT * FROM OUTCOME_PREDICTER")
tst = c.fetchall()

dataframe = pd.DataFrame(tst)

plt.matshow(dataframe.corr())

print(dataframe.corr())


# DF TO EXCEL
from pandas import ExcelWriter

writer = ExcelWriter('PythonExport.xlsx')
dataframe.corr().to_excel(writer,'Sheet5')
writer.save()
