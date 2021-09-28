#!/usr/bin/env python3
import argparse
import json
import math
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Queue, Empty

import requests
from bs4 import BeautifulSoup

from utils.db_helper import DBHelper, duma_create_table, generate_set_values_string


class LawsWriter:
    def __init__(self, connection, tasks_queue, waiting_time=10):
        self.connection = connection
        self.tasks_queue = tasks_queue
        self.waiting_time = waiting_time
        self.is_running = True
        self.failed_tasks = []

    def __call__(self):
        while True:
            try:
                law = self.tasks_queue.get(timeout=self.waiting_time)
            except Empty:
                print('Finishing...')
                return
            else:
                try:
                    self.dump(law)
                except Exception as e:
                    # print(e)
                    self.failed_tasks.append(law)
                    print(f"\tLaw {law['number']} task failed")
                self.tasks_queue.task_done()
                # print(f"Law {law['number']} task finished")

    def stop(self):
        self.is_running = False

    def dump(self, law):
        keys_string = ', '.join(law.keys())
        values_string = ', '.join(''.join(['\'', str(x), '\''])
                                  for x in law.values())
        set_string = generate_set_values_string(law)

        statement = 'INSERT INTO duma ({}) ' \
                    'VALUES ({}) ' \
                    'ON CONFLICT (number) ' \
                    'DO UPDATE SET {}' \
                    ';'.format(keys_string, values_string, set_string)
        self.connection.execute_statement(statement)
        # print(f"Updated law number {law.get('number')}")


status_table = {
    1: 'внесен в ГД',
    2: 'находится на рассмотрении в ГД',

    7: 'подписан Президентом РФ',
    8: 'отклонен (снят) ГД',
    9: 'отозванный или возвращенный СПЗИ',
    99: 'рассмотрение завершено по прочим причинам'
    # Пустые:
    # 3: 'входит в примерную программу',
    # 4: 'входит в программы комитетов',
    #
    # То же, что и 2:
    # 5: 'внесен в ГД помимо программ',
    #
    # Категория, включающая в себя все записи со статусами 7, 8, 9 и 99
    # плюс три странных записи: 94800648-1, 96101939-2, 97079221-2:
    # 6: 'рассмотрение завершено',
}


def get_status_by_id(status_id):
    return status_table.get(status_id)


def get_number_of_pages(query, query_parameters):
    params_string = '&'.join(['='.join([str(k), str(v)])
                              for k, v in query_parameters.items()])
    try:
        response = requests.get(query + params_string)
    except Exception as e:
        print(e)
        return 0
    else:
        first_page_laws = json.loads(response.content)
        if first_page_laws['count'] == 0:
            return 0
        return math.ceil(first_page_laws['count']
                         / len(first_page_laws['laws']))


def get_link_to_text(project_id):
    """
    Функция ищет ссылку на текст законопроекта
    """
    url = 'https://sozd.duma.gov.ru/bill/' + project_id
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        registration_stage = soup.find_all('div', {'data-eventnum': '1.1'})
        if registration_stage and len(registration_stage) > 0:
            docs = registration_stage[1]
            docs_links = docs.find_all('a')
            project_texts = [x for x in docs_links
                             if x.text.strip().startswith('Текст внесенного')]
            if project_texts:
                doc_guid = project_texts[0].attrs['id']
                return 'https://sozd.duma.gov.ru/download/' + doc_guid
    except requests.exceptions.RequestException as e:
        print(e)
    return None


def get_project_from_db(number):
    statement = f'select document_link from duma where number=\'{number}\';'
    result = connection.select_statement(statement)
    if result:
        return result[0][0]


def enqueue_law(law_item, in_queue, query_parameters):
    if not get_project_from_db(law_item.get('number')) is None:
        return
    law = {
        'duma_project_id': law_item.get('number'),
        'law_title': law_item.get('name'),
        'introduction_date': law_item.get('introductionDate'),

        'law_type': law_item.get('type').get('name')
        if law_item.get('type') is not None
        else None,

        'duma_solution': law_item.get('lastEvent').get('solution')
        if law_item.get('lastEvent') is not None
        else None,

        'law_status': law_item.get('lastEvent').get('stage').get('name')
        if (law_item.get('lastEvent') is not None
            and law_item.get('lastEvent').get('stage') is not None)
        else None,

        'review_phase': law_item.get('lastEvent').get('phase').get('name')
        if (law_item.get('lastEvent') is not None
            and law_item.get('lastEvent').get('phase') is not None)
        else None
    }
    departments = law_item.get('subject').get('departments')
    if len(departments) > 0:
        law['introduced_by'] = departments[0].get('name')
    law['review_stage'] = get_status_by_id(query_parameters.get('status'))
    law['document_link'] = get_link_to_text(law_item.get('number'))
    in_queue.put(law)


def enqueue_page(in_queue, query, query_parameters, page):
    params_string = '&'.join(['='.join([str(k), str(v)])
                              for k, v in query_parameters.items()])
    try:
        response = requests.get(query + params_string + f'&page={page}')
    except Exception as e:
        print(e)
    else:
        page_laws = json.loads(response.content)
        for law_item in page_laws['laws']:
            enqueue_law(law_item, in_queue, query_parameters)


def enqueue_laws(status_type):
    request_url = f'http://api.duma.gov.ru/api/{KEY}/search.json?' \
                  f'app_token={APP_TOKEN}' \
                  f'&'
    params = {
        'status': status_type,
    }
    pages = get_number_of_pages(request_url, params)
    print(f'Pages: {pages}')
    for page in range(1, pages + 1):
        enqueue_page(queue, request_url, params, page)


def get_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-s', '--status', type=int)
    arg_parser.add_argument('-c', '--connection_path', required=True)
    arg_parser.add_argument('-t', '--token_path', required=True)
    return arg_parser.parse_args()


if __name__ == '__main__':
    args = get_arguments()

    config = json.load(open(f'{args.connection}', 'r'))
    connection = DBHelper(config['database'])
    connection.execute_statement(duma_create_table())

    # Получи здесь http://api.duma.gov.ru/key-request ключ к API и токен
    # для standalone-приложения
    with open(args.token_path, 'r') as fp:
        KEY = fp.readline().strip('\n')
        APP_TOKEN = fp.readline().strip('\n')

    queue = Queue()
    laws_writer = LawsWriter(connection, queue)
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(laws_writer)

    if args.status is None:
        for status in status_table.keys():
            enqueue_laws(status)
    else:
        enqueue_laws(args.status)

    executor.shutdown(wait=True)
    laws_writer.stop()
    queue.join()
    print(laws_writer.failed_tasks)
