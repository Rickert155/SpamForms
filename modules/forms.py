from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from SinCity.Browser.driver_chrome import driver_chrome
from SinCity.colors import RED, GREEN, RESET, BLUE
from bs4 import BeautifulSoup
from modules.config import contact_pages
from modules.content import GenerateContent
from modules.miniTools import (
        RecordingNotSendedCompany, 
        RecordingSuccessSend,
        RecordingDoneDomain
        )
import sys, time

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
                link = f"{domain}/{link}"
                if 'https://' not in link and 'http://' not in link:
                    link = f"https://{link}"
                for page in contact_pages:
                    if page in link and '#' not in page:
                        list_link.add(link)
        except Exception as err:
            pass
            #print(f'error: {err}')
    
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
        count_form+=1
        count_textarea = 0

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
                    if 'textarea' in word:
                        count_textarea+=1
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
                        """
                        print(
                                f"\t[ - {number_field} - ]\n"
                                f"Type: {type_field}\n"
                                f"Name: {name_field}\n"
                                )
                        """
        if count_form == 0 or count_textarea == 0:
            print(f"Контактные формы не обнаружены")
            return None
        if count_form != 0 and len(fields_info) != 1:
            return fields_info
    

def Send(driver:str, fields:[], company:str, domain:str):
    count_status = len(fields)
    for target_form in driver.find_elements(By.TAG_NAME, 'form'):
        count_check = 0
        print(fields)
        for field in fields:
            name = field['name']
            for name_input in target_form.find_elements(By.NAME, name):
                field_name = name_input.get_attribute('name')
                if field_name == name:
                    count_check+=1
                    break
        if count_check == count_status:
            print("Форма подтверждена!")
            try:
                for field in fields:
                    name = field['name']
                    if 'recaptcha' in name:
                        RecordingNotSendedCompany(
                                domain=domain,
                                company=company,
                                reason="recaptcha"
                                )
                        return 
                    field = driver.find_element(By.NAME, name)
                    content_field = GenerateContent(name=name, company=company)
                    if content_field == False:
                        """
                        Если контент равен False, в таком случае 
                        это говорит, что поле не определено. Задачу 
                        следует передать ассистенту для ручной обработки
                        """
                        RecordingNotSendedCompany(
                                domain=domain, 
                                company=company, 
                                reason="unknown_field"
                                )
                        return
                    if content_field != False:
                        field.send_keys(content_field)
                        time.sleep(1)
                
                submit = driver.find_element(By.CSS_SELECTOR, '[type="submit"]')
                
                #submit.click()
                #time.sleep(2)
                input('test...')
                print(f"{GREEN}Форма отправлена!{RESET}")
                RecordingSuccessSend(domain=domain, company=company)
            except Exception as err:
                print(
                        f'{RED}При отправке формы произошла ошибка{RESET}\n'
                        f'{RED}Сайт следует проверить вручную!{RESET}\n'
                        f'{err}'
                        )
            finally:
                RecordingDoneDomain(domain=domain)

            break

        if count_check != count_status:
            RecordingNotSendedCompany(
                domain=domain, 
                company=company, 
                reason="unknown_field"
                )
                    

def divide_line():
    divide = "-"*60
    return divide

def SubmitForms(domain:str, company:str):
    driver = None
    try:
        print(f'{BLUE}Domain: {domain}{RESET}')
        driver = driver_chrome()
        url = f'https://{domain}'
        driver.get(url) 
    
        current_url  = driver.current_url
        if domain not in current_url:
            print(f'{RED}Перенаправление {url} на {current_url}{RESET}')
            driver.quit()
            return

        forms = SearchForms(driver=driver)
        """В этом коде не вижу необходимости в целом. Было для отладки"""
        if forms != None:
            # func submit
            Send(driver=driver, fields=forms, company=company, domain=domain)
            """
            Если же на главной странице есть форма - то заполняем
            и выходим
            """
            return

        count_sended = 0
        if forms == None:
            time.sleep(1)
            other_pages = OtherPages(driver=driver, domain=domain)
            if other_pages != None:
                number_page = 0
                for page in other_pages:
                    number_page+=1
                    if '://' in page:page = page.split('://')[1]
                    print(f"{BLUE}Contact page [{number_page}] {page}{RESET}")
                    print(page)
                    driver.get(f'https://{page}')
                    time.sleep(2)
                    check_form = SearchForms(driver=driver)
                    if check_form != None:
                        count_sended+=1
                        Send(
                                driver=driver, 
                                fields=check_form, 
                                company=company, 
                                domain=domain
                                )          
                        count_sended+=1
                        """
                        После заполнения первой же формы можно выйти 
                        из функции. Если ее заполнить не удалось - то нет смысла
                        пробовать другие формы(если они есть). Скорее всего на сайте
                        стоит защита от автоматизации и такую задачу лучше передать 
                        ассистенту
                        """
                        return
            if other_pages == None:
                print(f"{RED}На сайте не обнаружены страницы контактов!{RESET}")
                RecordingNotSendedCompany(
                        domain=domain, 
                        company=company, 
                        reason="not_defined"
                        )
                return
            elif count_sended == 0 and other_pages != None:
                print(f"{RED}Отправка формы не удалась!{RESET}")
                RecordingNotSendedCompany(
                        domain=domain, 
                        company=company, 
                        reason="not_defined"
                        )
                return

    
    except WebDriverException:
        print(f"{RED}Сайт не существует или недоступен{RESET}")
    finally:
        print(divide_line())
        if driver != None:
            driver.quit()

if __name__ == '__main__':
    try:
        params = sys.argv
        if len(params) > 1:
            domain = params[1]
            if '://' in domain:domain = domain.split('://')[1]
            SubmitForms(domain=domain, company='Rickert Company')
        if len(params) == 1:
            print("Передай переметрoм домен!")
            sys.exit()
    except KeyboardInterrupt:
        print(f"{RED}\nExit{RESET}")
