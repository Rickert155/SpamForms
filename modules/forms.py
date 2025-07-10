from SinCity.Browser.driver_chrome import driver_chrome
from SinCity.colors import RED, GREEN, RESET, BLUE
from bs4 import BeautifulSoup
from modules.config import contact_pages
import sys

"""Обработка других страниц, если не нашлось формы на основной странице"""
def OtherPages(driver:str, domain:str):
    source_code = SourcePage(driver=driver)
    bs = BeautifulSoup(source_code, 'lxml')
    list_link = set()
    for link in bs.find_all('a'):
        try:
            link = link.attrs['href']
            if link:
                if domain not in link and '://' not in link:
                    """На некоторых ссылках могут быть первым символом слэш"""
                    if link[0] == '/':link = link[1:]
                    link = f"{domain}{link}"
                    if 'https://' not in link and 'http://' not in link:
                        link = f"https://{link}"
                    for page in contact_pages:
                        if page in link:
                            list_link.add(link)
        except Exception as err:
            print(f'error: {err}')
    
    if len(list_link) != 0:
        return list_link 
    if len(list_link) == 0:
        return None


"""Получение исходного текста страницы"""
def SourcePage(driver:str):
    source_page = driver.page_source
    return source_page

"""Поиск форма на странице"""
def SearchForms(driver:str):
    list_forms = []
    source_code = SourcePage(driver=driver)
    bs = BeautifulSoup(source_code, 'lxml')
    
    """
    На некоторых сайтах бывает по 2 одинаковые формы/набору полей
    По этой причине лучше их хранить в списке
    """
    list_fields = []
    
    """
    Нам по итогу нужна будет одна форма
    Если на страницу несколько форм - особо нет смысла 
    заполнять остальные
    """
    count_form = 0
    for form in bs.find_all('form'):
        print(form)
        count_form+=1

        fields_info = [] 
        
        """Список полей, которые насы интересуют"""
        type_fields = ['input', 'textarea']
        number_field = 0
        for field in form.find_all(type_fields):
            """Преобразуем в строку, что бы можно было без боли распарсить"""
            field_string = str(field)
            """сплитим весь текст"""
            words = field_string.split()
            """Перебираем текст, ещем обязательные поля/textarea"""
            for word in words:
                if 'required' in word or 'textarea' in word:
                    if field not in list_fields:
                        """Получаем значения атрибутов, которые нас интересуют"""
                        type_field = field.get('type')
                        name_field = field.get('name')
                        """
                        Полезно больше для textarea, там часто нет значений
                        text присвамиваем только что бы в дальнейшем 
                        не возникло ошибок из-за NoneType и подобного
                        """
                        if type_field == None:type_field = "text"
                        
                        number_field+=1
                        
                        """Уже фантазия кончилась на переменные"""
                        info = {
                                "field_number":number_field,
                                "type":type_field,
                                "name":name_field
                                }
                        fields_info.append(info)
                        
                        list_fields.append(field)
                        print(
                                f"[{number_field}] {field}\n"
                                f"Type: {type_field}\n"
                                f"Name: {name_field}\n"
                                )
    if count_form == 0:
        return None
    if count_form != 0 and len(fields_info) != 1:
        return fields_info
    


def SubmitForms(domain:str):
    print(f'{BLUE}Domain: {domain}{RESET}')
    driver = driver_chrome()
    driver.get(f'http://{domain}')
    
    forms = SearchForms(driver=driver)
    if forms != None:
        print(forms)
    if forms == None:
        print("На странице не обнаружена контактная форма")
        other_pages = OtherPages(driver=driver, domain=domain)
        if other_pages != None:
            number_page = 0
            for page in other_pages:
                number_page+=1
                print(f"[{number_page}] {page}")
        if other_pages == None:
            print(f"На сайте не обнаружены страницы контактов!")
    
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
