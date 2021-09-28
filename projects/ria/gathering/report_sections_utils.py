from parsing_helper import *


def header(report):
    data = {}
    table = report.contents[1]
    data['id'] = table.loc[0, 0].split(' | ')[1]
    data['start'] = table.loc[1, 2]
    data['end'] = table.loc[2, 2]
    return data


def general_info(report):
    data = {}
    table = report.find_table_by_name('Общая информация')[0]

    table = table.loc[:, [0, 2]]
    name_value_two_cols(table, data, range(7), 2)
    developer_name = drop_punct(' '.join(table.loc[7, :].to_list()))
    developer_value = ', '.join(table.loc[8:, 2])
    data[developer_name] = developer_value
    return data


def degree(report):
    data = {}
    name = 'Степень регулирующего воздействия проекта акта'
    table = report.find_table_by_name(name)[0]

    # поменяла: value_col = 2 (а было 1), name_col = 1 (а было 2)
    # потому что у нас Средняя - это значение, а не заголовок (кажется)
    name_value_three_cols(table, data, range(1), 2, 1)
    name_value_two_cols(table, data, range(1, 2), 1)
    return data


def problem(report):
    data = {}
    name = 'Описание проблемы, на решение которой направлен ' \
           'предлагаемый способ регулирования'
    table = report.find_table_by_name(name)[0]

    name_value_two_cols(table, data, range(6), 1)
    return data


def int_exp(report):
    data = {}
    table = report.find_table_by_name('Анализ международного опыта')[0]

    name_value_two_cols(table, data, range(2), 1)
    return data


def goals(report):
    data = {}
    table = report.find_table_by_name('Цели предлагаемого регулирования')[0]

    ground_index = row_index_by_text(table, '.3.')
    name_value_block(table, data, 0, range(1, ground_index), 0)
    name_value_block(table, data, 0, range(1, ground_index), 2)
    remove_empty_rows(data)

    name_value_two_cols(table, data, range(ground_index, len(table)), 1)
    return data


def description(report):
    data = {}
    table = report.find_table_by_name('Описание предлагаемого регулирования')[0]

    name_value_two_cols(table, data, range(4), 1)
    return data


def groups(report):
    data = {}
    name = 'Основные группы субъектов предпринимательской ' \
           'и иной экономической деятельности'
    table = report.find_table_by_name(name)[0]

    group_1_text = '(Описание группы субъектов предпринимательской ' \
                   'и иной экономической деятельности)'
    group_2_text = '(Описание иной группы участников отношений)'
    group_1_row = row_index_by_text(table, group_1_text)
    group_2_row = row_index_by_text(table, group_2_text)

    name_value_block(table, data, 0, range(group_1_row + 1, group_2_row), 0)
    name_value_block(table, data, 0, range(group_1_row + 1, group_2_row), 2)
    name_value_block(table, data, 0, range(group_2_row + 1, len(table) - 1), 0)
    name_value_block(table, data, 0, range(group_2_row + 1, len(table) - 1), 2)
    remove_empty_rows(data)

    name_value_two_cols(table, data, range(len(table) - 1, len(table)), 1)
    return data


def business(report):
    data = {}
    name = 'деятельность субъектов малого и среднего предпринимательства'
    table = report.find_table_by_name(name)[0]

    grouped_values(table[:5], data, drop_lines=0)
    name_value_one_col(table, data, range(5, 7), 0)

    # Заберем все категории издержек
    kinds = ['Содержательные издержки',
             'Информационные издержки',
             'Преимущества и (или) иные выгоды',
             'Итого']
    info_cols = {'Описание социально-экономических '
                 'последствий реализации проекта акта': 0,
                 'Единовременные': 2,
                 'Периодические': 5}

    for pos, kind in enumerate(kinds):
        if kind == 'Итого':
            continue # потому что он только для определения end_index
        for info, col in info_cols.items():
            # количество строк в категории может быть разным,
            # поэтому его нужно определять во время выполнения
            start_index = row_index_by_text(table, kind)
            end_index = row_index_by_text(table, kinds[pos + 1])
            rows_num = end_index - start_index 
            name = kind + ': ' + info
            values = [
                table.loc[start_index + i, col] for i in range(1, rows_num)
            ]
            next_index = start_index + rows_num
            data[name] = values
            
    # Итого        
    next_index = next_index + 1 # пропускаем строчку-подзаголовок «7.1.6. Итого»
    time_variants = ["единовременные", "периодические"]
    consequence_variants = ["издержки (содержательные и информационные)",
                            "преимущества и (или) иные выгоды"]
    # Можно было захардкодить эти четыре варианта, но это слишком лёгкий и понятный путь xD
    for consequence_variant in consequence_variants:
        for i, time_variant in enumerate(time_variants):
            name = f"Итого {time_variant} {consequence_variant}"
            value = table.loc[next_index, 2 + 3 * i] # согласен, что формула супер-интуитивная
            data[name] = value
        next_index = next_index + 1             
    
    # Источники
    name_value_one_col(table, data, range(next_index, next_index + 1), 0)
    next_index += 2

    # Меры по нагрузке
    name = 'Нормативно-правовые меры, ' \
           'предпринятые для сокращения диспропорций в нагрузке'
    value = table.loc[next_index, 1]
    next_index += 1
    data[name] = value

    name = 'Организационные меры, ' \
           'предпринятые для сокращения диспропорций в нагрузке'
    value = table.loc[next_index, 1]
    next_index += 1
    data[name] = value

    # Прогнозы
    grouped_values(table[next_index:len(table)], data, drop_lines=0)

    return data


