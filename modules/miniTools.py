from modules.config import (
        done_dir, 
        done_file_path,
        base_dir
        )
import os, csv, sys


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
