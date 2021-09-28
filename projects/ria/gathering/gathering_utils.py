#!/usr/bin/env python3

def is_number(text):
    return re.search('^\d+$', text)

def docs_table_to_df(table):
    table_list = []
    for row in table.rows:
        # нужно проверить, что строчка – не разделитель между секциями! 
        table_list.append([text_process(cell.text) for cell in row.cells])  
    if not table_list[0][0]:
        table_list[0][0] = 'X'  # сюда нужно добавить угадывание смысла ключа
    df = pd.DataFrame(table_list)

    header = df.iloc[0]
    df = df[1:]
    df.columns = header
    
    return df


def url_by_project_id(project_id):
    '''
    По id проекта выдаем ссылку на карточку проекта на сайте regulation.gov.ru
    02/08/09-19/00094879 –> https://regulation.gov.ru/projects#npa=94879
    '''
    code = code_by_project_id(project_id)
    if is_number(code):
        return 'https://regulation.gov.ru/projects#npa=' + code

def code_by_project_id(project_id):
    code = str(project_id).split('/')[-1]
    code = code.lstrip('0')
    return code

if __name__ == '__main__':
    assert url_by_project_id('02/08/09-19/00094879') == 'https://regulation.gov.ru/projects#npa=94879'
    assert url_by_project_id('НПА') is None
    print("All tests passed")
