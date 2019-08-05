import requests
import csv
import json
import html
import re
import os
from bs4 import BeautifulSoup
import collections
import numpy as np
import glob
from pythainlp import word_tokenize
from gensim.models import word2vec
from gensim.models import KeyedVectors

class News:
    def __init__(self, publisher): # publisher: thairath, matichon, dailynews ...
        self.publisher = publisher
        self.dic = {}  # loaded json file
        self.opened = False  # opened file yet or not
        self.file_name = ''  # name of json file
        self.word_freq = None  # word frequency
        self.path = ''  # path of json file

    def check_open(self):
        assert self.opened, 'open json file first: XX.open(n[10k])'

    def add_zero(self, article_id):
        # 5003 -> 0005003 (7 digits) 
        return '0'*(7-len(str(article_id))) + str(article_id)  

    def open(self, start_id:int):  # start_id = n (* 10000)
        start = '0'*(3-len(str(start_id))) + '{}0001'.format(start_id)
        end = self.add_zero(int(start) + 9999)

        if self.publisher == 'thairath':
            self.path = '/Users/Nozomi/files/news/thairath/json/thairath{}-{}.json'.format(start, end)
        elif self.publisher == 'matichon':
            self.path = '/Users/Nozomi/files/news/matichon/json/matichon{}-{}.json'.format(start, end)
        elif self.publisher == 'dailynews':
            self.path = '/Users/Nozomi/files/news/dailynews/json/dailynews{}-{}.json'.format(start, end)
        
        with open(self.path, 'r') as f:
            self.dic = json.load(f)
            self.ids = list(self.dic.keys())

        self.file_name = self.path.rsplit('/')[-1]
        print('opened {}'.format(self.file_name))  # print 'open XXXX.json'
        print('{} articles'.format(len(self.ids)))
        self.opened = True

    def id_check(self, article_id):
        assert self.add_zero(article_id) in self.ids, 'no article id'
        return self.add_zero(article_id)