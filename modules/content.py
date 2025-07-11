from SinCity.colors import RED, RESET
from modules.config import content_file_path
import json, sys

def Content(name:str, target_company:str):
    name = name.strip().lower()
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

        if 'first' in name:content = first_name
        elif 'last' in name or 'surname' in name:content = last_name
        elif 'full' in name:content = full_name
        elif 'email' in name or 'mail' in name:content = email
        elif 'phone' in name:content = phone
        elif 'company' in name:content = company
        elif 'project' in name:content = your_project
        elif 'site' in name or 'url' in name:content = site
        elif 'subj' in name or 'theme' in name:content = subject
        elif 'message' in name:content = message
        elif 'body' in name:content = message
        elif 'name' in name:content = user_name

        else:
            return False

        return content

    except FileNotFoundError:
        print(f"{RED}Отсутствует файл с контентом: {content_file_path}{RESET}")
        sys.exit()
    except Exception as err:
        print(f"{RED}{err}{RESET}")

def GenerateContent(name:str, company:str):
    content = Content(name=name, target_company=company) 
    if content != False:
        print(f"Name: {name}\tContent: {content}")
        return content
    if content == False:
        return False


if __name__ == '__main__':
    params = sys.argv
    if len(params) > 1:
        name = params[1]
        GenerateContent(name=name, company="Testing Company")
    if len(params) == 1:
        print("Введите параметром имя!")
