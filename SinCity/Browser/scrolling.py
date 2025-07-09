import time

def Scrolling(driver, timeout:int=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    number_scrolling = 0
    while True:

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(timeout) 
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break  
        last_height = new_height
