import requests
from bs4 import BeautifulSoup

def search_debts(inn_search):
    params = {'inn':f'{inn_search}'}
    print('Идет поиск по rosdolgi.ru ...\n')
    query = requests.get('https://rosdolgi.ru/nalogi', params=params)
    if query.status_code == 200:
        try:
            bs = BeautifulSoup(query.text, 'lxml')
            result_search = bs.find(attrs={'data-amount': True})
            print(f'Задолженность {result_search["data-amount"]} | Источник: rosdolgi.ru')
        except:print(f'Налоговая задолженность по ИНН {inn_search} не найдена')
    else:print(f'Status Code: {query.status_code}\nПроверь правильность введенного ИНН')

