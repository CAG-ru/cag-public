import re


def remove_empty_rows(data):
    """
    Убрираем пустые строчки.
    Пустыми считаем те, у которых в основной (то есть первой) колонке ничего нет.
    """
    main_column = sorted(data.keys())[0]
    main_column_filled = [i for i, j in enumerate(data[main_column]) if j]

    for key in data.keys():
        col_values = data.get(key)
        if type(col_values) == list:
            data[key] = [col_values[i] for i in main_column_filled]


def split_cell(merged_cell):
    merged_cell = str(merged_cell)
    contents = [drop_punct(content) for content in merged_cell.split('|')]
    contents = cut_parenthesis(contents)
    if len(contents) >= 2:
        return contents
    elif len(contents) >= 1:
        return contents[0], ''
    else:
        return '', ''


def split_value(value):
    """
    Если после сплита второго столбца оказывается, что в первом больше значений,
    то обратно мёрджим первый столбец. Через какой символ?
    """
    value = value.strip()

    if value.startswith('-'):
        temp_split = [i for i in re.split(r'(-) ?', value) if i]
    elif value.startswith('1'):
        temp_split = [i for i in re.split(r'(\d+[.)])', value) if i]
    elif value.startswith('•'):
        # goals 93125
        temp_split = [i for i in re.split(r'(•)', value) if i]
    elif value.startswith('а)'):
        # goals 44971, 44976
        temp_split = [i for i in re.split(r'([а-я]+\))', value) if i]
    else:
        return value.split('\n')
    # s = re.split('\n+', value.replace(' | ', '\n').replace('\r', '\n'))

    split = []
    temp_string = ''
    for _ in range(len(temp_split)):
        temp_string += temp_split[_]
        if temp_split[_].endswith('\n') or _ == len(temp_split) - 1:
            split.append(temp_string)
            temp_string = ''

    return split


def cut_parenthesis(elems):
    if len(elems) >= 3:
        par = ''.join(elem.strip() for elem in elems[-3:])
        if par == '(место для текстового описания)':
            return elems[:-3]
    elif len(elems) >= 1:
        par = elems[-1]
        if par == '(место для текстового описания)':
            return elems[:-1]
    return elems


def remerge_cell(merged_cell):
    merged_cell = str(merged_cell)
    contents = [drop_punct(content) for content in merged_cell.split('|')]
    add_spaces = re.sub('\s{2,}', ' ', ''.join(contents))
    return re.sub('\.([а-яА-Я])', '. \g<1>', add_spaces)


def take_first(merged_cell):
    merged_cell = str(merged_cell)
    contents = [drop_punct(content) for content in merged_cell.split('|')]
    return contents[0]


def drop_punct(text):
    # if text.startswith('(') and text.endswith(')'):
    #    return text
    # else:
    #    return re.sub("\(.*\)", "", text).strip().strip(':')
    return text.strip().strip(':')


def guess_how_to_merge(cell_elems):
    contents = [drop_punct(content) for content in cell_elems]
    if len(contents) > 1:
        return remerge_cell(''.join(contents))
    else:
        return remerge_cell(cell_elems[0])


def name_value_one_col(table, data, rowr, col):
    for i, row in table.loc[rowr,].iterrows():
        cell = row[col]
        values = cell \
            .replace(':', ': | ') \
            .replace(': |  | ', ' | ') \
            .split(' | ')
        paragraph = drop_punct(values[0] + ' ' + values[1])
        if len(values) > 2:
            value = ' '.join(cut_parenthesis(values[2:]))
        else:
            value = ''
        data[paragraph] = value


def name_value_two_cols(table, data, rowr, value_col, index_col=0):
    '''
    для случаев, когда есть колонка с номером пункта (index col), 
    а название пункта и его наполнение лежат вместе в другой колонке (value col)
    rowr - это range строк, которые по такому типу записаны
    '''
    values = table.loc[rowr, value_col].apply(split_cell).to_list()
    # print(values)
    row_num = len(rowr)
    for i, j in zip(range(row_num), rowr):
        name = remerge_cell(str(table.loc[j, index_col])) + ' ' + values[i][0]
        value = guess_how_to_merge(values[i][1:])
        data[name] = value


def name_value_two_cols_2014(table, data, rowr, value_col, index_col=0):
    '''
    для случаев, когда есть колонка с номером пункта и заголовком (index col), 
    а наполнение лежит в отдельной колонке (value col)
    rowr - это range строк, которые по такому типу записаны
    '''
    names = table.loc[rowr, index_col].apply(split_cell).to_list()
    row_num = len(rowr)
    for i, j in zip(range(row_num), rowr):
        name = remerge_cell(names[i][0] + ' ' + names[i][1])
        value = remerge_cell(table.loc[j, value_col])
        data[name] = value


