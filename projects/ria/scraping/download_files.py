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

import urllib3

relative_lib_paths = [
                      'utils/',
                     ]

absolute_lib_paths = [os.path.abspath(x) for x in relative_lib_paths]
for path in absolute_lib_paths:
    sys.path.insert(0, path)

from db_helper import DBHelper


class Document:
    def __init__(self, _id=None, url=None, document_type=None,
                 report_data=None, version=None, restart_count=0):
        self.id = _id
        self.url = url
        self.document_type = document_type
        self.data = report_data
        self.version = version
        self.restart_count = restart_count
        if _id is None:
            # TODO: изменить version на document_type
            try:
                self.id = str(report_data['internal_id'])
                report_info = report_data['ria_report_urls'][version][0]
                if len(report_info) == 2:
                    self.url = report_info[1]
            except Exception as e:
                print(e)

    def check(self):
        if self.url and self.id:
            return True

    def __str__(self):
        return f'Document, version: {self.document_type}, ' \
               f'id: {self.id}, url: {self.url}'


class Downloader:
    def __init__(self,
                 tasks_queue,
                 directory,
                 parent_directory,
                 waiting_time=2,
                 max_restart_count=4,
                 ):
        self.is_running = True
        self.tasks_queue = tasks_queue
        self.directory = directory
        self.failed_tasks = []
        self.parent_directory = self.make_dir(parent_directory)
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
                    print(f'downloading {task.url}')
                    self.save_file(task)
                except Exception as e:
                    print(e)
                    self.fail_task(task)
                self.tasks_queue.task_done()
                print('task done')
                time.sleep(1)

    def stop(self):
        self.is_running = False

    def make_dir(self, _dir):
        if not os.path.isdir(_dir):
            os.mkdir(_dir)
        dirname = os.path.join(_dir, self.directory)
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        return dirname

    def save_file(self, task):
        response = self.http.request('GET', task.url, preload_content=False)
        try:
            if re.search('fileid=(.*)', task.url) \
                    or re.search('sozd.duma.gov.ru/download/*', task.url):
                ext = response.getheader('Content-Disposition') \
                    .split('.')[-1].strip('"')
                path = os.path.join(self.parent_directory, f'{task.id}.{ext}')
                with open(path, 'wb') as f:
                    shutil.copyfileobj(response, f)
            else:
                ext = 'html'
                path = os.path.join(self.parent_directory, f'{task.id}.{ext}')
                with open(path, 'wb') as f:
                    f.write(response.data)
                    f.flush()

            if task.document_type not in ['current', 'updated',
                                          'published', 'sozd']:
                try:
                    self.write_to_db({
                        'id': task.id,
                        'path': f'{self.directory}/{task.id}.{ext}',
                        'type': task.document_type
                    })
                except Exception as e:
                    print(e)
                    print(f'Не удалось записать {task.id} в базу.')

        except Exception as e:
            print(e)
            print(f'Не получилось скачать {task.id}')
        else:
            response.release_conn()

    @staticmethod
    def write_to_db(task):
        task_id = task['id']
        task_path = task['path']
        task_type = task['type']
        statement = 'UPDATE document ' \
                    'SET path=\'{}\' ' \
                    'WHERE ' \
                    'project_id={} ' \
                    'AND type=\'{}\'' \
                    ';'.format(task_path, task_id, task_type)
        connection.execute_statement(statement)

    def fail_task(self, task):
        if task.restart_count >= self.max_restart_count:
            self.failed_tasks.append(task.id)
        else:
            new_task = deepcopy(task)
            new_task.restart_count += 1
            self.tasks_queue.put(new_task)


def make_queue(input_type, document_type=None, impact_degree=None):
    queue = Queue()
    failed_tasks = []

    result = select_from_database(input_type, document_type, impact_degree)
    for _ in result:
        if input_type in ['published', 'sozd']:
            task = Document(_id=_[0], url=_[1], document_type=input_type)
        elif input_type == 'current':
            task = Document(_id=_[0], url=_[1], document_type=input_type)
        elif input_type == 'updated':
            url = list(filter(lambda x: str(x).startswith('https'), _))[0]
            task = Document(_id=_[0], url=url, document_type=input_type)
        else:
            url = _[1] if _[1] is not None else _[2]
            task = Document(_id=_[0], url=url, document_type=_[3])
        if task.check():
            queue.put(task)
        else:
            print(f'Не получилось сделать task c документом '
                  f'{document_type} для {task.id}')
            failed_tasks.append(task.id)
    return queue, failed_tasks


def select_from_database(input_type, document_type, impact_degree):
    if input_type == 'published':
        statement = 'SELECT internal_id, published_law_link ' \
                    'FROM project ' \
                    'WHERE NOT published_law_link IS NULL;'
    elif input_type == 'sozd':
        statement = 'SELECT number, document_link ' \
                    'FROM duma ' \
                    'WHERE NOT document_link IS NULL;'
    elif input_type == 'current':
        statement = 'SELECT id, current ' \
                    'FROM orv_reports.documents_links ' \
                    'WHERE current IS NOT NULL;'
    elif input_type == 'updated':
        statement = 'SELECT id, upd_0, upd_1, upd_2 ' \
                    'FROM orv_reports.documents_links ' \
                    'WHERE upd_0 IS NOT NULL ' \
                    'OR upd_1 IS NOT NULL ' \
                    'OR upd_2 IS NOT NULL;'
    elif input_type == 'internal':
        impact_degree_clause = 'impact_degree IS NULL' \
            if impact_degree is None \
            else f'impact_degree=\'{impact_degree}\''

        statement = 'SELECT project_id, preview_link, storage_link, type ' \
                    'FROM document ' \
                    'WHERE ' \
                    'type=\'{}\' ' \
                    'AND path IS NULL ' \
                    'AND project_id IN (' \
                    'SELECT internal_id FROM project WHERE {})' \
                    ';'.format(document_type, impact_degree_clause)
    else:
        print('Уточните тип документа.')
        sys.exit()
    return connection.select_statement(statement)


def get_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', '--config', required=True)
    arg_parser.add_argument('-i', '--input', default='internal',
                            choices=['internal', 'current', 'updated',
                                     'published', 'sozd'])
    arg_parser.add_argument('-d', '--directory', default='./downloads')
    arg_parser.add_argument('-w', '--workers', default=1, type=int)
    arg_parser.add_argument('-impact', '--impact')
    arg_parser.add_argument('-type', '--type')
    return arg_parser.parse_args()


if __name__ == '__main__':
    args = get_arguments()

    config = json.load(
        open(args.config, 'r'))
    
    connection = DBHelper(config['database'])
    connection.setup()

    input_type = args.input
    download_directory = config['working_directory'] + \
        '/scraping/downloads'
    workers = args.workers
    degree = args.impact
    doc_type = args.type

    tasks, failed = make_queue(input_type, doc_type, degree)
    directory_name = f'{doc_type}_{degree}' \
        if input_type not in ['current', 'updated', 'published', 'sozd'] \
        else input_type
    downloader = Downloader(tasks,
                            directory=directory_name,
                            parent_directory=download_directory)
    download_executor = ThreadPoolExecutor(max_workers=workers)
    for _ in range(workers):
        download_executor.submit(downloader)
    download_executor.shutdown(wait=True)

    print('executors finished')
    tasks.join()
    print('no tasks left')

    failed += downloader.failed_tasks
    print(failed)
