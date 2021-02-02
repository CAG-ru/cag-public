import requests
import json
import re


def use_yandexspeller(bad_str):
    """исправление орфографических ошибок с помощью Яндекс.Спеллер"""
    post_str = re.sub(r'[^\w|\d]', '', bad_str.lower())
    if not post_str:
        return None
    
    with requests.Session() as s:
        url = 'https://speller.yandex.net/services/spellservice.json/checkText?text='
        r = s.get(url + post_str)
        
        if r.status_code != 200:
            print(f'GET error: {r.status_code}')
            return None
        
        jsn = r.content.decode('unicode-escape')
        jsn_dict = json.loads(jsn)
        
        if not jsn_dict:
            return bad_str
        
        ya_answer = jsn_dict[0]['s']
        if ya_answer:
            return ya_answer[0]
        else:
            return bad_str
