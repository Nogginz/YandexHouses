import pandas as pd

filename = 'yandexSBPsaleSelenium'

data = pd.read_csv(filename + '.csv', delimiter=',')
data.index = data.pop("Unnamed: 0")
data.to_excel(filename + '.xls')
