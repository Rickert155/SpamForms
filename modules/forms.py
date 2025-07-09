from SinCity.Browser.driver_chrome import driver_chrome
from SinCity.colors import RED, GREEN, RESET, BLUE
from bs4 import BeautifulSoup
from modules.config import contact_pages
import sys

"""Обработка других страниц, если не нашлось формы на основной странице"""
def OtherPages():
    for page in contact_pages:
        print(page)

"""Получение исходного текста страницы"""
def SourcePage(driver:str):
    source_page = driver.page_source
    return source_page

"""Поиск форма на странице"""
def SearchForms(driver:str):
    list_forms = []
    source_code = SourcePage(driver=driver)
    bs = BeautifulSoup(source_code, 'lxml')

    for form in bs.find_all('form'):
        print(form)

        list_fields = []
        
        field_dict = {} 
        field_form = []

        type_fields = ['input', 'textarea']
        number_field = 0
        for field in form.find_all(type_fields):
            field_string = str(field)
            words = field_string.split()
            for word in words:
                if 'required' in word:
                    if field not in list_fields:
                        number_field+=1
                        list_fields.append(field)
                        field_dict['type'] = field.get('type')
                        field_dict['name'] = field.get('name')
                        print(f"[{number_field}] Required field: {field}\n")
                        field_form.append(field_dict)
                        
        print(field_form)
        list_fields.clear()


def SubmitForms(domain:str):
    print(f'{BLUE}Domain: {domain}{RESET}')
    driver = driver_chrome()
    driver.get(f'http://{domain}')
    
    forms = SearchForms(driver=driver)
    #other_pages = OtherPages()
    
    driver.quit()

if __name__ == '__main__':
    params = sys.argv
    if len(params) > 1:
        domain = params[1]
        if '://' in domain:domain = domain.split('://')[1]
        SubmitForms(domain=domain)
    if len(params) == 1:
        print("Передай переметр домен!")
        sys.exit()
