from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from urllib3.exceptions import ReadTimeoutError

from SinCity.Browser.driver_chrome import driver_chrome
from SinCity.Browser.scrolling import Scrolling
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

###########################################################
#       Обработка других страниц,                         #
#       если не нашлось формы на основной странице"""     #
###########################################################
def OtherPages(driver:str, domain:str):
    source_code = SourcePage(driver=driver)
    bs = BeautifulSoup(source_code, 'lxml')
    list_link = set()
    for link in bs.find_all('a'):
        link_page = None
        try:
            link_page = link.attrs['href']
        except Exception as err:
            pass
        if link_page != None and 'mailto:' not in link_page:
            for page in contact_pages:
                if page in link_page:
                    url = link_page
                    if '/./' in url:url = url.replace('/./', '/')
                    if '://' not in url:url = f"https://{domain}{url}"
                    
                    list_link.add(url)
    
    return list_link

###########################################################
#           Получение исходного текста страницы           #
###########################################################
def SourcePage(driver:str):
    source_page = driver.page_source
    return source_page

###########################################################
#               Красивый разделитель                      #
###########################################################
def divide_line():
    divide = "-"*60
    return divide


###########################################################
#                   Входная функция                       #
###########################################################
def SubmitForms(domain:str, company:str):
    driver = None
    try:
        driver = driver_chrome()
        url = f"https://{domain}"
        driver.get(url)
        
        """Проверка редиректа. Если редиректит - прекращаем работу с доменом"""
        current_url = driver.current_url
        if domain not in current_url:
            print(f'{RED}Перенаправление домена: {domain} -> {current_url}{RESET}')
            if driver != None:
                driver.quit()
            return
        
        Scrolling(driver=driver)
        time.sleep(2)

        all_forms = SearchForms(driver=driver)
        if len(all_forms) != 0:
            processingForms(forms=all_forms, driver=driver, company=company)
        if len(all_forms) == 0:
            print(f'{RED}Формы на {url} не обнаружены!{RESET}')
            other_pages = OtherPages(driver=driver, domain=domain)
            if len(other_pages) > 0:
                number_page = 0
                print(other_pages)
                for page in other_pages:
                    number_page+=1
                    print(f'{BLUE}[{number_page}] {page}{RESET}')
                    driver.get(page)
                    Scrolling(driver=driver)
                    time.sleep(2)
                    other_forms = SearchForms(driver=driver)
                    if len(other_forms) > 0:
                        processingForms(forms=other_forms, driver=driver, company=company)
                        
            if len(other_pages) == 0:
                print(f"{RED}Страниц контактов не обнаружены!{RESET}")

    except KeyboardInterrupt:
        print(f'{RED}\nExit...{RESET}')

    except WebDriverException:
        print(f'{RED}Домен неактивен{RESET}')

    finally:
        if driver != None:
            driver.quit()
        sys.exit()

###########################################################
#                   Поиск форм                            #
###########################################################
def SearchForms(driver:str):
    list_forms = []

    source_page = SourcePage(driver=driver)
    bs = BeautifulSoup(source_page, 'lxml')

    for form in bs.find_all('form'):
        list_type_field = ['input', 'textarea']
        data_form = [] 
        
        count_textarea = 0

        for field in form.find_all(list_type_field):
            text_field = str(field)
            
            field_info = {}
            
            if 'input' in text_field and 'hidden' not in text_field:
                field_info['tag'] = 'input'

                name = field.get('name')
                type_field = field.get('type')

                field_info['name'] = name
                field_info['type'] = type_field
                field_info['placeholder'] = None

            if 'textarea' in text_field:
                field_info['tag'] = 'textarea'
                count_textarea+=1
                field_info['name'] = 'text'
                field_info['type'] = 'text'
                field_info['placeholder'] = None

            try:
                placeholder = field.attrs['placeholder']
                field_info['placeholder'] = placeholder
            except KeyError:
                pass 

            if len(field_info) > 0:data_form.append(field_info)
        
        """
        Если такого набора словарей нет в списке форм 
        + есть textarea + длина 
        списка полей больше одного - в этом случае форма 
        будет распознана, как контактная"""
        if data_form not in list_forms and count_textarea != 0 and len(data_form) > 1:
            list_forms.append(data_form)
            count_textarea = 0
        
    return list_forms

###########################################################
#               Обработка формы                           #
###########################################################
def processingForms(forms:list[list[dict]], driver:str, company:str):
    """Получаем список форм с полями для обработки"""
    for form in forms:
        success = ConfirmForm(driver=driver, form=form, company=company)
        if success == True:
            print(f"{GREEN}Форма успешно отправлена!{RESET}")
            return
        if success == False:
            print(f"{RED}Форма не отправлена!{RESET}")

###########################################################
#               Подтверждение и отправка формы            #
###########################################################
def ConfirmForm(driver:str, form:[], company:str):
    all_forms = driver.find_elements(By.TAG_NAME, 'form')

    for target_form in all_forms:
        
        for field in form:
            tag = field['tag']
            name = field['name']
            type_field = field['type']
            placeholder = field['placeholder']

            full_attrs = f"{tag} {name} {type_field} {placeholder}"
            content = GenerateContent(full_attrs=full_attrs, company=company)
             
            if content != False: 
                try:
                    if tag == 'textarea':
                        letter = target_form.find_element(
                                By.TAG_NAME, 'textarea'
                                )
                        letter.send_keys(content)
                    
                    elif name != None:
                        target_name = target_form.find_element(
                                By.NAME, name
                                )
                        target_name.send_keys(content)

                    elif placeholder != None: 
                        target_placeholder = target_form.find_element(
                                By.CSS_SELECTOR, f'[placeholder="{placeholder}"]'
                                )
                        target_placeholder.send_keys(content)

                    elif 'textarea' in full_attrs:
                        print('textarea содержится')
                        letter = target_form.find_element(By.CSS_SELECTOR, 'textarea')
                        letter.send_keys(content)

                
                    else:
                        print(f'{RED}Форму необходимо проверить вручную!{RESET}')
                        return False
                

                    input('...')

                except Exception as err:
                    print(err)
                
            


        
        

###########################################################
#               Для отладочных запусков                   #
###########################################################
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
###########################################################
#               Для отладочных запусков                   #
###########################################################
