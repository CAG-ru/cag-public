#!/usr/bin/env python3

import re
import string
import os
import json
import pandas as pd

from collections import Counter


def is_empty(text):
    if text.replace('\r', '').replace('\n', '').strip() == '' \
            or text == '' or text == 'nan':
        return True
    return False


def is_single_char(text):
    if len(text) == 1:
        return True
    return False


def is_hyphens(text):
    if text.replace('-', '').strip() == '':
        return True 
    return False


def is_underscores(text):
    if text.replace('_', '').strip()  == '':
        return True
    return False


def is_junk(text):
    return is_empty(text) or is_single_char(text) \
            or is_hyphens(text) or is_underscores(text)


def clean_up(text):
    text = str(text)
    text = text.strip()
    text = text.lower()
    text = text.replace('(место для текстового описания)', '')
    if is_junk(text):
        return '$#*!'
        
    text = text.rstrip('.')
    text = text.rstrip(';')
    text = text.replace('«', '"').replace('»', '"')
    return text

def remove_standard_form(text):
    if pd.isnull(text) or type(text) == int:
        return text
    text = text.replace('(указываются полное и краткое наименования)', '')
    text = text.replace('(есть/нет)', '')
    text = text.replace('(место для текстового описания)', '')
    text = text.replace('(дней с момента принятия проекта нормативного правового акта)', '')
    return text

# Поиск самых частых значений
def most_freq(series, num):
    return sorted(Counter(series).items(), key=lambda item: (-item[1], item[0]))[:num]

# Поиск самых коротких заполнений
def shortest(series, num):
    return sorted(Counter(series).items(), key=lambda item: (len(item[0]), item[1]))[:num]

# Добываем топ самых коротких и частых значений
def get_column_features(df, column, top_freq):
    cleaned_field = df[column].apply(clean_up)
    mf = pd.DataFrame(most_freq(cleaned_field, top_freq))
    sh = pd.DataFrame(shortest(cleaned_field, top_freq))
    return mf, sh


def fill_df_info(all_fields, dataframe, df_name):
    """
    Функция принимает датафрейм, сравнивает значение нужных полей
    с мусорными, проставляет соответствующую оценку
    и возвращает новый датафрейм
    """
    with open('normalization/junk/junk_by_field.json', 'r') as fp:
        junk_by_field = json.load(fp)
    
    if df_name not in all_fields.keys():
        print('No such table in dataset.')
        return
    
    if 'header: id' in dataframe.columns:
        id_column = 'header: id'
    else:
        id_column = 'id'
    
    result_df = pd.DataFrame()
    for index, row in dataframe.iterrows():
        result_df.loc[index, id_column] = row[id_column]
        
        for short, long in all_fields.get(df_name).items():    
            value = dataframe.loc[index, long]
            value = clean_up(value)

            # Проверяем, есть ли текущее вхождение 
            # в "мусоре" для этого поля
            junk_set = junk_by_field.get(short)
            if junk_set is not None and value in junk_set:
                valid = 0
            else:        
                valid = 1

            result_df.loc[index, short] = value
            result_df.loc[index, str(short + '_valid')] = valid
    return result_df


if __name__ == '__main__':
    # Нам нужно очистить их больше: всякие посторонние символы теперь будут мешать
    test = pd.Series([
    '', '\r', 'dfd\n', '\r\n', '\n\r\n', 
    'u', '.',
    '-', '- --', 
    '____', 
    'nan', 'нет',
    '(место для текстового описания)',
    '-(место для текстового описания)'
    ])
    test.apply(clean_up)