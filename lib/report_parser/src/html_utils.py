#!/usr/bin/env python3
from pandas import DataFrame
import pandas as pd
import numpy as np
from bs4.element import NavigableString, Tag, Comment, Doctype
from bs4 import BeautifulSoup
from src.text_class import Text

def print_tag(tag):
    print('printing tag:', type(tag), tag.name)
    if type(tag) not in [NavigableString, Doctype, Comment]:
        for child in tag.children:
            print('child:', type(child), child.name)

def get_texts_and_tables(html_elems):
    contents = []
    contents_num = len(html_elems)
    cur_elem_num = 0

    while cur_elem_num < contents_num:
        elem_type, elem = html_elems[cur_elem_num]
        accumulated_texts = []
        table = None

        while elem_type == 'text' and cur_elem_num < contents_num:
            accumulated_texts.append(elem)
            cur_elem_num += 1
            if cur_elem_num < contents_num:
                elem_type, elem = html_elems[cur_elem_num]
            
        if len(accumulated_texts):
            contents.append(Text(accumulated_texts))
            accumulated_texts = []
        
        if elem_type == 'table':
            contents.append(parse_table(elem))
        
        cur_elem_num += 1
    return contents

def parse_table(table_rows):
    max_col_num = get_max_colspan(table_rows) 

    df = pd.DataFrame(columns = range(max_col_num), dtype=str)

    col_shifts = [0]
    row_shift = 0

    for i in range(len(table_rows)):
        html_row = table_rows[i]
        df_len = len(df)

        cur_shift = col_shifts.pop() if col_shifts else 0

        if row_shift == 0:
        #if True:
            df.append(pd.Series(dtype=str), ignore_index=True)

        next_row_shift = 0

        for j in range(len(html_row)):

            cell = html_row[j]
            shape = (cell[0], cell[1])

            need_rows = shape[0] - (len(df) - df_len)
            next_row_shift = max(need_rows - 1, next_row_shift)

            for _ in range(need_rows - 1):
                df.append(pd.Series(dtype=str), ignore_index=True)
                col_shifts.append(cur_shift + shape[1])


            for cell_row_n, cell_col_n in np.ndindex((shape[0], shape[1])):
                df.loc[df_len - row_shift + cell_row_n, cur_shift + cell_col_n] = \
                    cell[2]
                    
            cur_shift += shape[1] 

        if row_shift:
            row_shift -= 1
        row_shift = row_shift + next_row_shift      
        
    return df

def get_max_colspan(table_rows):
    max_col_num = 0
    for row in table_rows:
        col_num = 0
        for cell in row:
            col_num += cell[1]
        max_col_num = max(max_col_num, col_num)
    return(max_col_num)