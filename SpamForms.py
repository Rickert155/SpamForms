from SinCity.colors import RED, RESET, GREEN
from modules.miniTools import (
        initSpammer,
        ListBase,
        selectColumn,
        RecordingDoneDomain,
        ReadDoneDomain
        )
from modules.forms import SubmitForms
import csv

def processingBase(base:str, column:str):
    counter_domain = 0
    complite_domains = ReadDoneDomain()
    with open(base, 'r') as file:
        for row in csv.DictReader(file):
            domain = row[column]
            company = row['Company']
            if '://' in domain:domain = domain.split('://')[1]
            if domain not in complite_domains:
                counter_domain+=1
                
                """Основной функционал инструмента"""
                SubmitForms(domain=domain, company=company)
                
                """Записываем домен в док""" 
                RecordingDoneDomain(domain=domain)

    if counter_domain == 0:
        print(f"{GREEN}База {base}: Обработаны все домены!{RESET}")


def spamForms():
    initSpammer()

    list_base = ListBase()
    number_base=0
    for base in list_base:
        number_base+=1
        print(f'[{number_base}] {base}')
        """Определяем колонку с доменами/сайтами"""
        column_domain = selectColumn(base=base)
        processingBase(base=base,column=column_domain)

spamForms()
