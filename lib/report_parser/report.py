#!/usr/bin/env python3
import tempfile
import mammoth
from xml.sax import parse
from bs4 import BeautifulSoup
from os.path import splitext
from xlsx2html import xlsx2html
from xls2xlsx import XLS2XLSX
from pandas import DataFrame

from src.parsing_tree import ParsingTree
from src.html_utils import get_texts_and_tables
from src.config_parser import ConfigParser
from src.text_class import Text
class Report:
    def __init__(self, fname, config):
        name, ext = splitext(fname)
        self.ext = ext.strip('.')
        self.fname = fname
        self.config = config.get_config_by_extention(self.ext)
        self.log = []
        self.contents = []
        self.html = None

        if self.config == None:
            self.log.append(f'Расширение {self.ext} не поддерживается')
        else:
            self.load()

    def load(self):
        
        with open(self.fname, 'rb') as f:
            if self.ext in ['docx']: 
                converted = mammoth.convert(f)
                self.log += converted.messages
                self.html = converted.value

            elif self.ext in ['xlsx']:
                converted = xlsx2html(f)
                converted.seek(0)
                self.html = converted.read()

            elif self.ext in ['xls']:
                with tempfile.TemporaryFile() as f:
                    x2xFile = XLS2XLSX(self.fname).to_xlsx(f)
                    converted = xlsx2html(x2xFile)
                    converted.seek(0)
                    self.html = converted.read()
    
            else:
                self.html = f.read()

    def texts(self):
        return (x for x in self.contents if type(x) == Text)
    
    def tables(self):
        return (x for x in self.contents if type(x) == DataFrame)

    def parse(self):
        if self.html == None:
            return
        tree = ParsingTree(self.html, config = self.config, extension = self.ext)
        html_elems = tree.elements
        self.contents = get_texts_and_tables(html_elems) 

    def __str__(self):
        to_str = ''
        for elem in self.contents:
            to_str += str(type(elem)) + '\n'
            to_str += str(elem) + '\n'
        return to_str

    def find_table_by_name(self, name): 
        add_next_table = False
        find_text = True
        result = []
        for elem in self.contents:
            if type(elem) == Text:
                if find_text and elem.contains(name):
                    add_next_table = True
                    find_text = False
                else:
                    add_next_table = False
            else:
                if add_next_table:
                    result.append(elem)
        return result

if __name__ == '__main__':
    examples = ['report.html'] 
    config = ConfigParser('configfile.json') 
    for fn in examples:
        print(fn)
        path = 'examples/' + fn
        report = Report(path, config)
        report.parse()
        print('log:', report.log)
        some_tables = report.find_table_by_name('Общая информация')[0]
        print('found', some_tables)
        for text in report.texts():
            print(text)
        for table in report.tables():
            print(table)
        