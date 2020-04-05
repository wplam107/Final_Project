import numpy as np
import pandas as pd
import re
import pickle

# Universal clean function
def not_HK(df):
    cond1 = (df['headline'].str.find('Hong Kong') == -1) & (df['body'].str.find('Hong Kong') == -1)
    cond2 = (df['headline'].str.find('Hong Kong') == -1) & (df['body'].str.find('Hong Kong') > 1000)
    cond3 = (df['body'].str.find('TODAYS') != -1)
    a = np.where((cond1) | (cond2) | cond3, df.index, 0)
    b = [ i for i in a if i != 0 ]
    df.drop(b, inplace=True)
    return df

# Reuters clean functions
def str_to_date(s):
    match = re.match(r'^\w+\s\d+\,\s\d+', s)
    return match

def clean_body_reu(s):
    try:
        match = re.search(r'(?<=\(Reuters\)\s-\s).*$', s).group(0)
    except:
        match = s
    match = match.replace('’', '')
    match = re.sub(r'\(.*?\)', '', match)
    return match
    

# CCTV clean functions
def clean_body_cctv(s):
    try:
        match = re.search(r'(?<=\s--\s).*$', s).group(0)
    except:
        match = s
    match = match.replace('\'', '')
    match = match.replace('\n', '')
    match = re.sub(r'\(.*?\)', '', match)
    return match

# ABC clean functions
def con_to_string(s):
    if s == '2019-09-17T05:05+1000':
        s = 'September 17, 2019'
    elif s == '2019-06-23T11:20+1000':
        s = 'June 23, 2019'
    return s

def clean_body_abc(s):
    match = s.replace('\'', '')
    match = re.sub(r'\(.*?\)', '', match)
    return match

# CNN clean funtions
def string_to_date_cnn(s):
    match = re.search(r'(?<=,\s)(.+$)', s).group(0)
    return match

def clean_body_cnn(s):
    try:
        match = re.search(r'(?<=\))(.*)', s).group(0)
    except:
        match = s
    match = match.replace('\'', '')
    match = re.sub(r'\(.*?\)', '', match)
    return match