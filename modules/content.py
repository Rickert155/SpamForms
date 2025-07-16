from SinCity.colors import RED, RESET, BLUE
from modules.config import content_file_path
import json, sys

def Content(full_attrs:str, target_company:str):
    full_attrs = full_attrs.strip().lower()
    content = None
    try:
        with open(content_file_path, 'r') as file:
            data = json.load(file)
        first_name = data['first_name']
        last_name = data['last_name']
        user_name = data['name']
        full_name = data['full_name']
        email = data['email']
        phone = data['phone']
        company = data['company']
        your_project = data['your_project']
        site = data['site']
        subject = data['subject']
        message = data['message']
        
        template = "[AGENCY NAME]"
        subject = subject.replace(template, target_company)
        message = message.replace(template, target_company)

        if 'first' in full_attrs:content = first_name
        
        elif 'last' in full_attrs or 'surname' in full_attrs:content = last_name
        elif 'lnam' in full_attrs:content = last_name
        
        elif 'full' in full_attrs:content = full_name
        
        elif 'email' in full_attrs or 'mail' in full_attrs:content = email
        
        elif 'phone' in full_attrs:content = phone
        elif 'tele' in full_attrs:content = phone
        
        elif 'company' in full_attrs:content = company
        elif 'firma' in full_attrs:content = company
        
        elif 'project' in full_attrs:content = your_project
        
        elif 'site' in full_attrs or 'url' in full_attrs:content = site
        
        elif 'subj' in full_attrs or 'theme' in full_attrs:content = subject

        elif 'message' in full_attrs:content = message
        elif 'body' in full_attrs:content = message
        elif 'help' in full_attrs:content = message
        elif 'comment' in full_attrs:content = message
        elif 'nachricht' in full_attrs:content = message
        elif 'quest' in full_attrs:content = message
        elif 'textarea' in full_attrs:content = message
        
        elif 'name' in full_attrs:content = user_name
        elif 'naam' in full_attrs:content = user_name
        elif 'nome' in full_attrs:content = user_name
        
        else:
            return False

        return content

    except FileNotFoundError:
        print(f"{RED}Отсутствует файл с контентом: {content_file_path}{RESET}")
        sys.exit()
    except Exception as err:
        print(f"{RED}{err}{RESET}")

def GenerateContent(full_attrs:str, company:str):
    content = Content(target_company=company, full_attrs=full_attrs) 
    if content != False:
        print(f"{BLUE}{content}{RESET}")
        return content
    if content == False:
        return False


if __name__ == '__main__':
    params = sys.argv
    if len(params) > 1:
        full_attrs = params[1]
        GenerateContent(company='Rickert Tester', full_attrs=full_attrs)
    if len(params) == 1:
        print("Введите параметром имя!")
