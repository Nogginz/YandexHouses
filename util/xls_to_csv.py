import pandas as pd

filename = 'testYandex'

data = pd.read_excel(filename + '.xls', encoding="utf-8")
data.index = data.pop("Unnamed: 0")
data.to_csv(filename + '.csv', delimiter=',')