def new_functions(report):
    data = {}
    table = report.find_table_by_name('Новые функции')[0]

    name_functions = remerge_cell(table.loc[0, 0])
    name_procedure = remerge_cell(table.loc[0, 1])
    name_expenses = remerge_cell(table.loc[0, 2])
    name_function_desc = '8.1 Наименование органа'

    functions = []
    i = 1
    while i < len(table):
        office_pattern = table.loc[i, 0]
        if 'Наименование органа' not in office_pattern:
            break
        else:
            function_desc = table.loc[i, 1]
            j = i + 1
            while j < len(table):
                office = table.loc[j, 0]
                if 'Наименование органа' in office:
                    break
                else:
                    procedure = table.loc[j, 1]
                    expenses = table.loc[j, 2]
                    office_tuple = (office, procedure, expenses)
                    if len("".join(office_tuple)) != 0 or j == 2:
                        functions.append((function_desc, office_tuple))
                    j = j + 1
        i = j

    data[name_functions] = []
    data[name_procedure] = []
    data[name_expenses] = []
    data[name_function_desc] = []

    for function_desc, offices in functions:
        if not len(''.join([*offices, function_desc])) == 0:
            office, procedure, expenses = offices
            data[name_functions].append(office)
            data[name_procedure].append(procedure)
            data[name_expenses].append(expenses)
            data[name_function_desc].append(function_desc)
    return data


def new_functions_2016(report):
    data = {}
    tables = report.find_table_by_name('Новые функции')

    table_headers = tables[0]
    table_values = tables[1]

    name_functions = remerge_cell(table_headers.loc[0, 0])
    name_procedure = remerge_cell(table_headers.loc[0, 1])
    name_expenses = remerge_cell(table_headers.loc[0, 2])
    name_function_desc = '8.1 Наименование органа'

    functions = []
    i = 0
    while i < len(table_values):
        # print(f'i: {i}')
        office_pattern = table_values.loc[i, 0]
        # print(f'office_pattern: {office_pattern}')
        if 'Наименование органа' not in office_pattern:
            # print(f'!!!')
            break
        else:
            function_desc = table_values.loc[i, 1]
            j = i + 1
            # print(f'j: {j}')
            while j < len(table_values):
                office = table_values.loc[j, 0]
                # print(f'office: {office}')
                if 'Наименование органа' in office:
                    # print(f'???')
                    break
                else:
                    procedure = table_values.loc[j, 1]
                    expenses = table_values.loc[j, 2]
                    office_tuple = (office, procedure, expenses)
                    if len("".join(office_tuple)) != 0 or j == 1:
                        functions.append((function_desc, office_tuple))
                    j = j + 1
        i = j

    data[name_functions] = []
    data[name_procedure] = []
    data[name_expenses] = []
    data[name_function_desc] = []

    for function_desc, offices in functions:
        if not len(''.join([*offices, function_desc])) == 0:
            office, procedure, expenses = offices
            data[name_functions].append(office)
            data[name_procedure].append(procedure)
            data[name_expenses].append(expenses)
            data[name_function_desc].append(function_desc)
    return data


def expenses(report):
    data = {}
    table = report.find_table_by_name('Оценка соответствующих расходов')[0]

    name_functions = remerge_cell(table.loc[0, 0])
    name_41 = '9.4.1 Наименование органа'
    name_42 = '9.4.2 Единовременные расходы в год возникновения'
    name_43 = '9.4.3 Периодические расходы за период'
    name_44 = '9.4.4 Возможные поступления за период'

    data[name_functions] = []
    data[name_41] = []
    data[name_42] = []
    data[name_43] = []
    data[name_44] = []

    i = 1
    office = ''
    while i < len(table):
        paragraph = table.loc[i, 0]
        if paragraph == '9.4.':
            office = remerge_cell(table.loc[i, 2])
            i = i + 1
            continue
        elif paragraph == '9.5.':
            break
        else:
            j = i
            function_descs = []
            while j < len(table):
                paragraph = table.loc[j, 0]
                if paragraph in ['9.4.', '9.5.']:
                    i = j
                    break
                function_desc = table.loc[j, 1]
                first_year_exp = table.loc[j, 4]
                yearly_exp = table.loc[j + 1, 3]
                yearly_income = table.loc[j + 2, 3]
                function_desc_tuple = (function_desc, first_year_exp,
                                       yearly_exp, yearly_income)
                if not len(''.join(function_desc_tuple)) == 0:
                    function_descs.append(function_desc_tuple)
                j = j + 3
            if len(function_descs) != 0:
                for function_desc_tuple in function_descs:
                    function_desc, first_year_exp, yearly_exp, yearly_income = \
                        function_desc_tuple
                    data[name_functions].append(function_desc)
                    data[name_41].append(office)
                    data[name_42].append(first_year_exp)
                    data[name_43].append(yearly_exp)
                    data[name_44].append(yearly_income)
        i = j

    name_value_three_cols(table, data, range(i, i + 3), 4, 1)
    name_value_two_cols(table, data, range(i + 3, len(table)), 1)
    return data


