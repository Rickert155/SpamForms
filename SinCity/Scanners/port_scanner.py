import socket

def get_domain():
    domain = input("Domain: ")
    return domain

def CheckPort(domain:str, port:int):
    status = True
    cont = socket.socket()
    cont.settimeout(0.5)
    try:cont.connect((domain, port))
    except socket.error:status = False
    return status


def scanner(domain:str=None, min_port:int=1, max_port=80):
    if domain == None:domain = get_domain()
    domain = domain.strip()
    
    number_port = 0
    list_address = []

    for port in range(min_port, max_port+1):
        address = f"{domain}:{port}"
        if CheckPort(domain=domain, port=port):
            number_port+=1
            list_address+=[address]
            print(f"[+] {number_port} [+]\t{domain} : {port}")
        else:print(f"[x] x [x]\t{domain} : {port}")
    
    return list_address


