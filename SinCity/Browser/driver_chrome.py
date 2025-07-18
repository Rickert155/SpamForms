from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from SinCity.Agent.header import header

def driver_chrome():
    profileChrome = 'ProfileChrome'

    head = header()['User-Agent']

    chrome_options = Options()
    #chrome_options.add_argument(f'--user-data-dir={profileChrome}')
    chrome_options.add_argument(f"--user-agent={head}")
    chrome_options.add_argument(f"--headless")

    chrome_options.add_argument(f"--incognito")
    chrome_options.add_argument("--dns-server=8.8.8.8")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--lang=en-US")

    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver_chrome = webdriver.Chrome(options=chrome_options)

    return driver_chrome