def expenses_2016(report):
    data = {}
    name = 'Оценка соответствующих расходов'
    header, values, rest = report.find_table_by_name(name)

    name_functions = remerge_cell(header.loc[0, 0])
    name_41 = '9.4.1 Наименование органа'
    name_42 = '9.4.2 Единовременные расходы в год возникновения'
    name_43 = '9.4.3 Периодические расходы за период'
    name_44 = '9.4.4 Возможные поступления за период'

    data[name_functions] = []
    data[name_41] = []
    data[name_42] = []
    data[name_43] = []
    data[name_44] = []

    i = 0
    office = ''
    while i < len(values):
        paragraph = values.loc[i, 0]
        if paragraph.endswith('4.'):
            office = remerge_cell(values.loc[i, 2])
            i = i + 1
            continue
        else:
            j = i
            function_descs = []
            while j < len(values):
                paragraph = values.loc[j, 0]
                if paragraph.endswith('4.'):
                    i = j
                    break
                function_desc_as_list = paragraph.split(' | ')
                # В этом коде и так много костылей, поэтому ещё один не помешает.
                # Если в таблице какие-то ячейки не заполнены (то есть ничего не написано или стоит пробел),
                # то длина списка будет недостаточной, и мы получим list index out of range.
                # В результате таблица expenses не распарсится.
                # Поэтому мы проверяем длину списка, и если она недостаточная,
                # то включаем другой алгоритм обработки, который худо-бедно вытягивает нужные значения.
                # Возможно, этот «другой» алгоритм, несмотря на всю его неопрятность и костыльность,
                # можно было бы сделать основным, так как вообще-то он довольно универсальный.
                # Но поскольку тогда могут неожиданно вылезти какие-то неожиданные проблемы,
                # то лучше оставить как есть.
                if len(function_desc_as_list) > 12:
                    function_desc = function_desc_as_list[1]
                    first_year_exp = function_desc_as_list[4]
                    yearly_exp = function_desc_as_list[8]
                    yearly_income = function_desc_as_list[12]
                else:
                    fd_list_selected = [
                        x for x in function_desc_as_list
                        if x not in ":"
                           and not x.startswith(("Едино", "Период", "Возм"))
                    ]
                    vals = []
                    for i, el in enumerate(fd_list_selected):
                        el = str(el)
                        if el.startswith("9.4."):
                            if i == len(fd_list_selected) - 1:
                                val = ""
                            else:
                                val = str(fd_list_selected[i + 1])
                            if val.startswith("9.4."):
                                val = ""
                            vals.append(el)
                            vals.append(val)
                    if len(vals) == 8:
                        function_desc = vals[1]
                        first_year_exp = vals[3]
                        yearly_exp = vals[5]
                        yearly_income = vals[7]
                    else:
                        raise Exception("Incorrect № of values in expenses")
                function_desc_tuple = (function_desc, first_year_exp,
                                       yearly_exp, yearly_income)
                if not len(''.join(function_desc_tuple)) == 0:
                    function_descs.append(function_desc_tuple)
                j = j + 1
            if len(function_descs) != 0:
                for function_desc_tuple in function_descs:
                    function_desc, first_year_exp, yearly_exp, yearly_income = \
                        function_desc_tuple
                    data[name_functions].append(function_desc)
                    data[name_41].append(office)
                    data[name_42].append(first_year_exp)
                    data[name_43].append(yearly_exp)
                    data[name_44].append(yearly_income)
        i = j

    name_value_three_cols(rest, data, range(0, 3), 2, 1)
    name_value_two_cols(rest, data, range(3, len(rest)), 1)
    return data


