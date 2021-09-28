#!/usr/bin/env python3

import re
import string

from text_utils.simple_cleanup import simple_clean

number_re = re.compile('^\d+$')
digit_re = re.compile('\d')

def remove_standard_form(ans):
    form_chunks = [
        u'7.1.7.',
        u'источники данных:',
        u'(место для текстового описания)',
        u'иные сведения о расходах (возможных поступлениях) бюджетов бюджетной системы российской федерации:',
        u'источники данных:',
        u'информация о программах мониторинга и иных способах (методах) оценки достижения заявленных целей регулирования:',
        u'описание источников информации для расчета показателей (индикаторов):',
    ]

    for chunk in form_chunks:
        ans = ans.replace(chunk, '')

    ans = ans.strip()
    return ans

def remove_junk(ans):
    ans = str(ans)
    ans = simple_clean(ans)

    if not ans:
        return ''

    ans = remove_standard_form(ans)

    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    no_punct = ans.translate(translator).strip()

    if len(no_punct) == 0:
        return ''

    #absence = (
    #    u'не установлена',
    #    u'информация отсутствует',
    #    )

    #if no_punct in absence:
    #    return ''

    return ans

def normalize_estimation(ans):
    if not ans:
        return ''

    ans = remove_junk(ans)
    
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    no_punct = str(ans).translate(translator).strip()

    absence = (
        u'отсутствует',
        u'отсутствуют',
        u'нет',
        u'не проводилась'
    )

    if no_punct.strip() in absence:
        return ''

    else:
        return ans


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


# Точка входа дворника
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


if __name__ == '__main__':
    assert not normalize_estimation('-')
    assert not normalize_estimation('источники данных: отсутствуют  (место для текстового описания)') 
