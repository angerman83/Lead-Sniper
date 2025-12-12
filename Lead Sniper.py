import pandas as pd
import time
import re
from selenium import webdriver

# загрузка списка агентств
df = pd.read_excel('ppap.xlsx')

# запускаем браузер
driver = webdriver.Chrome() 

# счетчик обработки
ok = -1

# цикл по списку
for x in df.index:
    if x <= ok:
        continue # пропускаем успешные (если ранее был стоп по капче)
    driver.get(df.loc[x,'url']) # загружаем страницу
    time.sleep(10) # ждем паузу
    try: # проверка на наличие капчи
        if (driver.find_element('css selector','span.h1').text == 'Проверка, что Вы не робот'):
            print ('capcha ',x)
            break # если есть, останавлиаем цикл
    except:
        pass  # если нет, продолжаем
    try: # поиск нужных элементов и запись данных
        df.loc[x,'inn'] = driver.find_element('css selector','span.clipboard').text
        df.loc[x,'name'] = driver.find_element('css selector','a.upper').text
        for z in driver.find_elements('css selector','td.tth'): # проверка на наличие данных по выручке
            if (z.text == 'Доходы'): # если есть, то записываем
                df.loc[x,'revenue'] = re.sub(r'\D', '', driver.find_element('css selector','td.nwra').text) # оставляем только числа
                df.loc[x,'revenue_year'] = '2024'
                df.loc[x,'source'] = 'list_org'
    except:
        print('error ',x)
    print(x, ' ok') # отмечаем успех по этой записи
    ok = x # фиксируем успешное количество

comp = df.dropna() # убераем пропуски

for x in comp.index:
    try:
        pd.to_numeric(comp.loc[x,'revenue']) # проверка выручки на число
    except:
        comp.loc[x,'revenue'] = 0 # если не число, поставим ноль

comp['revenue'] = pd.to_numeric(comp['revenue']) # преобразуем выручку в число
comp.query('revenue > 200000000').drop('url',axis=1).to_csv('companies.csv') # сохраняем в файл