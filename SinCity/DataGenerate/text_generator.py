import random
from SinCity.DataGenerate.alphabet import alphabet_en, numbers, chars

def collected_char():
    list_char = []
    
    def collected(data_list:str):
        for data in data_list:
            list_char.append(data)
        
        return list_char

    collected(data_list=alphabet_en)
    collected(data_list=numbers)
    collected(data_list=chars)
    
    return list_char

def lower_or_upper(char:str):
    random_data = random.randint(1, 3)
    if type(char) == str:
        
        if random_data % 2 == 0:char = char.upper()
        else:char = char.lower()
    return char

def select_char(alphabet:list):
    char_select = random.randint(0, len(alphabet)-1)
    select = alphabet[char_select]
    return select


def generate_data(max_count:int):
    source_list_chars = collected_char()
    list_of_char = ''
    for generate_char in range(0, max_count):
        generate_char = select_char(alphabet=source_list_chars)
        generate_char = lower_or_upper(generate_char)
        list_of_char+=str(generate_char)
    
    return list_of_char 

def generator(max_word:int=1, max_count_char:int=5):
    collected = []
    for i in range(0, max_word):
        word = generate_data(max_count=max_count_char)
        collected.append(word)

    return collected
    
