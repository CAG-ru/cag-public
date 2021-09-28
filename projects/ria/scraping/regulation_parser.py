#!/usr/bin/env python3

import argparse
import datetime
import json
import pathlib
import re
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from xml.etree import ElementTree

import flatdict
import psycopg2
import requests
from bs4 import BeautifulSoup


relative_lib_paths = [
                      'utils/',
                     ]

absolute_lib_paths = [os.path.abspath(x) for x in relative_lib_paths]
for path in absolute_lib_paths:
    sys.path.insert(0, path)

from db_helper import DBHelper, generate_set_values_string


class ProjectScraper:
    def __init__(self, task_queue, results_queue):
        self.task_queue = task_queue
        self.results_queue = results_queue
        self.doc_names = {
            'Текст проекта': 'current_npa',
            'Текст проекта нормативного правового акта': 'current_npa',
            'Текущая версия текста проекта нормативного правового акта': 'current_npa',

            'Доработанный  текст проекта нормативного правового акта': 'updated_npa',
            'Доработанный по итогам обсуждений текст проекта акта': 'updated_npa',
            'Доработанный по итогам обсуждений текст проекта нормативного правового акта': 'updated_npa',
            'Доработанный по итогам обсуждений текст проекта нормативно правового акта': 'updated_npa',

            'Сводный отчет в отношении нормативного правового акта': 'main_ria_report',
            'Сводный отчет по проекту нормативного правового акта': 'main_ria_report',
            'Предыдущие версии сводных отчетов в отношении нормативного правового акта': 'previous_ria_report',
            'Доработанный по итогам обсуждений сводный отчёт': 'updated_ria_report',

            'Заключение об оценке регулирующего воздействия': 'decision',

            'Сводка предложений': 'discussion',

            'Принятый акт': 'published_law_link',
            'Принятый документ': 'published_law_link'
        }

    def __call__(self):
        while True:
            try:
                project = self.task_queue.get(timeout=5)
            except Empty:
                print('Scraper finished.')
                return
            else:
                jobs = [
                    self.add_npalist_info,
                    self.add_likes,
                    self.add_documents,
                ]
                for job in jobs:
                    try:
                        job(project)
                    except requests.RequestException as e:
                        print(project['regulation_project_id'], e)
                        break
                if self.has_all(project):
                    self.results_queue.put(project)
                else:
                    self.task_queue.put(project)
                self.task_queue.task_done()

    def has_all(self, project):
        return self.has_npalist_info(project) \
               and self.has_likes(project) \
               and self.has_documents(project)

    @staticmethod
    def has_npalist_info(project):
        additional_keys = [
            'development_stage',
            'project_status',
            'regulatory_impact',
            'mineco_solution',
            'problem_addressed',
            'act_objectives',
            'persons_affected_by_act',
            'relations_regulated_by_act',
            'act_significance',
            'estimated_effective_date',
            'estimated_transition_period',
            'departamental_number_if_passed',
            'passing_date_if_passed',
            'registration_number_if_passed'
        ]
        return all(x in project.keys() for x in additional_keys)

    @staticmethod
    def has_likes(project):
        return all(x in project.keys() for x in ['likes_num', 'dislikes_num'])

    @staticmethod
    def has_documents(project):
        return 'documents' in project.keys()

    @staticmethod
    def add_npalist_info(project):
        url = f'https://regulation.gov.ru/api/npalist?' \
              f'id={project["regulation_project_id"]}'
        response = requests.get(url)

        api_info = ElementTree.fromstring(str(response.text))[0]
        project_info = {x.tag: x.text for x in api_info}
        project.update({
            'development_stage': project_info.get('stage'),
            'project_status': project_info.get('status'),
            'regulatory_impact': project_info.get('regulatoryImpact'),
            'mineco_solution': project_info.get('procedureResult'),
            'problem_addressed': project_info.get('problem'),
            'act_objectives': project_info.get('objectives'),
            'persons_affected_by_act': project_info.get('circlePersons'),
            'relations_regulated_by_act': project_info.get('socialRelations'),
            'act_significance': project_info.get('rationale'),
            'estimated_effective_date': project_info.get('planDate'),
            'estimated_transition_period': project_info.get('transitionPeriod'),
            'departamental_number_if_passed': project_info.get('compliteNumberDepAct'),
            'passing_date_if_passed': project_info.get('compliteDateAct'),
            'registration_number_if_passed': project_info.get('compliteNumberRegAct')
        })

    @staticmethod
    def add_likes(project):
        url = f'https://regulation.gov.ru/Npa/GetRatingToolbar?' \
              f'id={project["regulation_project_id"]}'
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'lxml')
        buttons = soup.find_all('button')
        if buttons:
            project['likes_num'] = buttons[0].text.strip()
            project['dislikes_num'] = buttons[1].text.strip()

    def add_documents(self, project):
        start_job = datetime.datetime.now()
        url = f'https://regulation.gov.ru/Npa/GetAjaxForm?' \
              f'id={project["regulation_project_id"]}' \
              f'&mnemonic=Npa_AreaRegulation_ListView' \
              f'&readonly=true'
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'lxml')
        project['documents'] = self.search_links(soup)
        end_job = datetime.datetime.now()
        # print(f'Documents downloaded by {end_job - start_job}')

    def search_links(self, soup):
        documents_links = {}
        for k, v in self.doc_names.items():
            link = self.search_link(soup, k)
            if link is None:
                continue
            documents_links[v] = link
        return documents_links

    @staticmethod
    def search_link(soup, doc_name):
        split = str(soup.contents).split(doc_name)
        if len(split) == 1:
            return

        chunk = list(filter(lambda x: x.strip().startswith('</dt>'), split))
        if not chunk:
            return

        substring = chunk[0].split('</dd>')[0]
        regex = "([0-9a-fA-F]{8}" + "-([0-9a-fA-F]{4}-)" + "{3}[0-9a-fA-F]{12})"
        match = re.search(regex, substring)
        if match:
            link = match.group(0)
            return link


