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
            RecordingNotSendedCompany(
                domain=domain,
                company=company,
                reason="redirect_domain"
                        )
            if driver != None:
                driver.quit()
            return False
        
        Scrolling(driver=driver)
        time.sleep(2)

        all_forms = SearchForms(driver=driver)
        if len(all_forms) != 0:
            send = processingForms(
                    forms=all_forms, 
                    driver=driver, 
                    company=company,
                    domain=domain
                    )
            if send == True:
                return True
            if send == False:
                RecordingNotSendedCompany(
                    domain=domain,
                    company=company,
                    reason="unknown_field"
                        )
        if len(all_forms) == 0:
            print(f'{RED}Формы на {url} не обнаружены!{RESET}')
            other_pages = OtherPages(driver=driver, domain=domain)
            count_send = False
            if len(other_pages) > 0:
                number_page = 0
                for page in other_pages:
                    number_page+=1
                    print(f'{BLUE}[{number_page}] {page}{RESET}')
                    driver.get(page)
                    Scrolling(driver=driver)
                    time.sleep(2)
                    other_forms = SearchForms(driver=driver)
                    if len(other_forms) > 0:
                        send = processingForms(
                                forms=other_forms, 
                                driver=driver, 
                                company=company,
                                domain=domain
                                )
                        if send == True:
                            count_send = True
                            return True
            if count_send == False:
                print(f'{RED}Контактных форм не обнаружено!{RESET}')
                RecordingNotSendedCompany(
                    domain=domain, 
                    company=company,
                    reason="not_defined"
                    )

            if len(other_pages) == 0:
                print(f"{RED}Страниц контактов не обнаружены!{RESET}")
        
        return False 

    except KeyboardInterrupt:
        print(f'{RED}\nExit...{RESET}')
        sys.exit()

    except WebDriverException:
        print(f'{RED}Домен неактивен{RESET}')
        return False
    
    except ReadTimeoutError:
        print(f'{RED}Слишком долгое ожидание ответа!{RESET}')

    finally:
        if driver != None:
            driver.quit()

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
            
            if 'input' in text_field and 'hidden' not in text_field and 'submit' \
                    not in text_field:
                field_info['tag'] = 'input'
                name = field.get('name')
                type_field = field.get('type')
                id_field = field.get('id') or '' 

                field_info['id'] = id_field 
                field_info['name'] = name
                field_info['type'] = type_field
                field_info['placeholder'] = None
                field_info['class'] = None

                classes = field.get('class') or None
                text_classes = ''
                if classes == None:
                    text_classes = '' 
                if classes != None:
                    for class_ in classes:
                        text_classes = f"{text_classes}.{class_}"
                    if text_classes[0] == '.':text_classes = text_classes[1:]
                
                field_info['class'] = text_classes

            if 'textarea' in text_field:
                field_info['tag'] = 'textarea'
                count_textarea+=1
                field_info['name'] = field.get('name') or 'text'
                field_info['type'] = field.get('type') or 'text'
                field_info['placeholder'] = None
                field_info['id'] = '' 
                
                classes = field.get('class') or None
                text_classes = ''
                if classes == None:
                    text_classes = '' 
                if classes != None:
                    for class_ in classes:
                        text_classes = f"{text_classes}.{class_}"
                    if text_classes[0] == '.':text_classes = text_classes[1:]
                
                field_info['class'] = text_classes

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
def processingForms(forms:list[list[dict]], driver:str, company:str, domain:str):
    """Получаем список форм с полями для обработки"""
    for form in forms:
        if len(form) < 3:
            continue
        success = ConfirmForm(driver=driver, form=form, company=company)
        if success == True:
            print(f"{GREEN}Форма успешно отправлена!{RESET}")
            return True
        if success == False:
            print(f"{RED}Форма не отправлена!{RESET}")
            RecordingNotSendedCompany(domain=domain, company=company, reason="unknown_field")
            return False

