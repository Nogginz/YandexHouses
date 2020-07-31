import pandas as pd
import requests
from bs4 import BeautifulSoup

def parse_add_info(link):
    info = {}

    response = requests.get(link)
    s = response.status_code

    while s != 200:
        print('error:', s)
        response = requests.get(link)
        s = response.status_code

    html = response.text
    soup = BeautifulSoup(html, "lxml")

    base_anket = soup.find("dl", class_ ="dl-horizontal house")
    try:
        dts = base_anket.findAll("dt")
    except AttributeError:
        print("ERROR")
        print(base_anket)
        print(response.status_code)
        response = requests.get(link)
        html = response.text
        soup = BeautifulSoup(html, "lxml")
        base_anket = soup.find("dl", class_="dl-horizontal house")
        dts = base_anket.findAll("dt")

    dds = base_anket.findAll("dd")

    for row in range(len(dts)):
        if dts[row].text.replace('\n','') == "Год постройки":
            info["Год постройки"] = dds[row].text.replace('\n','')
        elif dts[row].text.replace('\n','') == "Количество этажей":
            info['Количество этажей'] = dds[row].text.replace('\n','')
        elif dts[row].text.replace('\n','') == "Жилых помещений":
            info['Количество жилых помещений'] = dds[row].text.replace('\n','')
        elif dts[row].text.replace('\n','') == "Материал несущих стен":
            info['Материал несущих стен'] = dds[row].text.replace('\n','')
        elif dts[row].text.replace('\n','') == "Тип мусоропровода":
            info['Тип мусоропровода'] = dds[row].text.replace('\n','')
        elif dts[row].text.replace('\n','') == "Спортивная площадка":
            info['Спортивная площадка'] = dds[row].text.replace('\n','')
        elif dts[row].text.replace('\n','') == "Адрес":
            info['Адрес'] = dds[row].text.replace('\n','').replace("   На карте", '')

        #print(info['Адрес'])

        if not ("Год постройки" in info):
            info["Год постройки"] = "не указано"
        elif not ("Количество этажей" in info):
            info["Количество этажей"] = "не указано"
        elif not ("Количество жилых помещений" in info):
            info["Количество жилых помещений"] = "не указано"
        elif not ("Материал несущих стен" in info):
            info["Материал несущих стен"] = "не указано"
        elif not ("Тип мусоропровода" in info):
            info["Тип мусоропровода"] = "не указано"
        elif not ("Спортивная площадка" in info):
            info["Спортивная площадка"] = "не указано"

    if ("Адрес" in info):
        city = info['Адрес'].split(", ")[-1]
        adds = info['Адрес'].split(", ")
        adds = ', '.join(adds[:len(adds)-2])
        info['Адрес'] = adds
        info['Город'] = city
    else:
        info['Адрес'] = "не указано"
        info['Город'] = "не указано"


    tables = soup.find("div", id="house-properties").findAll("div", class_="row")
    first_tables = tables[0].findAll("tr")

    for row in range(len(first_tables)):
        c1, c2 = first_tables[row].findAll("td")
        c1, c2 = c1.text, c2.text

        if c1 == 'Количество лифтов':
            info['Количество лифтов'] = c2
        elif c1 == 'Количество подъездов':
            info['Количество подъездов'] = c2
        elif c1 == 'Площадь зем. участка общего имущества м2':
            info['Площадь зем. участка общего имущества м2'] = c2
        elif c1 == 'Площадь нежилых помещений м2':
            info['Площадь нежилых помещений м2'] = c2
        elif c1 == 'Площадь парковки м2':
            info['Площадь парковки м2'] = c2

        if not ("Количество лифтов" in info):
            info["Количество лифтов"] = "не указано"
        elif not ("Количество подъездов" in info):
            info["Количество подъездов"] = "не указано"
        elif not ("Площадь зем. участка общего имущества м2" in info):
            info["Площадь зем. участка общего имущества м2"] = "не указано"
        elif not ("Площадь нежилых помещений м2" in info):
            info["Площадь нежилых помещений м2"] = "не указано"
        elif not ("Площадь парковки м2" in info):
            info["Площадь парковки м2"] = "не указано"

    third_table = tables[2].findAll("tr")
    for row in range(len(third_table)):
        c1, c, c2 = third_table[row].findAll("td")
        c1, c2 = c1.text, c2.text

        if c1 == "Количество мусоропроводов, ед.":
            info["Количество мусоропроводов, ед."] = c2

        if not ("Количество мусоропроводов, ед." in info):
            info["Количество мусоропроводов, ед."] = "не указано"

    return info

links = []
page = "http://dom.mingkh.ru/sankt-peterburg/sankt-peterburg/houses"
lines = []
N = 187 #/187
for number_page in range(1, N+1):
    print(number_page,'/',N)

    r = requests.get(page + "?page=" + str(number_page))
    s = r.status_code

    while s != 200:
        print('error:', s)
        r = requests.get(page + "?page=" + str(number_page))
        s = r.status_code

    html = r.text
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("tbody").findAll('tr')
    for tr in table:
        tds = tr.find_all("td")
        links.append("http://dom.mingkh.ru" + tds[2].find("a").get("href"))

houses = len(links)
print("Ссылки собраны! Ссылок:", houses)

i = 0
infs = []
for link in links:
    i+=1
    print(i,'/',houses)
    inf = parse_add_info(link)
    if len(inf) == 14:
        infs.append(inf)

data = pd.DataFrame(infs)
data.to_csv("database_SPB.csv")
data.to_excel("database_SPB.xls")