def expenses_high_2016(report):
    data = {}
    name = 'Оценка соответствующих расходов'
    header, values = report.find_table_by_name(name)

    name_functions = remerge_cell(header.loc[0, 0])
    name_41 = '9.4.1 Наименование органа'
    name_42 = '9.4.2 Единовременные расходы в год возникновения'
    name_43 = '9.4.3 Периодические расходы за период'
    name_44 = '9.4.4 Возможные поступления за период'

    data[name_functions] = []
    data[name_41] = []
    data[name_42] = []
    data[name_43] = []
    data[name_44] = []

    i = 0
    office = ''
    while i < len(values):
        paragraph = values.loc[i, 0]
        if paragraph.endswith('.4.'):
            office = remerge_cell(values.loc[i, 3])
            i = i + 1
            continue
        if paragraph.endswith('.5.'):
            break
        else:
            j = i
            function_descs = []
            while j < len(values):
                paragraph = values.loc[j, 0]
                if paragraph.endswith('4.') or paragraph.endswith('5.'):
                    break
                function_desc_as_list = paragraph.split(' | ')
                # В этом коде и так много костылей, поэтому ещё один не помешает.
                # Если в таблице какие-то ячейки не заполнены (то есть ничего не написано или стоит пробел),
                # то длина списка будет недостаточной, и мы получим list index out of range.
                # В результате таблица expenses не распарсится.
                # Поэтому мы проверяем длину списка, и если она недостаточная,
                # то включаем другой алгоритм обработки, который худо-бедно вытягивает нужные значения.
                # Возможно, этот «другой» алгоритм, несмотря на всю его неопрятность и костыльность,
                # можно было бы сделать основным, так как вообще-то он довольно универсальный.
                # Но поскольку тогда могут неожиданно вылезти какие-то неожиданные проблемы,
                # то лучше оставить как есть.
                if len(function_desc_as_list) > 12:
                    function_desc = function_desc_as_list[1]
                    first_year_exp = function_desc_as_list[4]
                    yearly_exp = function_desc_as_list[8]
                    yearly_income = function_desc_as_list[12]
                else:
                    fd_list_selected = [
                        x for x in function_desc_as_list
                        if x not in ":"
                           and not x.startswith(("Едино", "Период", "Возм"))
                    ]
                    vals = []
                    for i, el in enumerate(fd_list_selected):
                        el = str(el)
                        if el.startswith("9.4."):
                            if i == len(fd_list_selected) - 1:
                                val = ""
                            else:
                                val = str(fd_list_selected[i + 1])
                            if val.startswith("9.4."):
                                val = ""
                            vals.append(el)
                            vals.append(val)
                    if len(vals) == 8:
                        function_desc = vals[1]
                        first_year_exp = vals[3]
                        yearly_exp = vals[5]
                        yearly_income = vals[7]
                    else:
                        raise Exception(
                            "Incorrect number of values in expenses")
                function_desc_tuple = (function_desc, first_year_exp,
                                       yearly_exp, yearly_income)
                if not len(''.join(function_desc_tuple)) == 0:
                    function_descs.append(function_desc_tuple)
                j = j + 1
            if len(function_descs) != 0:
                for function_desc_tuple in function_descs:
                    function_desc, first_year_exp, yearly_exp, yearly_income = function_desc_tuple
                    data[name_functions].append(function_desc)
                    data[name_41].append(office)
                    data[name_42].append(first_year_exp)
                    data[name_43].append(yearly_exp)
                    data[name_44].append(yearly_income)
        i = j

    name_value_three_cols(values, data, range(i, i + 3), 4, 3)
    name_value_two_cols(values, data, range(i + 3, len(values)), 1)
    return data


def group_changes(report):
    data = {}
    name = 'Новые преимущества, а также обязанности или ограничения ' \
           'для субъектов предпринимательской и иной экономической деятельности'
    table = report.find_table_by_name(name)[0]

    grouped_values(table, data)
    return data


def group_changes_2016(report):
    data = {}
    name = 'Новые преимущества, а также обязанности или ограничения ' \
           'для субъектов предпринимательской и иной экономической деятельности'
    header, values = report.find_table_by_name(name)

    grouped_values_2016(values, data, header)
    return data


def group_expenses(report):
    data = {}
    name = 'Оценка расходов и доходов субъектов предпринимательской ' \
           'и иной экономической деятельности'
    table = report.find_table_by_name(name)[0]

    grouped_values(table, data)
    return data


def group_expenses_2016(report):
    data = {}
    name = 'Оценка расходов и доходов субъектов предпринимательской ' \
           'и иной экономической деятельности'
    header, values = report.find_table_by_name(name)

    grouped_values_2016(values.iloc[:len(values) - 1, [0, 2]], data, header)
    name_value_two_cols(values, data, range(len(values) - 1, len(values)), 1)
    return data


def cancel_duties(report):
    data = {}
    table = report.find_table_by_name('Информация об отмене обязанностей')[0]

    grouped_values(table[:len(table) - 1], data, 0)
    name_value_two_cols(table, data, range(len(table) - 1, len(table)), 1)
    return data


def risks(report):
    data = {}
    name = 'Риски решения проблемы предложенным способом регулирования'
    table = report.find_table_by_name(name)[0]

    grouped_values(table[0:len(table) - 1], data, 0)
    name_value_two_cols(table, data, range(len(table) - 1, len(table)), 1)
    return data


def risks_low(report):
    data = risks(report)

    # В отчётах для низкого уровня регулирующего воздействия не указаны:
    name_12_3 = '12.3. Методы контроля эффективности избранного способа ' \
                'достижения целей регулирования'
    name_12_4 = '12.4. Степень контроля рисков'
    risks_count = len(data[sorted(data.keys())[0]])
    data[name_12_3] = ['non-applicable'] * risks_count
    data[name_12_4] = ['non-applicable'] * risks_count
    return data


def necessary_measures(report):
    data = {}
    name = 'Необходимые для достижения заявленных целей регулирования'
    table = report.find_table_by_name(name)[0]

    grouped_values(table[0:len(table) - 1], data, 0)
    name_value_three_cols(table, data, range(len(table) - 1, len(table)),
                          len(table.columns) - 1, 1)
    return data