def name_value_three_cols(table, data, rowr, value_col, name_col, index_col=0):
    '''
    для случаев, когда есть колонка с номером пункта (index col),
    колонка с названием пункта name_col,
    а наполнение лежит отдельно в другой колонке (value col)
    rowr - это range строк, которые по такому типу записаны
    '''
    nums = table.loc[rowr, index_col].apply(remerge_cell).to_list()
    names = table.loc[rowr, name_col].apply(take_first).to_list()
    values = table.loc[rowr, value_col].apply(take_first).to_list()
    for i in range(len(nums)):
        name = nums[i] + ' ' + names[i]
        value = values[i]
        data[name] = value


def level_columns(data, key, name):
    """
    Выравниваем количество значений в name на основании key
    """
    # Если оказывается, что мы во второй столбец добавили больше значений,
    # то склеиваем значения в последних ячейках во втором столбце
    # Пример несовпадения количества: 77663 (сектор 7)
    if len(data[key]) < len(data[name]):
        count = len(data[name]) - len(data[key])
        data[name][-(count + 1)] = '; '.join(data[name][-(count + 1):])
        data[name] = data[name][:-count]
        pass
    # Дополняем список значений во втором столбце последним имеющимся
    # Пример несовпадения количества: 44382 (сектор 7)
    elif len(data[key]) > len(data[name]):
        data[name].extend([data[name][-1]]
                          * (len(data[key]) - len(data[name])))


def name_value_block(table, data, name_row, value_rowr, col):
    '''
    !!! Только для goals и groups
    Для вот таких случаев:
    
    номер | название
    значение1 | значение1
    значение2 | значение2
    ...
    
    Мы передаем номер левого столбца (col),
    номер строки, в которой находится "номер | название" (name_row)
    и range строк-значений (value_rowr)
    
    '''
    name = ' '.join([remerge_cell(table.loc[name_row, col]),
                     take_first(table.loc[name_row, col + 1])])
    if name not in data:
        data[name] = []
    for row in value_rowr:
        value = table.loc[row, col + 1]
        sv = split_value(value)
        if len(sv) > 1:
            # Случай, когда пункты перечислены внутри одной ячейки
            # Пример отчёта: 81230 (секция 7) или 81256 (секция 5)
            data[name].extend(sv)
        else:
            # Случай, когда пункты перечислены каждый в своей строчке
            # Пример отчёта: 35113 (секции 5 или 7)
            data[name].append(value)

    # Выравниваем количество значений во втором столбце на основании первого
    if col == 2:
        key_name = ' '.join([remerge_cell(table.loc[name_row, 0]),
                             take_first(table.loc[name_row, 1])])
        level_columns(data, key_name, name)


def name_value_block_2014(table, data, name_row, value_rowr, col):
    '''
    Для вот таких случаев:
    
    номер название
    значение1 
    значение2 
    ...
    
    Мы передаем номер столбца (col),
    номер строки, в которой находится "номер название" (name_row)
    и range строк-значений (value_rowr)
    
    '''
    name = remerge_cell(table.loc[name_row, col])
    if name not in data:
        data[name] = []
    for row in value_rowr:
        values = table.loc[row, col].split(' | ')
        for value in values:
            if not re.match('^\d\.$', value.strip()):  # это держится на соплях
                data[name].append(drop_punct(value))


def drop_empty(table):
    '''
    Выбрасываем строки, которые не заполнены полностью.
    Если в строке заполнена хотя бы одна ячейка, то оставляем.
    При этом возвращаем обратно пустые строки,
    чтобы не полезли баги из-за NaN в функциях, зависящих от этой.
    '''
    table.replace('', float('NaN'), inplace=True)
    table.dropna(how="all", inplace=True)
    table.replace(float('NaN'), '', inplace=True)
    table.reset_index(drop=True, inplace=True)


def row_index_by_text(table, text):
    '''
    ищем номер первой строчки, в которой в первом столбце есть text
    '''
    index_col = table.loc[:, 0].apply(remerge_cell)
    indices = index_col \
        .index[index_col.apply(lambda x: x.endswith(text))].to_list()
    if len(indices):
        return indices[0]


def row_index_by_text_2014(table, text):
    '''
    ищем номер первой строчки, в которой в первом столбце есть text
    '''
    index_col = table.loc[:, 0].apply(take_first)
    indices = index_col \
        .index[index_col.apply(lambda x: x.endswith(text))].to_list()
    if len(indices):
        return indices[0]