class ProjectDumper:
    def __init__(self, task_queue, connection, batch_count=1, waiting_time=3):
        self.batch = []
        self.batch_count = batch_count
        self.task_queue = task_queue
        self.is_accepting_tasks = True
        self.waiting_time = waiting_time
        self.connection = connection
        try:
            self.connection.setup()
        except psycopg2.DatabaseError as e:
            print(e)

    def __call__(self):
        while True:
            try:
                task = self.task_queue.get(timeout=self.waiting_time)
            except Empty:
                if not self.is_accepting_tasks:
                    print('Dumper is empty.')
                    break
            else:
                try:
                    self.batch.append(task)
                    if len(self.batch) >= self.batch_count:
                        self.dump()
                        self.batch = []
                except psycopg2.DatabaseError as e:
                    print(e)
                self.task_queue.task_done()
        self.dump()

    def dump(self):
        for project in self.batch:
            project['last_updated_date'] = str(datetime.datetime.today())
            existing_values = {k: v for k, v in project.items()
                               if v is not None and k != 'documents'}
            self.insert_project(existing_values)
            self.insert_documents(project['regulation_project_id'],
                                  project['last_updated_date'],
                                  project['documents'])

    def insert_project(self, existing_values):
        for k, v in existing_values.items():
            if type(v) == str:
                existing_values[k] = v.replace('\'', ' ')
        keys = ', '.join(existing_values.keys())
        values = ', '.join(f'\'{x}\'' for x in existing_values.values())
        set_string = generate_set_values_string(existing_values)
        statement = """INSERT INTO project ({}) 
                    VALUES ({}) 
                    ON CONFLICT (regulation_project_id) 
                    DO UPDATE SET {};
                    """.format(keys, values, set_string)
        try:
            self.connection.execute_statement(statement)
        except psycopg2.DatabaseError as e:
            print(e)

    def insert_documents(self, project_id, updated, documents):
        if not documents:
            return
        for k, v in documents.items():
            document = {
                'GUID': v,
                'regulation_project_id': project_id,
                'document_type': k,
                'link': f'https://regulation.gov.ru/Files/GetFile?fileid={v}',
                'last_updated_date': updated
            }
            keys = ', '.join(document.keys())
            values = ', '.join(f'\'{x}\'' for x in document.values())
            set_string = generate_set_values_string(document)
            statement = """INSERT INTO document ({}) 
                        VALUES ({}) 
                        ON CONFLICT (GUID) 
                        DO UPDATE SET {};
                        """.format(keys, values, set_string)
            try:
                self.connection.execute_statement(statement)
            except psycopg2.DatabaseError as e:
                print(project_id, e)

    def stop(self):
        self.is_accepting_tasks = False