###########################################################
#               Подтверждение и отправка формы            #
###########################################################
def ConfirmForm(driver:str, form:[], company:str):
    all_forms = driver.find_elements(By.TAG_NAME, 'form')
    
    for target_form in all_forms:
        """Чисто для отладки вывести количество форм на странице"""
        #print(f'Всего форм: {len(all_forms)}')

        input_fields = target_form.find_elements(By.TAG_NAME, 'input')
        all_fields_input = len(input_fields)
        """Показываем инпуты(их количество)"""
        #print(f'Всего {all_fields_input} инпутов')
        for input_field in input_fields:
            if input_field.is_displayed() == False:
                all_fields_input-=1
        """Показываем фактический остаток полей, которые не скрыты"""
        #print(f'Всего не скрытых полей {all_fields_input}')
        if all_fields_input < 2:
            continue

        matched_field = 0
        max_field = len(form)
        for field in form:
            tag = field['tag']
            name = field['name']
            type_field = field['type']
            placeholder = field['placeholder']
            class_name = field['class']
            id_field = field['id']

            full_attrs = (
                    f"{tag} {name} {type_field} "
                    f"{placeholder} {class_name}"
                    )
            if 'newsletter' in full_attrs:
                continue
            if 'recaptcha' in full_attrs:
                RecordingNotSendedCompany(
                    domain=domain,
                    company=company,
                    reason="recaptcha"
                    )
                return False
            if 'email' in type_field:
                full_attrs = 'email'
            if 'date' in type_field:
                all_fields_input-=1
                continue
            if 'file' in type_field:
                all_fields_input-=1
                continue
            content = GenerateContent(full_attrs=full_attrs, company=company)

            print(full_attrs)
            content_list = []
            list_class = []
            
            if content != False and content not in content_list:
                content_list.append(content)
                time.sleep(1)
                try:
                    if 'textarea' in full_attrs:
                        print(f'Обнаружено поле для ввода письма:')
                        content = GenerateContent(full_attrs="textarea", company=company)
                        print(content)
                        letter = target_form.find_element(By.TAG_NAME, 'textarea')
                        letter.send_keys(content)
                        matched_field+=1
                        continue

                    if len(id_field) > 1:
                        print(id_field)
                        element = target_form.find_element(By.ID, id_field)
                        element.send_keys(content)
                        matched_field+=1
                        continue


                    if 'checkbox' in full_attrs:
                        try:
                            print(f'Обнаружен чек-бокс')
                            for checkbox in target_form.find_elements(
                                    By.CSS_SELECTOR, 'checkbox'
                                    ):
                                checkbox.click()
                                matched_field+=1
                                continue
                        except:
                            print(f'{RED}Не удалось прожать чек-бокс!{RESET}')
                            return False
                    
                    elif placeholder != None: 
                        print(f'Ввод по placeholder: {placeholder}')
                        target_placeholder = target_form.find_element(
                                By.CSS_SELECTOR, f'[placeholder="{placeholder}"]'
                                )
                        target_placeholder.send_keys(content)
                        matched_field+=1
                        continue

                            
                    elif name != None:
                        print(f'Ввод {content} по name')
                        target_name = target_form.find_element(
                                By.NAME, name
                                )
                        target_name.send_keys(content)
                        matched_field+=1
                        continue

                    
                    elif len(class_name) >= 1:
                        if class_name not in list_class:
                            list_class.append(class_name)
                            print(class_name)
                            class_element = target_form.find_element(By.CLASS_NAME, class_name)
                            class_element.send_keys(content)
                            matched_field+=1
                            continue


                    else:
                        print(
                                f"{RED}Поле не получилось определить стандартным методом\n"
                                f"Пытаемся найти поле силами селениума!{RESET}"
                                )
                        for element in target_form.find_elements(By.TAG_NAME, tag):
                            print('тут исключение')
                            id_element = element.get_attribute('id')
                            element = element.find_element(By.ID, id_element)
                            element.send_keys(content)
                            matched_field+=1

                        if 'textarea' in full_attrs.lower():
                            textarea = target_form.find_element(By.TAG_NAME, 'textarea')
                            textarea.send_keys(content)
                            matched_field+=1
                except Exception as err:
                    print(err)
                
        """
        Тут пока что есть трудности с точным подсчетом полей
        По этой причине будем считать, что все ок, если форма отправилась
        """
        #if max_field == matched_field:
        try:
            submit = driver.find_element(By.CSS_SELECTOR, '[type="submit"]')
            """Для текстовых запусков комментируем клик по кнопке"""
            #submit.click()
            time.sleep(2)
            return True
        except:
            pass
        if max_field != matched_field:
            continue

    return False

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
