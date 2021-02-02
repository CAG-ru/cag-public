import os
from fuzzywuzzy import process
from normalization.yaspeller import use_yandexspeller


NORMALIZED_LOCATIONS = []

with open(os.path.join(os.path.dirname(__file__), 'normalized_locations.txt')) as f:
    for line in f.readlines():
        if not line.startswith('#') and (line != '\n'):
            NORMALIZED_LOCATIONS.append(line.strip())


def normalize_location_name(original_name):
    """приведение названий локаций к стандартному виду"""
    name = use_yandexspeller(original_name).lower()
    
    name = name.replace('авт.', 'автономный')
    name = name.replace('а.о.', 'автономный округ')
    name = name.replace('автономии', 'автономного округа')
    name = name.replace('кроме', 'без')
    name = name.replace('в том числе', '')
    name = name.replace('без кфо', 'без крымского федерального округа')
    
    if 'чечен' not in name:
        name = name.replace('ингушская', 'ингушетия')
    
    if ('тюмен' in name) and ('без' in name):
        before_bez = name[:name.find('без')+3]
        name = before_bez + 'автономий'
    
    closest_normalized_name = process.extractOne(name, NORMALIZED_LOCATIONS)[0]
    return closest_normalized_name


if __name__ == '__main__':
    test_string = '''
             Роиссийская
    федерация
    '''
    assert normalize_location_name(test_string) == 'Российская Федерация'