def kpi(report):
    data = {}
    table = report.find_table_by_name('Индикативные показатели')[0]

    grouped_values(table[0:len(table) - 3], data, 0)
    name_value_two_cols(table, data, range(len(table) - 3, len(table) - 2), 1)
    name_value_three_cols(table, data, range(len(table) - 2, len(table) - 1),
                          len(table.columns) - 1, 1)
    name_value_two_cols(table, data, range(len(table) - 1, len(table)), 1)
    return data


def kpi_2016(report):
    data = {}
    header, values, rest = report.find_table_by_name('Индикативные показатели')

    grouped_values_2016(values, data, header)
    name_value_two_cols(rest, data, range(0, 1), 1)
    name_value_three_cols(rest, data, range(1, 2), 2, 1)
    name_value_two_cols(rest, data, range(2, 3), 1)
    return data


def supposed_date(report):
    data = {}
    name = 'Предполагаемая дата вступления в силу проекта акта'
    table = report.find_table_by_name(name)[0]

    name_value_three_cols(table, data, range(1), len(table.columns) - 1, 1)
    name_value_two_cols(table, data, range(1, 2), 1)
    name_value_two_cols(table, data, range(1, 2), 3, 2)
    name_value_two_cols(table, data, range(2, len(table)), 1)
    return data


def notification_info(report):
    data = {}
    table = report.find_table_by_name('Сведения о размещении уведомления')[0]

    name_value_two_cols(table, data, range(1), 1)
    suggestion_acceptance_period_paragraph = remerge_cell(table.loc[1, 0])
    suggestion_acceptance_period_name = remerge_cell(table.loc[1, 1])
    name = ' '.join([suggestion_acceptance_period_paragraph,
                     suggestion_acceptance_period_name])
    start = table.loc[2, 2]
    end = table.loc[3, 2]

    data[name] = [start, end]

    name_value_two_cols(table, data, range(4, len(table)), 1)
    return data


def anticorr_expertise(report):
    """
    Были обнаружены следующие 4 ситуации:
    - Подстрока "(при наличии):" находится в той же строке, что и текст до неё
    -- Значение заполнено или подставлено из шаблона
    -- Значения нет (совсем нет, пусто)
    - Подстрока "(при наличии):" находится в следующей строчке
    -- Значение заполнено или подставлено из шаблона
    -- Значения нет (совсем нет, пусто)
    """
    data = {}
    name = 'Сведения о проведении независимой антикоррупционной экспертизы'
    table = report.find_table_by_name(name)[0]

    name_value_three_cols(table, data, range(1), 2, 1)
    factors_paragraph = remerge_cell(table.loc[1, 0])
    delimiter = '(при наличии):'
    splitted_cell = table.loc[1, 1].split(delimiter)
    factors_name = drop_punct(splitted_cell[0].split('|')[0])
    factors_value = drop_punct(splitted_cell[1].split('|')[1])
    if factors_value == '(':
        factors_value = ''

    data[factors_paragraph + ' ' + factors_name] = factors_value
    return data


def other_notification_info(report):
    data = {}
    name = 'Иные сведения, которые, по мнению разработчика'
    table = report.find_table_by_name(name)[0]

    name_value_two_cols(table, data, range(len(table)), 1)
    return data


def public_discussion(report):
    data = {}
    name = 'Сведения о проведении публичного обсуждения проекта акта'
    table = report.find_table_by_name(name)[0]

    name_value_two_cols(table, data, range(1), 1)

    public_discussion_paragraph = remerge_cell(table.loc[1, 0])
    public_discussion_period_name = remerge_cell(table.loc[1, 1])
    public_discussion_name = ' '.join([public_discussion_paragraph,
                                       public_discussion_period_name])
    public_discussion_start = table.loc[2, 2]
    public_discussion_end = table.loc[3, 2]

    data[public_discussion_name] = [public_discussion_start,
                                    public_discussion_end]

    name_value_two_cols(table, data, range(4, len(table)), 1)
    return data


# region 2014


def header_2014(report):
    data = {}
    table = report.contents[1]
    id_cell = table.loc[0][0].split(' | ')
    if len(id_cell) == 3:
        data['id'] = id_cell[2]
    else:
        # надо вводить internal_id, который будет совпадать с номером отчета
        data['id'] = 'xxx'
    date_cell = table.loc[0][1].split(' | ')
    start = date_2014_to_2016(date_cell[2], date_cell[3])
    end = date_2014_to_2016(date_cell[6], date_cell[7])
    data['start'] = '.'.join(start)
    data['end'] = '.'.join(end)
    return data


def general_info_2014(report):
    data = {}
    table = report.find_table_by_name('Общая информация')[0]

    dev_cell = table.loc[0, 0].split(' | ')
    par = drop_punct(dev_cell[1] + ' ' + dev_cell[0])
    dev = drop_punct(dev_cell[2])
    data[par] = dev

    name_value_one_col(table, data, range(1, len(table)), 0)
    return data


def degree_2014(report):
    data = {}
    name = 'Степень регулирующего воздействия проекта акта'
    table = report.find_table_by_name(name)[0]

    name_value_two_cols_2014(table, data, range(1), 1)
    name_value_one_col(table, data, range(1, 2), 0)
    return data


