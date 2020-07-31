import pandas as pd
import os
from selenium import webdriver
from bs4 import BeautifulSoup
import time

def save_data(items, filename = "example", type = 0, datas = 0):
    data = pd.DataFrame(items)
    data["Адрес"] = data.pop("дом")
    data["Количество комнат"] = data.pop("комнат")#.astype(str).astype("int64")
    data["Площадь"] = data.pop("площадь")
    data["Этаж"] = data.pop("этаж")#.astype(str).astype("int64")
    data["Срок экспозиции"] = data.pop("экспозиция")#.astype(str).astype("int64")
    data["Начальная цена"] = data.pop("стартцена")#.astype(str).astype("int64")
    data["Начальная цена за 1 метр"] = data.pop("стартм")#.astype(str).astype("int64")
    data["Цена при снятии"] = data.pop("концена").astype(str)#.astype("int64")
    data["Цена при снятии за 1 метр"] = data.pop("конм")#.astype(str).astype("int64")
    data["Опубликовано"] = data.pop("датап")
    data["Дата снятия"] = data.pop("датас")
    #data.index = data.pop("Unnamed: 0")

    files = os.listdir()
    if filename + '.csv' in files:
        last_data_csv = pd.read_csv(filename+".csv")
        last_data_csv.index = last_data_csv.pop("Unnamed: 0")
        data = last_data_csv.merge(data, how='outer')
    else:
        last_data_csv = pd.read_csv("test.csv")
        last_data_csv.index = last_data_csv.pop("Unnamed: 0")
        data = last_data_csv.merge(data, how='outer')
    data.to_csv(filename + ".csv")

    with open(filename.replace("@","") + "log.txt", 'w') as f:
        f.write(str(datas))

    print("СОХРАНЕНО")

def parse_pagination(soup):
    try:
        pag_group = soup.find("div", class_="Pager Pager_theme_islands").span
    except AttributeError:
        return 1
    last_page = pag_group.findAll("label")[-1]
    last_page_number = last_page.find("a").text.replace(" ",'').replace("\"", '')
    if "Следующая" in last_page_number:
        last_page = pag_group.findAll("label")[-2]
    last_page_number = last_page.find("a").text.replace(" ", '').replace("\"", '')
    return last_page_number

def get_log(filename):
    with open(filename.replace("@", "") + "log.txt", "r") as f:
        return int(f.read())

def parse_item_list(soup, add):
    item_list = []
    table = soup.find("div", class_="OffersArchiveSearchOffers__body")
    rows = table.findAll("div", class_="OffersArchiveSearchOffers__row")
    for row in rows:
        cells = row.findAll("div" ,class_="OffersArchiveSearchOffers__cell")
        area_rooms = cells[1].find("div", class_="OffersArchiveSearchOffers__title")
        if area_rooms is None:
            area_rooms = cells[1].a
        area_rooms = area_rooms.find("span").text.split(", ")
        area = area_rooms[0].replace(" ",'').replace("&nbsp;", '')
        rooms = area_rooms[1].replace(" ",'').replace("-комнатная", '')
        floor = cells[1].find('div', class_="OffersArchiveSearchOffers__extra-info").text.replace(" ",'').replace('этаж', "")
        price_start = cells[2].find("div", class_='OffersArchiveSearchOffers__price').span.text.replace(' ','').replace(",",'.').replace("млн₽","")

        if "." in price_start:
            price_start = price_start.split('.')
            price_start = price_start[0] + price_start[1] + "000000"[len(price_start[1]):]
        else:
            price_start = price_start + "000000"

        m_price_start = cells[2].find("div", class_='OffersArchiveSearchOffers__extra-info').span.text.replace(" ", '').replace(' ','').replace("₽",'').replace(",",'.')

        price_end = cells[3].find("div", class_='OffersArchiveSearchOffers__price').span.text.replace(' ','').replace(",",'.').replace("млн₽","")

        if "." in price_end:
            price_end = price_end.split('.')
            price_end = price_end[0] + price_end[1] + "000000"[len(price_end[1]):]
        else:
            price_end = price_end + "000000"

        m_price_end = cells[3].find("div", class_='OffersArchiveSearchOffers__extra-info').span.text.replace(" ",'').replace(' ','').replace("₽",'').replace(",",'.')

        date_publication = cells[4].text.replace("\n",'').replace("\"", '')[0:10]
        exposition = cells[4].div.text.replace('&nbsp;', " ").replace("В экспозиции",'').replace("дня",'').replace("дней",'').replace("день",'')

        date_final = cells[5].text


        item_list.append({"площадь": area.replace(" м²", ''),
         "комнат": rooms.replace("свободнаяпланировка", "свободная планировка"),
         "этаж": floor,
         "стартцена": price_start,
         "стартм": m_price_start,
         "концена": price_end,
         "конм": m_price_end.replace(" ",''),
         "датап": date_publication,
         "датас": date_final,
         "экспозиция": exposition,
         "дом": add})

        # print("| Площадь:",area)
        # print("| Комнаты:", rooms)
        # print("| Этаж:", floor)
        # print("| Стартовая цена:", price_start)
        # print("| Стартовая цена 1м:", m_price_start)
        # print("| Конечная цена:", price_end)
        # print("| Конечная цена 1м:", m_price_end)
        # print("| Дата публикации:", date_publication)
        # print("| Дата снятия:", date_final)
        # print("| Экспозиция:", exposition)
        # print()
    return item_list

