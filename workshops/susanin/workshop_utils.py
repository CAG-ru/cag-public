def normalise_colnames(df):
    if '' in df.columns:
        df.drop([''], axis=1, inplace=True)
    normalised_colnames = [
        'name',
        'address',
        'director',
        'phone_no',
        'email',
        'title',
        'date',
        'year',
        'source'
        ]
    normalised_colnames_no_email = [
        'name',
        'address',
        'director',
        'phone_no',
        'title',
        'date',
        'year',
        'source'
        ]
    drop_colnames = [
        '№ п/п', 
        'Широта', 
        'Долгота', 
        'Перечень закрепленных за учреждением территорий',
        '№',
        'npp',
        'Сайт',
        'Официальный сайт',
        'shortName',
        'vice',
        'tasks',
        'okpo',
        'ogrn',
        'inn',
        'fax', 
        'otherTel',
        'WWW-сайт',
        'Сокращенное наименование',
        'Сокращённое наименование',
        'kulskazka2.ru"',
        'Адрес сайта'
    ]
    for drop_col in drop_colnames:
        if drop_col in df.columns:
            df.drop([drop_col], axis=1, inplace=True)
    if len(df.columns) == len(normalised_colnames):
        df.columns = normalised_colnames
    elif len(df.columns) + 1 == len(normalised_colnames):
        df.columns = normalised_colnames_no_email
    else:
        display(df.head(2), df.shape)
    df.drop(columns=['source', 'title'])
    return df

import re

def bad_sources(df):
    bad_sources_list = ['Большеболд', 'Наваш', 'Городец',
                       'Лукоян', 'Краснобак', 'Кстов']
    if 'Источник' in df.columns:
        for bs in bad_sources_list:
            if bs in df['Источник'].to_list()[0]:
                return True
    if 'source' in df.columns:
        for bs in bad_sources_list:
            if bs in df['source'].to_list()[0]:
                return True    

def normalise_order(df):
    directors = df.director.unique()
    addresses = df.address.unique()
    if any(map(lambda x: re.search('\d', x), directors)):
        if any(map(lambda x: re.search(r'-', x), directors)):
            if not any(map(lambda x: re.search('\d', x), addresses)):
                df.rename(mapper={
                    'address' : 'director',
                    'director' : 'phone_no',
                    'phone_no' : 'address'
                }, axis=1, inplace=True)
            else:
                display(df.head(1))
        else:
            df.rename(mapper={
                'director' : 'address',
                'address' : 'director'
            }, axis=1, inplace=True)
    addresses = df.address.unique()
    if not all(map(lambda x: re.search('[а-я]', x), addresses)):
        df.rename(mapper={
            'phone_no' : 'address',
            'address' : 'phone_no'
        }, axis=1, inplace=True)
    return df

def postprocess(df):
    def add_mun_1(row):
        #if row['municipality'] == 'None':
        #    row['municipality'] = row['municipality1']
        #    row['municipality_type'] = row['municipality1_type']
        return row
    return df.apply(add_mun_1, axis=1)