def degree_2014_low(report):
    data = {}
    name = 'Степень регулирующего воздействия проекта акта'
    table = report.find_table_by_name(name)[0]

    name_value_two_cols_2014(table, data, range(1), 1)
    name_value_one_col(table, data, range(1, 2), 0)
    return data


def problem_2014(report):
    data = {}
    name = 'Описание проблемы, на решение которой направлен ' \
           'предлагаемый способ регулирования'
    table = report.find_table_by_name(name)[0]

    name_value_one_col(table, data, range(6), 0)
    return data


def int_exp_2014(report):
    data = {}
    table = report.find_table_by_name('Анализ международного опыта')[0]

    name_value_one_col(table, data, range(2), 0)
    return data


def goals_2014(report):
    data = {}
    table = report.find_table_by_name('Цели предлагаемого регулирования')[0]

    ground_index = row_index_by_text_2014(table, '.3.')
    name_value_block_2014(table, data, 0, range(1, ground_index), 0)
    name_value_block_2014(table, data, 0, range(1, ground_index), 1)
    name_value_one_col(table, data, range(ground_index, len(table)), 0)
    return data


def goals_2014_low(report):
    data = {}
    table = report.find_table_by_name('Цели предлагаемого регулирования')[0]

    name_value_block_2014(table, data, 0, range(1, 2), 0)
    name_value_block_2014(table, data, 0, range(1, 2), 1)
    name_value_one_col(table, data, range(2, len(table)), 0)
    return data


def description_2014(report):
    data = {}
    table = report.find_table_by_name('Описание предлагаемого регулирования')[0]

    name_value_one_col(table, data, range(len(table)), 0)
    return data


def groups_2014(report):
    data = {}
    name = 'Основные группы субъектов предпринимательской ' \
           'и иной экономической деятельности'
    table = report.find_table_by_name(name)[0]

    name_value_block_2014(table, data, 0, range(1, len(table) - 1), 0)
    name_value_block_2014(table, data, 0, range(1, len(table) - 1), 1)

    name_value_one_col(table, data, range(len(table) - 1, len(table)), 0)
    return data


def new_functions_2014(report):
    data = {}
    table = report.find_table_by_name('Новые функции')[0]
    grouped_values(table, data, drop_lines=1)
    return data


def expenses_2014(report):
    data = {}
    table = report.find_table_by_name('Оценка соответствующих расходов')[0]

    # Название функции лежит прямо в заголовке
    function_cell = table.loc[0, 0].split(' | ')
    name_functions = drop_punct(' '.join(function_cell[:2]))
    if len(function_cell) > 2:
        function_desc = remerge_cell(function_cell[2:])
    else:
        function_desc = ''
    data[name_functions] = [function_desc]

    # Название органа тоже лежит прямо в заголовке
    name_41 = '9.4.1 Наименование органа'
    office_cell = table.loc[1, 0].split(' | ')
    if len(office_cell) > 2:
        office_desc = remerge_cell(office_cell[2:])
    else:
        office_desc = ''
    data[name_41] = [office_desc]

    name_42 = '9.4.2 Единовременные расходы в год возникновения'
    name_43 = '9.4.3 Периодические расходы за период'
    name_44 = '9.4.4 Возможные поступления за период'

    data[name_42] = [drop_punct(table.loc[2, 2])]
    data[name_43] = [drop_punct(table.loc[3, 2])]
    data[name_44] = [drop_punct(table.loc[4, 2])]

    name_value_two_cols_2014(table, data, range(5, 8), 2)
    name_value_one_col(table, data, range(8, 9), 0)

    source_cell = table.loc[9, 0].split(' | ')
    source_name = '9.9. Источники данных:'
    source_value = drop_punct(' '.join(source_cell[2:]))
    data[source_name] = source_value

    return data


def group_changes_2014(report):
    data = {}
    table = report.find_table_by_name('Новые обязанности или ограничения')[0]

    grouped_values(table, data)
    return data


def group_expenses_2014(report):
    data = {}
    name = 'Оценка расходов субъектов предпринимательской'
    table = report.find_table_by_name(name)[0]

    grouped_values(table[:len(table) - 1], data)
    name_value_one_col(table, data, range(len(table) - 1, len(table)), 0)
    return data


def risks_2014(report):
    data = {}
    name = 'Риски решения проблемы предложенным способом регулирования'
    table = report.find_table_by_name(name)[0]

    grouped_values_2014(table.loc[[0, 2, 3, 4, 5, 6]], data, 0)
    name_value_one_col(table, data, range(len(table) - 1, len(table)), 0)
    return data


def necessary_measures_2014(report):  # держится на соплях
    data = {}
    name = 'Необходимые для достижения заявленных целей регулирования'
    table = report.find_table_by_name(name)[0]

    grouped_values(table[0:len(table) - 1], data, 0)
    name_value_one_col(table, data, range(len(table) - 1, len(table)), 0)

    return data


def kpi_2014(report):
    data = {}
    table = report.find_table_by_name('Индикативные показатели')[0]

    grouped_values(table[0:len(table) - 3], data, 0)
    name_value_one_col(table, data, range(len(table) - 3, len(table) - 2), 0)
    name_value_two_cols_2014(table, data, range(len(table) - 2, len(table) - 1),
                             len(table.columns) - 1, 1)
    name_value_one_col(table, data, range(len(table) - 1, len(table)), 0)
    return data


