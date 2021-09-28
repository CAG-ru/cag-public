#!/usr/bin/env python3

import argparse
import os
import re
import shutil
import sys
import time
import json
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from queue import Queue, Empty

import numpy as np
import psycopg2
import urllib3

relative_lib_paths = [
    'utils/',
]

absolute_lib_paths = [os.path.abspath(x) for x in relative_lib_paths]
for path in absolute_lib_paths:
    sys.path.insert(0, path)

from db_helper import DBHelper


class Document:
    def __init__(self, guid=None, project_id=None, document_type=None, url=None,
                 impact_degree=None, restart_count=0):
        self.guid = guid
        self.project_id = project_id
        self.document_type = document_type
        self.impact_degree = impact_degree
        self.url = url
        self.restart_count = restart_count

    def check(self):
        if self.url:
            return True

    def __str__(self):
        return f'Document type: {self.document_type}, ' \
               f'id: {self.guid}, url: {self.url}'


class Downloader:
    def __init__(self,
                 tasks_queue,
                 parent_directory,
                 waiting_time=2,
                 max_restart_count=4,
                 ):
        self.is_running = True
        self.tasks_queue = tasks_queue
        self.failed_tasks = []
        self.parent_directory = parent_directory
        self.waiting_time = waiting_time
        self.max_restart_count = max_restart_count
        self.http = urllib3.PoolManager(timeout=10, cert_reqs='CERT_NONE')

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def __call__(self):
        while True:
            try:
                task = self.tasks_queue.get(timeout=self.waiting_time)
            except Empty:
                print('No tasks left for this worker')
                return
            else:
                try:
                    print(f'Downloading {task.url}')
                    self.save_file(task)
                except Exception as e:
                    print(e)
                    self.fail_task(task)
                self.tasks_queue.task_done()
                print('Task done')
                time.sleep(1)

    def stop(self):
        self.is_running = False

    def save_file(self, task):
        try:
            response = self.http.request('GET', task.url, preload_content=False)
        except urllib3.exceptions.ResponseError as e:
            print(e)
        else:
            if task.document_type in ['decision', 'discussion',
                                      'main_ria_report', 'updated_ria_report',
                                      'previous_ria_report']:
                directory = f'{self.parent_directory}/' \
                            f'{task.document_type}_{task.impact_degree}'
            elif task.document_type in ['current_npa', 'updated_npa',
                                        'published_law_link']:
                type_name = task.document_type.split('_')[0]
                directory = f'{self.parent_directory}/npa/{type_name}'
            else:
                directory = f'{self.parent_directory}/duma'

            try:
                if re.search('fileid=(.*)', task.url) \
                        or re.search('sozd.duma.gov.ru/download/*', task.url):
                    ext = response.getheader('Content-Disposition') \
                        .split('.')[-1].strip('"')
                    path = os.path.join(directory, f'{task.project_id}.{ext}')
                    with open(path, 'wb') as f:
                        shutil.copyfileobj(response, f)
                else:
                    ext = 'html'
                    path = os.path.join(directory, f'{task.project_id}.{ext}')
                    with open(path, 'wb') as f:
                        f.write(response.data)
                        f.flush()
                if task.document_type == 'duma':
                    try:
                        self.write_to_duma({
                            'project_id': '1192824-7',
                            'path': path
                        })
                    except psycopg2.DatabaseError as e:
                        print(e)
                        print(f'Не удалось записать {task.id} в базу.')
                else:
                    try:
                        self.write_to_document({
                            'guid': task.guid,
                            'path': path
                        })
                    except psycopg2.DatabaseError as e:
                        print(e)
                        print(f'Не удалось записать {task.id} в базу.')
            except Exception as e:
                print(e)
                print(f'Не получилось скачать {task.guid}')
            else:
                response.release_conn()

    @staticmethod
    def write_to_document(task):
        guid = task['guid']
        path = task['path']
        statement = 'UPDATE document ' \
                    'SET path=\'{}\' ' \
                    'WHERE ' \
                    'guid=\'{}\'' \
                    ';'.format(path, guid)
        connection.execute_statement(statement)

    @staticmethod
    def write_to_duma(task):
        project_id = task['project_id']
        path = task['path']
        statement = 'UPDATE duma ' \
                    'SET path=\'{}\' ' \
                    'WHERE ' \
                    'duma_project_id=\'{}\'' \
                    ';'.format(path, project_id)
        connection.execute_statement(statement)

    def fail_task(self, task):
        if task.restart_count >= self.max_restart_count:
            self.failed_tasks.append(task.id)
        else:
            new_task = deepcopy(task)
            new_task.restart_count += 1
            self.tasks_queue.put(new_task)


def make_queue(input_db, document_type=None):
    queue = Queue()
    failed_tasks = []

    result = select_from_database(input_db)
    for _ in result:
        if input_db == 'duma':
            task = Document(guid=None, project_id=_[0],
                            url=_[1], document_type=input_db)
        else:
            task = Document(guid=_[0], project_id=_[1],
                            document_type=_[2], url=_[3], impact_degree=_[4])
        if task.check():
            queue.put(task)
        else:
            print(f'Не получилось сделать task c документом '
                  f'{document_type} для {task.guid}')
            failed_tasks.append(task.guid)
    return queue, failed_tasks


def select_from_database(input_type):
    if input_type == 'duma':
        statement = 'SELECT duma_project_id, document_link ' \
                    'FROM duma ' \
                    'WHERE NOT document_link IS NULL;'
    else:
        statement = 'SELECT guid, document.regulation_project_id, ' \
                    'document_type, link, regulatory_impact ' \
                    'FROM document ' \
                    'INNER JOIN project ' \
                    'ON document.regulation_project_id=project.regulation_project_id;' \

    return connection.select_statement(statement)


def get_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', '--config', required=True)
    arg_parser.add_argument('-i', '--input', required=True,
                            choices=['duma', 'orv'])
    arg_parser.add_argument('-w', '--workers', default=1, type=int)
    return arg_parser.parse_args()


def create_directories():
    for d in [download_directory, f'{download_directory}/duma',
              f'{download_directory}/npa/current',
              f'{download_directory}/npa/updated',
              f'{download_directory}/npa/published']:
        os.makedirs(d, exist_ok=True)
    for t, i in np.array(np.meshgrid(
            ['decision', 'discussion', 'main_ria_report',
             'previous_ria_report', 'updated_ria_report'],
            ['Высокая', 'Средняя', 'Низкая', 'None', 'Не_определена'])) \
            .T.reshape(-1, 2):
        os.makedirs(f'{download_directory}/{t}_{i}', exist_ok=True)


if __name__ == '__main__':
    args = get_arguments()

    config = json.load(open(args.config, 'r'))

    connection = DBHelper(config['database'])
    connection.setup()

    input_db = args.input
    download_directory = config['working_directory'] + '/scraping'
    workers = args.workers

    create_directories()

    tasks, failed = make_queue(input_db)
    downloader = Downloader(tasks, parent_directory=download_directory)
    download_executor = ThreadPoolExecutor(max_workers=workers)
    for _ in range(workers):
        download_executor.submit(downloader)
    download_executor.shutdown(wait=True)

    print('executors finished')
    tasks.join()
    print('no tasks left')

    failed += downloader.failed_tasks
    print(failed)
