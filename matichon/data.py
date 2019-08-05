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

# all contents of Thairath are https://www.thairath.co.th/content/******* (7digits)

def return_str(text):
    """
    return original text if any
    return '' if None
    (sometimes there is no content in certain keys of json)
    """
    if text is None:
        return ''
    else:
        return text_trim(text)

##### function for scraping #####
"""
content is in <div class="td-main-content-wrap"> -> <article>

"""


def scrape(start_id, end_id):  # 7 digits
    
    json_name = '/Users/Nozomi/files/news/matichon/json/matichon{}-{}.json'.format(start_id, end_id)

    file = open(json_name, 'w', encoding='utf-8')

    all_dic = {}

    for article_id in range(start_id, end_id):
        response = requests.get('https://www.matichon.co.th/news/' + str(article_id))  # get html
        if response.status_code != 200:
            continue
        else:
            soup = BeautifulSoup(response.text, "html.parser")  # get text
            if soup.find('article') == None:
                continue
            else:
                headline = soup.find('h1', class_="entry-title").text
                article = '\n'.join([i.text for i in soup.find('article').find_all('p') if i.text not in ['', '\xa0']])
                date = soup.find('article').find('time').get('datetime')
                article_url = response.url
                category = article_url.split('/')[-2]

                all_dic[str(article_id)] = {"headline":headline, "article":article, "date":date,
                "category":category, "url":article_url}
    json.dump(all_dic, file, indent=4, ensure_ascii=False)
    file.close()


##### data processing #####

class News:

    def __init__(self, newspaper='thairath'):
        self.newspaper = newspaper  # publisher: thairath, matichon, dailynews ...
        self.dic = {}  # loaded json file
        self.opened = False  # opened file yet or not
        self.path = ''  # path of json file
        self.file_name = ''  # name of json file
        self.word_freq = None  # word frequency

    def check_open(self):
        assert self.opened, 'open json file first: mc.open(n[10k])'

    def add_zero(self, article_id):
        # 5003 -> 0005003 (7 digits) 
        return '0'*(7-len(str(article_id))) + str(article_id)  

    def open(self, start_id:int):  # start_id = n (* 10000)
        start = '0'*(3-len(str(start_id))) + '{}0001'.format(start_id)
        end = self.add_zero(int(start) + 9999)
        self.path = '/Users/Nozomi/files/news/matichon/json/matichon{}-{}.json'.format(start, end)
        self.file_name = self.path.rsplit('/')[-1]
        
        with open(self.path, 'r') as f:
            self.dic = json.load(f)
            self.ids = list(self.dic.keys())
        print('opened {}'.format(self.file_name))  # print 'open XXXX.json'
        print('{} articles'.format(len(self.ids)))
        self.opened = True

    def id_check(self, article_id):
        assert self.add_zero(article_id) in self.ids, 'no article id'
        return self.add_zero(article_id)

MC = News()  # instance

##############################################################################

def load(start_id:int):  # start_id = n (* 10000)
    MC.open(start_id)

def article(article_id):
    MC.check_open()
    article_id = MC.id_check(article_id)
    return MC.dic[article_id]['article']

def date(article_id):
    MC.check_open()
    article_id = MC.id_check(article_id)
    return MC.dic[article_id]['date']

def all_date(self):
    MC.check_open()
    date = set()
    for id in self.ids:
        date.add(MC.dic[id]['date'].split('T')[0])
    return date

def headline(article_id, print_text=False):
    MC.check_open()
    article_id = MC.id_check(article_id)
    if print_text:
        print()
    return MC.dic[article_id]['headline']

def category(article_id):
    MC.check_open()
    article_id = MC.id_check(article_id)
    return MC.dic[article_id]['category']

def url(article_id):
    MC.check_open()
    article_id = MC.id_check(article_id)
    return MC.dic[article_id]['url']

#################################################################

def text_trim(text:str):
    text = html.unescape(text)
    #text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = text.replace('\r', '')
    text = text.replace('\u200b', '')
    text = text.replace('\xa0', ' ')
    text = re.sub(' +', ' ', text)
    text = re.sub('[\'\"‘’“”\)\(`]', '', text)
    return text.strip(' ')

def tokenize(text:str):
    # raw string -> list of tokenized sentences (list of tokens)
    seqs = [text_trim(seq) for seq in text.split('\n')]
    return [word_tokenize(seq, keep_whitespace=False) for seq in seqs if seq !='' and seq != ' '] 

def output():
    path = MC.path.replace('.json', '.txt')
    if os.path.exists(path):
        print('file exists')
    else:
        with open(path, 'w', encoding='utf-8') as f:
            for id in MC.ids:
                for seq in tokenize(article(id)):
                    f.write(' '.join(seq) + '\n')

def word_freq(top_n=100):
    files = glob.glob('/Users/Nozomi/files/news/matichon/json/*.txt')  # open tokenized files
    MC.word_freq = collections.Counter()
    for file in files:
        with open(file, 'r') as f:
            for word in f.read().replace('\n', ' ').split():
                MC.word_freq[word] += 1
    for tpl in MC.word_freq.most_common(top_n):
        print(tpl[0], tpl[1])
    with open('freq.txt', 'w') as f:
        for tpl in MC.word_freq.most_common():
            f.write(tpl[0]+ ' ' + str(tpl[1]) + '\n')

######################################################################