def supposed_date_2014(report):
    data = {}
    name = 'Предполагаемая дата вступления в силу проекта акта'
    table = report.find_table_by_name(name)[0]

    name_value_one_col(table, data, range(0, 4), 0)
    name_value_one_col(table, data, range(1, 4), 1)
    return data


def notification_info_2014(report):
    data = {}
    table = report.find_table_by_name('Сведения о размещении уведомления')[0]
    name_value_one_col(table, data, range(1), 0)

    cell = table.loc[1, 0].split(' | ')
    suggestion_acceptance_period_paragraph = \
        remerge_cell(cell[0]).strip('|').strip(' ')
    suggestion_acceptance_period_name = remerge_cell(cell[1])
    name = ' '.join([suggestion_acceptance_period_paragraph,
                     suggestion_acceptance_period_name])
    start = cell[2]
    end = cell[3]
    data[name] = [start, end]

    name_value_one_col(table, data, range(2, len(table)), 0)
    return data


def other_notification_info_2014(report):
    data = {}
    name = 'Иные сведения, которые, по мнению разработчика'
    table = report.find_table_by_name(name)[0]

    name_value_one_col(table, data, range(len(table)), 0)
    return data


def public_discussion_2014(report):
    data = {}
    name = 'Сведения о проведении публичного обсуждения проекта акта'
    table = report.find_table_by_name(name)[0]

    name_value_one_col(table, data, range(1), 0)

    cell = table.loc[1, 0].split(' | ')
    suggestion_acceptance_period_paragraph = \
        remerge_cell(cell[0]).strip('|').strip(' ')
    suggestion_acceptance_period_name = remerge_cell(cell[1])
    name = ' '.join([suggestion_acceptance_period_paragraph,
                     suggestion_acceptance_period_name])
    start = cell[2]
    end = cell[3]
    data[name] = [start, end]

    name_value_one_col(table, data, range(2, len(table)), 0)
    return data


# endregion


# region Olde

def olde_selector(report, num, first=None, last=None, header=True):
    table = list(report.tables())[num].copy()
    if first:
        table = table.copy()[first:]
    if last:
        table = table.copy()[:last]
    table.reset_index(inplace=True, drop=True)
    if header:
        table.drop(0, inplace=True)
        table.reset_index(inplace=True, drop=True)
    return table


def header_olde_selector(report):
    return olde_selector(report, 0, first=None, last=None, header=False)


def general_info_olde_selector(report):
    return olde_selector(report, 1, first=None, last=None, header=True)


def degree_olde_selector(report):
    return olde_selector(report, 2, first=None, last=None, header=True)


def problem_olde_selector(report):
    return olde_selector(report, 3, first=None, last=None, header=True)


def int_exp_olde_selector(report):
    return olde_selector(report, 4, first=None, last=None, header=True)


def goals_olde_selector(report):
    return olde_selector(report, 5, first=None, last=None, header=True)


def description_olde_selector(report):
    return olde_selector(report, 6, first=None, last=4, header=True)


def groups_olde_selector(report):
    return olde_selector(report, 6, first=5, last=None, header=True)


def new_functions_olde_selector(report):
    return olde_selector(report, 7, first=None, last=None, header=True)


def expenses_olde_selector(report):
    return olde_selector(report, 8, first=None, last=None, header=True)


def group_changes_olde_selector(report):
    return olde_selector(report, 9, first=None, last=None, header=True)


def group_expenses_olde_selector(report):
    return olde_selector(report, 10, first=None, last=None, header=True)


def risks_olde_selector(report):
    return olde_selector(report, 11, first=None, last=None, header=True)


def necessary_measures_olde_selector(report):
    return olde_selector(report, 13, first=None, last=None, header=True)


def kpi_olde_selector(report):
    return olde_selector(report, 14, first=None, last=6, header=True)


def supposed_date_olde_selector(report):
    return olde_selector(report, 12, first=None, last=None, header=True)


def notification_info_olde_selector(report):
    return olde_selector(report, 14, first=6, last=None, header=True)


def other_notification_olde_selector(report):
    return olde_selector(report, 15, first=None, last=None, header=True)


def public_discussion_olde_selector(report):
    return olde_selector(report, 16, first=None, last=None, header=True)


def header_olde(report):
    data = {}
    table = header_olde_selector(report)
    # надо вводить internal_id, который будет совпадать с номером отчета
    data['id'] = 'xxx'
    date_cell = table.loc[0][1].split(' | ')
    start = date_olde_to_2016(date_cell[1])
    end = date_olde_to_2016(date_cell[2])
    data['start'] = '.'.join(start)
    data['end'] = '.'.join(end)
    return data


def general_info_olde(report):
    data = {}
    table = general_info_olde_selector(report)
    name_value_one_col(table, data, range(0, len(table) - 5), 0)

    dev_par_name = remerge_cell(table.loc[7, 0])
    dev_value = ' '.join(table.loc[8:, 0].apply(drop_punct).to_list())
    data[dev_par_name] = dev_value

    return data


