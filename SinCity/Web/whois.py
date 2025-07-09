import requests, os
from bs4 import BeautifulSoup
from SinCity.Agent.header import header

def whois(domain:str):
    head = header()
    params = {'domain':{domain}}
    site = 'https://whois.ru/'
    response = requests.get(site, params=params, headers=head)
    if response.status_code == 200:
        bs = BeautifulSoup(response.text, 'lxml')
        try:
            for information in bs.find_all(class_='raw-domain-info-pre'):
                print(information.get_text())
        except Exception as ex:
            print(f'Error: {ex}')
    else:print(f'Response code: {response.status_code}')