def download_dump(dump_path):
    url = 'https://regulation.gov.ru/Npa/CollectionRead?' \
          'mnemonic=Npa_AreaRegulation_Grid'
    while True:
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(e)
        else:
            dump = response.json()['Data']
            if dump_path:
                with open(dump_path, 'w') as fp:
                    json.dump(dump, fp)
            else:
                with open('regulation_dump.json', 'w') as fp:
                    json.dump(dump, fp)
            del dump
            break


def rename_keys(project):
    new_project = {}
    keys_map = {
        'id': 'regulation_project_id',
        'statistic_views': 'views_num',
        'statistic_comments': 'comments_num',
        'date': 'creation_date',
        'publishdate': 'publication_date',
        'title': 'act_title',
        'creatordepartment_title': 'developer',
        'stage_title': 'development_stage',
        'status_title': 'project_status',
        'category_title': 'procedure_type',
        'kind_title': 'act_type',
        'degreeregulatoryimpact_title': 'regulatory_impact',
        'creator_fullname': 'added_by',
        'responsible_fullname': 'responsible',
        'startdiscussion': 'public_discussion_start',
        'enddiscussion': 'public_discussion_end',
        'parallelstagestartdiscussion': 'parallel_stage_discussion_start',
        'parallelstageenddiscussion': 'parallel_stage_discussion_end',
        'regionsignificant': 'is_regionally_significant',
        'controlsupervisoryactivities': 'act_changes_controlling_activities',
        'regulatorscissors': 'is_regulatory_guillotine_applied',
        'procedureresult_title': 'mineco_solution'

    }
    for key in project.keys():
        if key.lower() in keys_map.keys():
            new_key = keys_map.get(key.lower())
            new_project[new_key] = project.pop(key)
    new_project['okved_list'] = '; '.join([x.get('Title')
                                           for x in project['Okveds']])
    return new_project


def make_tasks(dump, update):
    queue = Queue()

    if not dump and not update:
        print('Не указан файл дампа для парсинга.')
        sys.exit()

    if not update or not os.path.isfile(dump):
        print('Начинается скачивание файла дампа.')
        download_dump(dump)

    with open(dump, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    for _ in sorted(data, key=lambda x: x['ID'], reverse=True):
        project = flatdict.FlatDict(_, delimiter='_')
        project = rename_keys(project)
        queue.put(project)
    print('Queue submitted.')
    return queue


def submit_tasks(args):
    config = json.load(open(f'{args.config}', 'r')) 
    workdir = config['working_directory']
    
    print(os.getcwd())
    if not os.path.isdir(workdir + '/scraping/'):
        os.mkdir(workdir + '/scraping/')
    
    dump = workdir + '/scraping/regulation_dump.json'
    update = args.update
    tasks = make_tasks(dump, update)
    
    results = Queue()
    
    connection = DBHelper(config['database'])
    dumper = ProjectDumper(results, connection, batch_count=10)

    scraper_executor = ThreadPoolExecutor(max_workers=args.workers)
    for _ in range(args.workers):
        scraper = ProjectScraper(tasks, results)
        scraper_executor.submit(scraper)

    dump_executor = ThreadPoolExecutor(max_workers=1)
    dump_executor.submit(dumper)

    scraper_executor.shutdown(wait=True)
    dumper.stop()
    dump_executor.shutdown(wait=True)
    print("Executors finished")
    print(f"Tasks empty: {tasks.empty()}")
    tasks.join()
    print("No tasks left")
    results.join()
    print("No results left")


def get_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', '--config', required=True)
    arg_parser.add_argument('-u', '--update', type=bool, default=False)
    arg_parser.add_argument('-w', '--workers', type=int, default=1)
    return arg_parser.parse_args()


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    submit_tasks(get_arguments())
    print(datetime.datetime.now() - start_time)
