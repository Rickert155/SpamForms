import requests, json, random, os
from bs4 import BeautifulSoup

agent_json = 'agent.json'

def check_agent_list(agent_list:str):
    global agent_json
    
    if os.path.exists(agent_list):
        agents = []
        with open(agent_list, 'r') as file:
            for line in file.readlines():
                line_agent = line.strip()
                agents.append(line_agent)
    
        data = {'user-agent':agents}

        with open(agent_json, 'w') as file:
            json.dump(data, file, sort_keys=True, indent=4)
    else:
        print(f'Файл со списком user-agent {agent_list} не найден')

def generate_agent():
    global agent_json
    if os.path.exists(agent_json):
        with open(agent_json, 'r') as file:
            agents = json.load(file)
            len_list_agents = len(agents['user-agent'])
            select_random_agent = random.randint(0, len_list_agents-1)
            agent = agents['user-agent'][select_random_agent]
    
        return agent
    else:
        print(
                'JSON с user-agent еще не создан, будет использоваться стандартный user-agent\n'
                'Используй функцию check_agent_list для создания JSON с user-agent'
                )

def header():
    agent = generate_agent()
    header = {
            'Content-Type':'text/html',
            'User-Agent':agent,
            'Accept-Encoding':'gzip',
            'Accept-Language':'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
            }
    return header