def degree_olde(report):
    data = {}
    table = degree_olde_selector(report)
    name_value_two_cols_2014(table, data, range(1), 1)
    name_value_one_col(table, data, range(1, 2), 0)
    return data


def problem_olde(report):
    data = {}
    table = problem_olde_selector(report)
    name_value_one_col(table, data, range(6), 0)
    return data


def int_exp_olde(report):
    data = {}
    table = int_exp_olde_selector(report)
    name_value_one_col(table, data, range(2), 0)
    return data


def goals_olde(report):
    data = {}
    table = goals_olde_selector(report)
    ground_index = row_index_by_text_2014(table, '.3.')
    name_value_block_2014(table, data, 1, range(2, ground_index), 0)
    name_value_block_2014(table, data, 1, range(2, ground_index), 1)
    name_value_one_col(table, data, range(ground_index, len(table)), 0)
    return data


def description_olde(report):
    data = {}
    table = description_olde_selector(report)
    name_value_one_col(table, data, range(len(table)), 0)
    return data


def groups_olde(report):
    data = {}
    table = groups_olde_selector(report)
    name_value_block_2014(table, data, 0, range(1, len(table) - 1), 0)
    name_value_block_2014(table, data, 0, range(1, len(table) - 1), 1)
    name_value_one_col(table, data, range(len(table) - 1, len(table)), 0)
    return data


def new_functions_olde(report):
    data = {}
    table = new_functions_olde_selector(report)

    name_functions = remerge_cell(table.loc[0, 0])
    name_procedure = remerge_cell(table.loc[0, 1])
    name_expenses = remerge_cell(table.loc[0, 2])
    name_function_desc = '8.1 Наименование органа'

    functions = []
    i = 1
    while i < len(table):
        office_pattern = table.loc[i, 0]
        if 'Наименование органа' not in office_pattern:
            break
        else:
            function_desc = table.loc[i, 1]
            j = i + 1
            while j < len(table):
                office = table.loc[j, 0]
                if 'Наименование органа' in office:
                    break
                else:
                    procedure = table.loc[j, 1]
                    expenses = table.loc[j, 2]
                    office_tuple = (office, procedure, expenses)
                    functions.append((function_desc, office_tuple))
                    j = j + 1
        i = j

    data[name_functions] = []
    data[name_procedure] = []
    data[name_expenses] = []
    data[name_function_desc] = []

    for function_desc, offices in functions:
        if not len(''.join(offices)) == 0:
            office, procedure, expenses = offices
            data[name_functions].append(office)
            data[name_procedure].append(procedure)
            data[name_expenses].append(expenses)
            data[name_function_desc].append(function_desc)
    return data


def expenses_olde(report):  # функция актуальна только для отчета 29463.html
    data = {}
    table = expenses_olde_selector(report)
    data['.2 Наименование органа'] = \
        ['non-applicable'] * (len(table) - 1)
    data['.3 Единовременные расходы в год возникновения'] = \
        ['non-applicable'] * (len(table) - 1)
    data['.4 Возможные поступления за период'] = \
        ['non-applicable'] * (len(table) - 1)
    grouped_values(table.loc[:, [0, 2]], data, 0)
    return data


def group_changes_olde(report):
    data = {}
    table = group_changes_olde_selector(report)
    grouped_values(table, data, 0)
    return data


def group_expenses_olde(report):
    data = {}
    table = group_expenses_olde_selector(report)
    grouped_values(table[0:len(table) - 1], data, 0)
    name_value_one_col(table, data, range(len(table) - 1, len(table)), 0)
    return data


def risks_olde(report):
    data = {}
    table = risks_olde_selector(report)
    grouped_values(table[0:len(table) - 1], data, 0)
    name_value_one_col(table, data, range(len(table) - 1, len(table)), 0)
    return data


def necessary_measures_olde(report):  # держится на соплях
    data = {}
    table = necessary_measures_olde_selector(report)
    grouped_values(table[0:len(table) - 1], data, 0)
    name_value_one_col(table, data, range(len(table) - 1, len(table)), 0)
    return data


def kpi_olde(report):
    data = {}
    table = kpi_olde_selector(report)
    grouped_values(table[0:2], data, 0)
    name_value_one_col(table, data, range(2, len(table)), 0)
    return data


def supposed_date_olde(report):
    data = {}
    table = supposed_date_olde_selector(report)
    name_value_one_col(table, data, range(0, 1), 0)
    name_value_two_cols_2014(table, data, range(1, 3), 1)
    name_value_two_cols_2014(table, data, range(1, 3), 3, 2)
    name_value_one_col(table, data, range(3, 4), 0)
    return data


def notification_info_olde(report):
    data = {}
    table = notification_info_olde_selector(report)
    table.reset_index(inplace=True, drop=True)
    name_value_one_col(table, data, range(len(table)), 0)
    return data


def other_notification_olde(report):
    data = {}
    table = other_notification_olde_selector(report)
    name_value_one_col(table, data, range(len(table)), 0)
    return data


def public_discussion_olde(report):
    data = {}
    table = public_discussion_olde_selector(report)
    name_value_one_col(table, data, range(len(table)), 0)
    return data

# endregion
