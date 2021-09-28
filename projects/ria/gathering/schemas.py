import re

import report_sections_utils
from parsing_helper import date_2014_to_2016


def guess_year(header):
    try:
        matches = re.findall('\d{4}', header.loc[2, 2])
        if len(matches):
            return matches[0]
        else:
            return ''
    except:
        try:
            date_cell = header.loc[0][1].split(' | ')
            end = date_2014_to_2016(date_cell[6], date_cell[7])
            day, month, year = end
            return year
        except:
            return ''


def parse_by_schema(fn, report, schema_name='middle_15', year=None):
    if len(list(report.tables())) == 0:
        return

    header_df = list(report.tables())[0]

    if not year:
        year = guess_year(header_df)

    schema = schemas[schema_name]
    if year not in schema['years']:
        return

    data = {}

    for section_name, section in schema['sections'].items():
        tables = []
        if 'name' in section:
            tables = report.find_table_by_name(section['name'])
        elif 'selector' in section:
            tables = [section['selector'](report)]
        else:
            print(f'no selection basis in section {section_name}')
        schema_table_num = section['table_num']
        if not tables:
            # print(f'report {fn} does not have table {section_name}')
            continue
        elif len(tables) != schema_table_num:
            # print(f'report {fn} year {year} schema {schema_name} '
            #      f'section {section_name} table number mismatch: '
            #      f'{len(tables)} vs {schema_table_num}')
            return
        else:
            dims = section['dim']
            for i, dim in enumerate(dims):
                if len(tables[i].columns) != dim[1]:
                    # print(f'report {fn} year {year} schema {schema_name} '
                    #      f'section {section_name} '
                    #      f'table {i} columns mismatch: '
                    #      f'{len(tables[i].columns)} vs {dim[1]}')
                    return
                elif len(tables[i]) != dim[0] \
                        and not section['allow_more_rows']:
                    # print(f'report {fn} year {year} schema {schema_name} '
                    #      f'section {section_name} '
                    #      f'table {i} rows mismatch: '
                    #      f'{len(tables[i])} vs {dim[0]}')
                    return
                else:
                    try:
                        section_data = section['parser'](report)
                    except Exception as e:
                        print(f'report {fn} year {year} '
                              f'schema {schema_name}: '
                              f'parser error in section {section_name}')
                        print(f'{e}')
                    else:
                        data[section_name] = section_data
    if data:
        data['header']['regulation_project_id'] = fn
    return data


