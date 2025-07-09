import requests, json, os, time
from SinCity.Agent.header import header

DOMAIN = None

def get_domain():
    domain = input("Domain: ")
    if '//' in domain:domain = domain.split('//')[1]
    if '/' in domain:domain = domain.split('/')[0]
    if 'www.' in domain:domain = domain.split('www.')[1]
    if '@' in domain:domain = domain.split('@')[1]
    if '.' not in domain:domain = None
    try:
        a, b = domain.split('.')
        if len(a) <= 1 and len(b) <= 1:domain = None
    except:domain = None

    return domain

def plugins(file_name:str=None):
    list_plugins = []
    
    try:
        with open(file_name, 'r') as file:
            for plugin in file.readlines():
                if plugin not in list_plugins:list_plugins+=[plugin.strip()]
   
        return list_plugins
    
    except FileNotFoundError:
        with open(file_name, 'w') as file:file.close()
        print(
            f'Файл со списком плагинов не обнаружен: {file_name}\n'
            f'Файл {file_name} создан. Можете в него добавить список'
            ) 

counter_plugin = 0

def recording(data:dict):
    global DOMAIN
    file_name = f'{DOMAIN}.json'
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            info = {DOMAIN:[]}
            json.dump(info, file, indent=4)

    with open(file_name, 'r') as file:
        info = json.load(file)
    
    data["date"] = time.strftime("%d/%m/%Y")
    data["time"] = time.strftime("%H:%M")

    info[DOMAIN].append(data)
    with open(file_name, 'w') as file:
        json.dump(info, file, indent=4)


def processing_readme(response):
    global counter_plugin
    global LIST_PLUGINS
    divide_line = '*'*40
    
    pattern_line_tag = 'Stable tag: '

    plugin_name = None
    plugin_version = None
    number_lines = 0
    for line in response.iter_lines():
        number_lines+=1
        line = line.decode('utf-8')
        if number_lines == 1:plugin_name = line
        if 'Stable tag:' in line:plugin_version = line
    
    if '=' in plugin_name:plugin_name = plugin_name.replace('=', '')
    if '#' in plugin_name:plugin_name = plugin_name.replace('#', '')
    plugin_name = plugin_name.strip()
    if pattern_line_tag in plugin_version:
        plugin_version = plugin_version.split(pattern_line_tag)[1]
    plugin_version = plugin_version.strip()
    print(
            f'{divide_line}\n'
            f'[{counter_plugin}]\t\tDetected Plugin\n'
            f'Plugin: \t{plugin_name}\n'
            f'Version: \t{plugin_version}\n'
            f'{divide_line}\n'
            )
    data = {"plugin_name":plugin_name, "plugin_version":plugin_version}
    recording(data=data)

def scan_url(address:str):
    global counter_plugin
    head = header()
    try:
        response = requests.get(address, headers=head)
        if response.status_code != 404:
            address_readme = f'{address}/readme.txt'
            response = requests.get(address_readme, headers=head)
            if response.status_code == 200:
                counter_plugin+=1
                processing_readme(response)
    except requests.exceptions.ConnectionError as err:print(f'Error connect domain')

def processing(domain:str):
    add_protocol = 'http://'
    add_url = '/wp-content/plugins/'
    url = f'{add_protocol}{domain}{add_url}'
    
    url_admin = f'{add_protocol}{domain}/wp-login.php'
    response = requests.get(url_admin)
    if response.status_code != 404:
        list_plugins = plugins(file_name='plugins.txt')
        if list_plugins != None:
            for plugin in list_plugins:
                full_address_plugin = f'{url}{plugin}'
                scan_url(address=full_address_plugin)
    else:print(f'{domain} not WordPress...')

def Scanner():
    global DOMAIN
    try:
        domain = get_domain()
        DOMAIN, domain_info_json = domain, f'{domain}.json'
        if os.path.exists(domain_info_json):os.remove(domain_info_json)
        if domain != None:
            print(f'Processing domain {domain}...')
            try:
                processing(domain=domain)
            except requests.exceptions.ConnectionError as err:print(err)

    except KeyboardInterrupt:print('\nExit...')

