from modules.config import (
        done_dir, 
        done_file_path,
        base_dir,
        result_dir,
        base_name
        )
from SinCity.colors import RED, RESET, GREEN
import os, csv, sys, time

def CurrentTime():
    current_time = time.strftime("%d/%m/%Y %H:%M:%S")
    return current_time

"""Определяем колонку доменами/сайтами"""
def selectColumn(base:str):
    column = None
    domain_column = 'Domain'
    site_column = 'Site'

    with open(base, 'r') as file:
        headers = next(csv.reader(file))

    if domain_column in headers:
        column = domain_column
        return column
    if domain_column not in headers and site_column in headers:
        column = site_column
        return column

    if column == None:
        print(
                f'Не обнаружены колонки с доменами или сайтами!\n'
                f'Проверьте наличие колонки {domain_column} и/или {site_column}'
                )
        sys.exit()


"""Собираем список баз"""
def ListBase():
    list_base = []
    for base in os.listdir(base_dir):
        if '.csv' in base:list_base.append(f"{base_dir}/{base}")
    return list_base

"""Проверка необходимых директорий/файлов"""
def initSpammer():
    if not os.path.exists(done_dir):os.makedirs(done_dir)
    if not os.path.exists(done_file_path):
        with open(done_file_path, 'a') as file:
            file.close()

def ReadDoneDomain():
    list_domain = set()
    with open(done_file_path, 'r') as file:
        for domain in file.readlines():
            list_domain.add(domain.strip())
    return list_domain

def RecordingDoneDomain(domain:str):
    domain_list = []
    if os.path.exists(done_file_path):
        with open(done_file_path, 'r') as file:
            for line in file.readlines():
                domain_done = line.strip()
                if domain_done not in domain_list:domain_list.append(domain_done)
    
    if domain not in domain_list: 
        with open(done_file_path, 'a+') as file:
            file.write(f'{domain}\n')


def RecordingNotSendedCompany(domain:str, company:str, reason:str):
    if not os.path.exists(result_dir):os.makedirs(result_dir) 
    result_file_name = f"{result_dir}/{base_name}_{reason}.csv"
    if not os.path.exists(result_file_name):
        with open(result_file_name, 'a') as file:
            write = csv.writer(file)
            write.writerow(['Domain', 'Company', 'Reason', 'Time'])
    
    list_domain = []
    with open(result_file_name, 'r') as file:
        for row in csv.DictReader(file):
            domain = row['Domain']
            list_domain.append(domain)
    
    current_time = CurrentTime()
    
    if domain not in list_domain:
        if 'defined' in reason:
            print(f'{RED}Формы не обнаружены!{RESET}')
        if 'unknown' in reason:
            print(f"{RED}Неизвестное поле в форме. Задача подлежит ручной проверке{RESET}")
        if 'recaptcha' in reason:
            print(f'{RED}Обнаружено поле recaptcha{RESET}')
        with open(result_file_name, 'a+') as file:
            write = csv.writer(file)
            reason = reason.replace('_', ' ')
            write.writerow([domain, company, reason, current_time])
            print(f'{RED}[{current_time}] {domain} : {company} - {reason}{RESET}')
    

def RecordingSuccessSend(domain:str, company:str):
    if not os.path.exists(result_dir):os.makedirs(result_dir) 
    file_name = f"{result_dir}/{base_name}_success_send.csv"
    if not os.path.exists(file_name):
        with open(file_name, 'a') as file:
            write = csv.writer(file)
            write.writerow(['Domain', 'Company', 'Time'])
    
    current_time = CurrentTime()
    with open(file_name, 'a+') as file:
        write = csv.writer(file)
        write.writerow([domain, company, current_time])
        print(f'{GREEN}[{current_time}] Форма отправлена, результат зафиксирован{RESET}')
