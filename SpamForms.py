from SinCity.Browser.driver_chrome import driver_chrome
from modules.miniTools import (
        initSpammer,
        ListBase,
        selectColumn
        )
            

def spamForms():
    initSpammer()

    list_base = ListBase()
    number_base=0
    for base in list_base:
        number_base+=1
        print(f'[{number_base}] {base}')
        """Определяем колонку с доменами/сайтами"""
        column_domain = selectColumn(base=base)

spamForms()