schemas = {
    'high_16': {
        'years': ('2015', '2016', '2017', '2018',
                  '2019', '2020', '2021', '2109', ''),
        'sections': {
            'header': {
                'name': 'ФОРМА',
                'table_num': 1,
                'dim': [(3, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.header,
            },
            'general_info': {
                'name': 'Общая информация',
                'table_num': 1,
                'dim': [(12, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.general_info,
            },
            'degree': {
                'name': 'Степень регулирующего воздействия проекта акта',
                'table_num': 1,
                'dim': [(2, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.degree,
            },
            'problem': {
                'name': 'Описание проблемы',
                'table_num': 1,
                'dim': [(6, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.problem,
            },
            'int_exp': {
                'name': 'Анализ международного опыта',
                'table_num': 1,
                'dim': [(2, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.int_exp,
            },
            'goals': {
                'name': 'Цели предлагаемого регулирования',
                'table_num': 1,
                'dim': [(4, 4)],  # не менее 4
                'allow_more_rows': True,
                'parser': report_sections_utils.goals,
            },
            'description': {
                'name': 'Описание предлагаемого регулирования',
                'table_num': 1,
                'dim': [(4, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.description,
            },
            'groups': {
                'name': 'Основные группы субъектов',
                'table_num': 1,
                'dim': [(6, 4)],  # не менее 3
                'allow_more_rows': True,
                'parser': report_sections_utils.groups,
            },
            'new_functions': {
                'name': 'Новые функции',
                'table_num': 2,
                'dim': [(1, 3), (2, 3)],  # не менее 3
                'allow_more_rows': True,
                'parser': report_sections_utils.new_functions_2016,
            },
            'expenses': {
                'name': 'Оценка соответствующих расходов',
                'table_num': 2,
                'dim': [(1, 3), (7, 5)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.expenses_high_2016,
            },
            'group_changes': {
                'name': 'Новые преимущества',
                'table_num': 2,
                'dim': [(2, 3), (1, 2)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.group_changes_2016,
            },
            'group_expenses': {
                'name': 'Оценка расходов и доходов субъектов',
                'table_num': 2,
                'dim': [(2, 3), (2, 3)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.group_expenses_2016,
            },
            'risks': {
                'name': 'Риски решения проблемы',
                'table_num': 1,
                'dim': [(3, 5)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.risks,
            },
            'business': {
                'name': 'деятельность субъектов '
                        'малого и среднего предпринимательства',
                'table_num': 1,
                'dim': [(28, 7)],
                'allow_more_rows': True,
                'parser': report_sections_utils.business
            },
            'necessary_measures': {
                'name': 'Необходимые для достижения '
                        'заявленных целей регулирования',
                'table_num': 1,
                'dim': [(3, 6)],
                'allow_more_rows': True,
                'parser': report_sections_utils.necessary_measures,
            },
            'kpi': {
                'name': 'Индикативные показатели',
                'table_num': 3,
                'dim': [(1, 4), (1, 2), (3, 3)],
                'allow_more_rows': True,
                'parser': report_sections_utils.kpi_2016,
            },
            'supposed_date': {
                'name': 'Предполагаемая дата вступления в силу проекта акта',
                'table_num': 1,
                'dim': [(8, 5)],
                'allow_more_rows': False,
                'parser': report_sections_utils.supposed_date,
            },
            'notification_info': {
                'name': 'Сведения о размещении уведомления',
                'table_num': 1,
                'dim': [(7, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.notification_info,
            },
            'anticorr_expertise': {
                'name': 'Сведения о проведении '
                        'независимой антикоррупционной экспертизы',
                'table_num': 1,
                'dim': [(2, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.anticorr_expertise,
            },
            'other_notification_info': {
                'name': 'Иные сведения, которые, по мнению разработчика',
                'table_num': 1,
                'dim': [(2, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.other_notification_info,
            },
            'public_discussion': {
                'name': 'Сведения о проведении '
                        'публичного обсуждения проекта акта',
                'table_num': 1,
                'dim': [(8, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.public_discussion,
            },
            'cancel_duties': {
                'name': 'Информация об отмене обязанностей',
                'table_num': 1,
                'dim': [(7, 3)],
                'allow_more_rows': True,
                'parser': report_sections_utils.cancel_duties,
            }
        }
    },
    'middle_16': {
        'years': ('2015', '2016', '2017', '2018',
                  '2019', '2020', '2021', '2109', ''),
        'sections': {
            'header': {
                'name': 'ФОРМА',
                'table_num': 1,
                'dim': [(3, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.header,
            },
            'general_info': {
                'name': 'Общая информация',
                'table_num': 1,
                'dim': [(12, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.general_info,
            },
            'degree': {
                'name': 'Степень регулирующего воздействия проекта акта',
                'table_num': 1,
                'dim': [(2, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.degree,
            },
            'problem': {
                'name': 'Описание проблемы',
                'table_num': 1,
                'dim': [(6, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.problem,
            },
            'int_exp': {
                'name': 'Анализ международного опыта',
                'table_num': 1,
                'dim': [(2, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.int_exp,
            },
            'goals': {
                'name': 'Цели предлагаемого регулирования',
                'table_num': 1,
                'dim': [(4, 4)],  # не менее 4
                'allow_more_rows': True,
                'parser': report_sections_utils.goals,
            },
            'description': {
                'name': 'Описание предлагаемого регулирования',
                'table_num': 1,
                'dim': [(4, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.description,
            },
            'groups': {
                'name': 'Основные группы субъектов',
                'table_num': 1,
                'dim': [(6, 4)],  # не менее 3
                'allow_more_rows': True,
                'parser': report_sections_utils.groups,
            },
            'new_functions': {
                'name': 'Новые функции',
                'table_num': 2,
                'dim': [(1, 3), (2, 3)],  # не менее 3
                'allow_more_rows': True,
                'parser': report_sections_utils.new_functions_2016,
            },
            'expenses': {
                'name': 'Оценка соответствующих расходов',
                'table_num': 3,
                'dim': [(1, 3), (2, 3), (5, 3)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.expenses_2016,
            },
            'group_changes': {
                'name': 'Новые преимущества',
                'table_num': 2,
                'dim': [(2, 3), (1, 2)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.group_changes_2016,
            },
            'group_expenses': {
                'name': 'Оценка расходов и доходов субъектов',
                'table_num': 2,
                'dim': [(2, 3), (2, 3)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.group_expenses_2016,
            },
            'risks': {
                'name': 'Риски решения проблемы',
                'table_num': 1,
                'dim': [(3, 5)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.risks,
            },
            'necessary_measures': {
                'name': 'Необходимые для достижения '
                        'заявленных целей регулирования',
                'table_num': 1,
                'dim': [(3, 6)],
                'allow_more_rows': True,
                'parser': report_sections_utils.necessary_measures,
            },
            'kpi': {
                'name': 'Индикативные показатели',
                'table_num': 3,
                'dim': [(1, 4), (1, 2), (3, 3)],
                'allow_more_rows': True,
                'parser': report_sections_utils.kpi_2016,
            },
            'supposed_date': {
                'name': 'Предполагаемая дата вступления в силу проекта акта',
                'table_num': 1,
                'dim': [(8, 5)],
                'allow_more_rows': False,
                'parser': report_sections_utils.supposed_date,
            },
            'notification_info': {
                'name': 'Сведения о размещении уведомления',
                'table_num': 1,
                'dim': [(7, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.notification_info,
            },
            'anticorr_expertise': {
                'name': 'Сведения о проведении '
                        'независимой антикоррупционной экспертизы',
                'table_num': 1,
                'dim': [(2, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.anticorr_expertise,
            },
            'other_notification_info': {
                'name': 'Иные сведения, которые, по мнению разработчика',
                'table_num': 1,
                'dim': [(2, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.other_notification_info,
            },
            'public_discussion': {
                'name': 'Сведения о проведении '
                        'публичного обсуждения проекта акта',
                'table_num': 1,
                'dim': [(8, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.public_discussion,
            },
            'cancel_duties': {
                'name': 'Информация об отмене обязанностей',
                'table_num': 1,
                'dim': [(7, 3)],
                'allow_more_rows': True,
                'parser': report_sections_utils.cancel_duties,
            }
        }
    },
    'low_16': {
        'years': ('2015', '2016', '2017', '2018',
                  '2019', '2020', '2021', '2109', ''),
        'sections': {
            'header': {
                'name': 'ФОРМА',
                'table_num': 1,
                'dim': [(3, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.header,
            },
            'general_info': {
                'name': 'Общая информация',
                'table_num': 1,
                'dim': [(12, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.general_info,
            },
            'degree': {
                'name': 'Степень регулирующего воздействия проекта акта',
                'table_num': 1,
                'dim': [(2, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.degree,
            },
            'problem': {
                'name': 'Описание проблемы',
                'table_num': 1,
                'dim': [(6, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.problem,
            },
            'int_exp': {
                'name': 'Анализ международного опыта',
                'table_num': 1,
                'dim': [(2, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.int_exp,
            },
            'goals': {
                'name': 'Цели предлагаемого регулирования',
                'table_num': 1,
                'dim': [(4, 4)],  # не менее 4
                'allow_more_rows': True,
                'parser': report_sections_utils.goals,
            },
            'description': {
                'name': 'Описание предлагаемого регулирования',
                'table_num': 1,
                'dim': [(4, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.description,
            },
            'groups': {
                'name': 'Основные группы субъектов',
                'table_num': 1,
                'dim': [(6, 4)],  # не менее 3
                'allow_more_rows': True,
                'parser': report_sections_utils.groups,
            },
            'new_functions': {
                'name': 'Новые функции',
                'table_num': 2,
                'dim': [(1, 3), (2, 3)],  # не менее 3
                'allow_more_rows': True,
                'parser': report_sections_utils.new_functions_2016,
            },
            'expenses': {
                'name': 'Оценка соответствующих расходов',
                'table_num': 3,
                'dim': [(1, 3), (2, 3), (5, 3)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.expenses_2016,
            },
            'group_changes': {
                'name': 'Новые преимущества',
                'table_num': 2,
                'dim': [(2, 3), (1, 2)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.group_changes_2016,
            },
            'group_expenses': {
                'name': 'Оценка расходов и доходов субъектов',
                'table_num': 2,
                'dim': [(2, 3), (2, 3)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.group_expenses_2016,
            },
            'risks': {
                'name': 'Риски решения проблемы',
                'table_num': 1,
                'dim': [(3, 3)],  # может быть меньше
                'allow_more_rows': True,
                'parser': report_sections_utils.risks_low,
            },
            'necessary_measures': {
                'name': 'Необходимые для достижения '
                        'заявленных целей регулирования',
                'table_num': 1,
                'dim': [(3, 6)],
                'allow_more_rows': True,
                'parser': report_sections_utils.necessary_measures,
            },
            'kpi': {
                'name': 'Индикативные показатели',
                'table_num': 3,
                'dim': [(1, 4), (1, 2), (3, 3)],
                'allow_more_rows': True,
                'parser': report_sections_utils.kpi_2016,
            },
            'supposed_date': {
                'name': 'Предполагаемая дата вступления в силу проекта акта',
                'table_num': 1,
                'dim': [(8, 5)],
                'allow_more_rows': False,
                'parser': report_sections_utils.supposed_date,
            },
            'notification_info': {
                'name': 'Сведения о размещении уведомления',
                'table_num': 1,
                'dim': [(7, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.notification_info,
            },
            'anticorr_expertise': {
                'name': 'Сведения о проведении '
                        'независимой антикоррупционной экспертизы',
                'table_num': 1,
                'dim': [(2, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.anticorr_expertise,
            },
            'other_notification_info': {
                'name': 'Иные сведения, которые, по мнению разработчика',
                'table_num': 1,
                'dim': [(2, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.other_notification_info,
            },
            'public_discussion': {
                'name': 'Сведения о проведении '
                        'публичного обсуждения проекта акта',
                'table_num': 1,
                'dim': [(8, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.public_discussion,
            },
            'cancel_duties': {
                'name': 'Информация об отмене обязанностей',
                'table_num': 1,
                'dim': [(7, 3)],
                'allow_more_rows': True,
                'parser': report_sections_utils.cancel_duties,
            }
        }
    },
    'middle_15': {
        'years': ('2015', '2016'),
        'sections': {
            'header': {
                'name': 'ФОРМА',
                'table_num': 1,
                'dim': [(3, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.header,
            },
            'general_info': {
                'name': 'Общая информация',
                'table_num': 1,
                'dim': [(12, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.general_info,
            },
            'degree': {
                'name': 'Степень регулирующего воздействия проекта акта',
                'table_num': 1,
                'dim': [(2, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.degree,
            },
            'problem': {
                'name': 'Описание проблемы',
                'table_num': 1,
                'dim': [(6, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.problem,
            },
            'int_exp': {
                'name': 'Анализ международного опыта',
                'table_num': 1,
                'dim': [(2, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.int_exp,
            },
            'goals': {
                'name': 'Цели предлагаемого регулирования',
                'table_num': 1,
                'dim': [(8, 4)],  # не менее 4
                'allow_more_rows': False,
                'parser': report_sections_utils.goals,
            },
            'description': {
                'name': 'Описание предлагаемого регулирования',
                'table_num': 1,
                'dim': [(4, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.description,
            },
            'groups': {
                'name': 'Основные группы субъектов',
                'table_num': 1,
                'dim': [(14, 4)],  # не менее 3
                'allow_more_rows': False,
                'parser': report_sections_utils.groups,
            },
            'new_functions': {
                'name': 'Новые функции',
                'table_num': 1,
                'dim': [(31, 3)],  # не менее 3
                'allow_more_rows': False,
                'parser': report_sections_utils.new_functions,
            },
            'expenses': {
                'name': 'Оценка соответствующих расходов',
                'table_num': 1,
                'dim': [(86, 5)],  # может быть меньше
                'allow_more_rows': False,
                'parser': report_sections_utils.expenses,
            },
            'group_changes': {
                'name': 'Новые преимущества',
                'table_num': 1,
                'dim': [(27, 3)],  # может быть меньше
                'allow_more_rows': False,
                'parser': report_sections_utils.group_changes,
            },
            'group_expenses': {
                'name': 'Оценка расходов и доходов субъектов',
                'table_num': 1,
                'dim': [(27, 3)],  # может быть меньше
                'allow_more_rows': False,
                'parser': report_sections_utils.group_expenses,
            },
            'risks': {
                'name': 'Риски решения проблемы',
                'table_num': 1,
                'dim': [(7, 5)],  # может быть меньше
                'allow_more_rows': False,
                'parser': report_sections_utils.risks,
            },
            'necessary_measures': {
                'name': 'Необходимые для достижения '
                        'заявленных целей регулирования',
                'table_num': 1,
                'dim': [(7, 6)],
                'allow_more_rows': False,
                'parser': report_sections_utils.necessary_measures,
            },
            'kpi': {
                'name': 'Индикативные показатели',
                'table_num': 1,
                'dim': [(29, 6)],
                'allow_more_rows': False,
                'parser': report_sections_utils.kpi,
            },
            'supposed_date': {
                'name': 'Предполагаемая дата вступления в силу проекта акта',
                'table_num': 1,
                'dim': [(8, 5)],
                'allow_more_rows': False,
                'parser': report_sections_utils.supposed_date,
            },
            'notification_info': {
                'name': 'Сведения о размещении уведомления',
                'table_num': 1,
                'dim': [(7, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.notification_info,
            },
            'anticorr_expertise': {
                'name': 'Сведения о проведении '
                        'независимой антикоррупционной экспертизы',
                'table_num': 1,
                'dim': [(2, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.anticorr_expertise,
            },
            'other_notification_info': {
                'name': 'Иные сведения, которые, по мнению разработчика',
                'table_num': 1,
                'dim': [(2, 2)],
                'allow_more_rows': False,
                'parser': report_sections_utils.other_notification_info,
            },
            'public_discussion': {
                'name': 'Сведения о проведении '
                        'публичного обсуждения проекта акта',
                'table_num': 1,
                'dim': [(8, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.public_discussion,
            },
            'cancel_duties': {
                'name': 'Информация об отмене обязанностей',
                'table_num': 1,
                'dim': [(7, 3)],
                'allow_more_rows': False,
                'parser': report_sections_utils.cancel_duties,
            }
        }
    }
}