def get_links(file = "databaseSpb.csv", type = 0):
    addresses = list(pd.read_csv(file, delimiter=',')["Адрес"])
    urls = []
    for address in addresses:
        #print(address)

        try:
            link = address.replace(",", "%2C").replace(" ", "%20").replace("/", "%2F")
        except AttributeError:
            continue

        if type == 0:
            url = 'https://realty.yandex.ru/otsenka-kvartiry-po-adresu-onlayn/' + link + '/kupit/kvartira/'
        elif type == 1:
            url = 'https://realty.yandex.ru/otsenka-kvartiry-po-adresu-onlayn/' + link + '/snyat/kvartira/'
        else:
            return
        urls.append(url)
    return urls, addresses

def get_soup(browser, url):
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    while "ошибка" in soup.title.text:
        browser.get(url)
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
    return soup

def main():

    browser = webdriver.Chrome()
    browser.get('https://realty.yandex.ru/')
    time.sleep(15)
    type = 0
    file = "database_SPB.csv"
    urls, addresses = get_links(file, type)
    items = []
    gets = 0

    filename = "yandexSPBsaleSelenium"

    try:
        start = get_log(filename)
    except FileNotFoundError:
        start = 0

    nums = start-1
    name_address = ''
    old_name_address = ''

    for url in urls[start:]:

        nums+=1
        gets+=1
        soup =  get_soup(browser, url)#получить суп страницы
        print(gets," : ", nums)

        if nums % 1000 == 0:
            print("СОХРАНЕНИЕ")
            filename += "@"
            try:
                save_data(items, filename=filename, datas=nums)
            except KeyError:
                print("Данные не сохранены")
            print("items отчищен")
            items = []

        old_name_address = name_address
        name_address = soup.find('input', attrs = {"name":"address"})["value"]

        print(name_address)

        if old_name_address == name_address:
            print('адрес пропущен')
            continue

        if (not (soup.find('div', class_="OffersArchiveSearchOffers__not-found") is None)) or (not (soup.find('div', class_='OffersArchiveNotFound__text') is None)):
            #print("ничего не найдено")
            continue

        items.extend(parse_item_list(soup, addresses[nums])) #получить итемы страницы и добавить их к остальным итемам
        pages_num = int(parse_pagination(soup)) #получить количество страниц по url
        for page in range(1, pages_num+1): #пройтись по всем страницам
            #time.sleep(1)
            if page == 1: #если страница первая
                continue  #то пропустить
            urlp = url + str(page) + "/" #добавить к ЮРЛ номер страницы
            gets += 1
            print(gets, " : ", nums)
            soup = get_soup(browser, urlp) #получить суп страницы

            items.extend(parse_item_list(soup, addresses[nums])) #получить итемы страницы и добавить их к остальным итемам

        if gets % 100 == 0:
            print("СОХРАНЕНИЕ")
            save_data(items, filename = filename, datas = nums)


    save_data(items, filename=filename, datas=nums)

if __name__ == "__main__":
    main()