def grouped_values(table, data, drop_lines=1):
    local_table = table.T.drop_duplicates().T.copy().reset_index(drop=True)
    columns = local_table.loc[0, :].to_list()
    columns = [remerge_cell(x) for x in columns]

    for par_name in columns:
        data[par_name] = []

    for group, df in local_table.loc[1 + drop_lines:, :].groupby(0):
        drop_empty(df)
        for num, row in df.iterrows():
            contents = row.to_list()
            # Если строка (не считая группирующей колонки) пустая,
            # и это не первая строчка, то не добавляем её.
            # Нам нужно добавить первую строчку в любом случае, потому что бывает так:
            # заголовок | заголовок | заголовок
            # --------- | --------- | ---------
            # значение  | <пусто>   | <пусто>
            # <пусто>   | <пусто>   | <пусто>
            # ...
            if len("".join(contents[1:])) == 0 and num != 0:
                continue
            # Пытаемся разделить содержимое ячейки по переносам или ' | '.
            # Если это удаётся, считаем, что ячейка содержит перечисление.
            # Пример отчёта: 81230 (секция 13) или 77663 (секция 12).
            split_contents = list(map(lambda x: split_value(x), contents))
            if len(split_contents[0]) == 1:
                for i, par_name in enumerate(columns):
                    data[par_name].append(remerge_cell(contents[i]))
            else:
                # Если одно значение указано для всех пунктов.
                # Пример такого отчёта: 77663 ().
                for c in split_contents[1:]:
                    c.extend([c[0]] * (len(split_contents[0]) - 1)) \
                        if len(c) == 1 else None
                for i, par_name in enumerate(columns):
                    data[par_name].extend(split_contents[i])

# Используется только в risks_2014, которые не используются в актуальных схемах
# Может, удалить?
def grouped_values_2014(table, data, drop_lines=1):
    columns = table.loc[0, :].to_list()
    columns = [remerge_cell(x) for x in columns]

    for par_name in columns:
        data[par_name] = []

    for group, df in table.loc[1 + drop_lines:, :].groupby(0):
        for num, row in df.iterrows():
            contents = row.to_list()
            for i, par_name in enumerate(columns):
                data[par_name].append(contents[i])


def grouped_values_2016(table, data, header):
    columns = header.loc[0, :].to_list()
    columns = [remerge_cell(x) for x in columns]

    for par_name in columns:
        data[par_name] = []

    for group, df in table.groupby(0):
        drop_empty(df)
        for num, row in df.iterrows():
            contents = row.to_list()[1].split(' | ')
            value_columns = len(columns) - 1
            if len(contents) < value_columns:
                empty_num = value_columns - len(contents)
                contents += [''] * empty_num
            if len(contents) == value_columns:
                data[columns[0]].append(group)
                for i, par_name in enumerate(columns[1:]):
                    data[par_name].append(contents[i])
            # Случай, когда вложенная таблица состоит из нескольких строк.
            # Примеры отчётов: 81137 (секция 10) и 80445 (секция 14).
            else:
                cont_table = [contents[i:i + value_columns]
                              for i in range(0, len(contents), value_columns)]
                # Если одно значение указано для всех пунктов.
                # Пример такого отчёта: 77663 (секция 14.4).
                for c in cont_table[1:]:
                    c.extend([c[0]] * (len(cont_table[0]) - 1)) \
                        if len(c) == 1 else None
                transposed = [[_[i] for _ in cont_table]
                              for i in range(value_columns)]
                groups = [x for x in group.split('|') if x.isprintable()]
                if len(groups) < len(cont_table):
                    groups = [group] * (len(cont_table))
                data[columns[0]].extend(groups)
                for i, par_name in enumerate(columns[1:]):
                    data[par_name].extend(transposed[i])


recode_month = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12',
}


def date_2014_to_2016(day_month, year):
    dd, mm, yyyy = '00', '00', '0000'

    day_re = re.compile('«(.*)»')
    day_re_match = day_re.search(day_month)
    if day_re_match:
        dd = day_re_match.group(1).strip()
        if not re.search('\d\d', dd):
            dd = '00'

    month_re = re.compile('»(.*)')
    month_re_match = month_re.search(day_month)
    if month_re_match:
        mm = recode_month.get(month_re_match.group(1).strip(), '00')

    year_re_matches = re.compile('\d{4}').findall(year)
    if len(year_re_matches):
        yyyy = year_re_matches[0]

    return dd, mm, yyyy


def date_olde_to_2016(olde):
    olde = olde.lower()
    dd, mm, yyyy = '00', '00', '0000'

    day_re = re.compile('«(.*)»')
    day_re_match = day_re.search(olde)
    if day_re_match:
        dd = day_re_match.group(1).strip()
        if not re.search('\d\d', dd):
            dd = '00'

    month_re = re.compile('» ([а-я]*)')
    month_re_match = month_re.search(olde)
    if month_re_match:
        mm = recode_month.get(month_re_match.group(1).strip(), '00')

    year_re_matches = re.compile('\d{4}').findall(olde)
    if len(year_re_matches):
        yyyy = year_re_matches[0]

    return dd, mm, yyyy
