import pandas as pd
import re
from schemas import schemas, parse_by_schema


def format_columns(name, prefix=''):
    new_name = re.sub('^[\.\d]*', '', name).strip()
    if new_name == 'Источники данных' and prefix == 'business':
        if '1.2' in name:
            new_name = new_name + ' (оценка структуры)'
        else:
            new_name = new_name + ' (оценка влияния)'
    if prefix:
        new_name = prefix + ': ' + new_name
    return new_name

def scalar_values_keys(dict_):
    return [key for key in dict_.keys() if not value_is_a_list(dict_, key)]

def list_values_keys(dict_):
    return [key for key in dict_.keys() if value_is_a_list(dict_, key)]

def value_is_a_list(dict_, key):
    return type(dict_[key]) == list

def add_otm_data(data, df, section_name):
    relevant_data = data[section_name]
    keys = list_values_keys(relevant_data)
    for values in zip(*[relevant_data[key] for key in keys]):
        row = [data['header']['regulation_project_id']] + list(values)
        df.loc[-1] = row
        df.reset_index(drop=True, inplace=True)
        
def get_business_data(data, structure_df, expenses_df, prognosis_df):
    relevant_data = data['business']
    keys = list_values_keys(relevant_data)
    formatted_keys = [format_columns(k) for k in keys]
    name_pairs = list(zip(keys, formatted_keys))
    # Структура
    structure_keys = ['Оценка структуры регулируемых субъектов по категориям',
                     'Количественная (интервальная) оценка',
                     'Удельный вес(%)']
    if structure_df.empty:
        structure_df = pd.DataFrame(columns = ['regulation_project_id'] + structure_keys)
        
    for values in zip(*[relevant_data[key[0]] for key in name_pairs if key[1] in structure_keys]):
        row = [data['header']['regulation_project_id']] + list(values)
        structure_df.loc[-1] = row
        structure_df.reset_index(drop=True, inplace=True)  
                        
    # Издержки
    expenses_keys = [k for k in formatted_keys if ':' in k]
    if expenses_df.empty:
        expenses_df = pd.DataFrame(columns = ['regulation_project_id'] + expenses_keys)
    for values in zip(*[relevant_data[key[0]] for key in name_pairs if key[1] in expenses_keys]):
        row = [data['header']['regulation_project_id']] + list(values)
        expenses_df.loc[-1] = row
        expenses_df.reset_index(drop=True, inplace=True)    

    # Прогноз
    prognosis_keys = [
        'Прогноз количественной динамики структуры регулируемых субъектов по категориям при введении предлагаемого регулирования',
        'Микропредприятия',
        'Малыепредприятия',
        'Средниепредприятия']
    if prognosis_df.empty:
        prognosis_df = pd.DataFrame(columns = ['regulation_project_id'] + prognosis_keys)
    for values in zip(*[relevant_data[key[0]] for key in name_pairs if key[1] in prognosis_keys]):
        row = [data['header']['regulation_project_id']] + list(values)
        prognosis_df.loc[-1] = row
        prognosis_df.reset_index(drop=True, inplace=True)
        
    return structure_df, expenses_df, prognosis_df

def validate_names(data_names, df_cols):
    d_set = set(data_names)
    df_set = set(df_cols)
    if len(d_set - df_set) != 0:
        if d_set - df_set != set(['header: regulation_project_id']):
            return False
    return True


def add_report_to_df(project_id, report, main_df, otm_tables, bad_reports):
    try:
        data = None
        for schema_name in schemas.keys():
            data = parse_by_schema(project_id, report, schema_name)
            if data:
                break
        if not data:
            bad_reports.append((project_id, report))
        else:
            for section_name, df in otm_tables.items():
                if section_name == 'business':
                    continue
                if section_name in data:
                    add_otm_data(data, df, section_name)
                    
            row_dict = {'regulation_project_id': project_id}
            for section_name in data.keys():
                section = data[section_name]
                keys = scalar_values_keys(section)
                for key in keys:
                    row_dict[format_columns(key, section_name)] = section[key]
            
            
            if 'business' in data:
                business_data = get_business_data(data, *otm_tables['business'])

                summary_filter = filter(lambda c: str(c).startswith('Итого'),
                                        business_data[1].columns)
                summary = pd.DataFrame(business_data[1][summary_filter])
                for i, values in summary.iterrows():
                    for _ in values.index[1:]:
                        key = ' '.join(['business:', _, values[0].lower()])
                        row_dict[key] = values[_]

                no_summary_filter = filter(lambda c: not str(c).startswith('Итого'),
                                        business_data[1].columns)
                no_summary = pd.DataFrame(business_data[1][no_summary_filter])
                otm_tables['business'] = [business_data[0],
                                        no_summary,
                                        business_data[2]]
            row = pd.Series(row_dict)
            if not validate_names(row_dict.keys(), main_df.columns):
                print(row_dict.keys())
                print(main_df.columns)
                bad_reports.append(project_id)
                raise Exception(f'{project_id}: too many columns in data')
            main_df = main_df.append(row, ignore_index=True)
    except Exception as e:
        print(e)
        bad_reports.append((project_id, report))    
    
    return main_df

def fill_blanks(row):
    high_sections = ['business', 'cancel_duties']
    middle_sections  = ['int_exp', 'expenses', 'kpi', 
                        'new_functions', 'group_changes', 
                        'group_expenses']  + high_sections
    degree = row['impact_degree']

    if degree == 'Средняя':
        for col in list(row.axes[0]):
            for section in high_sections:
                if str(col).startswith(section):
                    if str(row[col]) == 'nan':
                        row[col] = 'non-applicable'
                    break
                    
    if degree == 'Низкая':
        for col in list(row.axes[0]):
            for section in middle_sections:
                if str(col).startswith(section):
                    if str(row[col]) == 'nan':
                        row[col] = 'non-applicable'
                    break
    return row
