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

tr_url = 'https://www.thairath.co.th/content/'


##### function for scraping #####

def scrape(start_id, end_id):
    
    json_name = '/Users/Nozomi/files/news/thairath/json/thairath0{}-0{}.json'.format(start_id, end_id)

    file = open(json_name, 'w', encoding='utf-8')

    all_dic = {}

    for article_id in range(start_id, end_id):
        response = requests.get(tr_url + str(article_id))  # get html
        if response.status_code == 200:  # if 404 pass
            soup = BeautifulSoup(response.text, "html.parser")  # get text

            # find more than 2 tags <script>
            content_list = soup.find_all('script', type="application/ld+json")

            # convert final one from json into dict
            try:
                content_dic = json.loads(content_list[-1].text)
            except IndexError:
                continue  # no content -> skip to next id
            
            if len(str(article_id)) < 7: # make all id have 7 digits  e.g. 123 -> 0000123
                id7 = '0'*(7-len(str(article_id)))+str(article_id)
            else:
                id7 = str(article_id)

            all_dic[id7] = {'headline':content_dic['headline'], 'description':content_dic['description'],
            'article':content_dic['articleBody'], 'date':content_dic['datePublished'], 'url':content_dic['mainEntityOfPage']['@id']}
    
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
        assert self.opened, 'open json file first: tr.open(n[10k])'

    def add_zero(self, article_id):
        # 5003 -> 0005003 (7 digits) 
        return '0'*(7-len(str(article_id))) + str(article_id)  

    def open(self, start_id:int):  # start_id = n (* 10000)
        start = '0'*(3-len(str(start_id))) + '{}0001'.format(start_id)
        end = self.add_zero(int(start) + 9999)
        self.path = '/Users/Nozomi/files/news/thairath/json/thairath{}-{}.json'.format(start, end)
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

TR = News()  # instance

##############################################################################

def load(start_id:int):  # start_id = n (* 10000)
    TR.open(start_id)

def article(article_id):
    TR.check_open()
    article_id = TR.id_check(article_id)
    return TR.dic[article_id]['article']

def date(article_id):
    TR.check_open()
    article_id = TR.id_check(article_id)
    return TR.dic[article_id]['date']

def all_date(self):
    TR.check_open()
    date = set()
    for id in self.ids:
        date.add(TR.dic[id]['date'].split('T')[0])
    return date

def headline(article_id, print_text=False):
    TR.check_open()
    article_id = TR.id_check(article_id)
    if print_text:
        print()
    return TR.dic[article_id]['headline']

def description(article_id):
    TR.check_open()
    article_id = TR.id_check(article_id)
    return TR.dic[article_id]['description']

def url(article_id):
    TR.check_open()
    article_id = TR.id_check(article_id)
    return TR.dic[article_id]['url']

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
    path = TR.path.replace('.json', '.txt')
    if os.path.exists(path):
        print('file exists')
    else:
        with open(path, 'w', encoding='utf-8') as f:
            for id in TR.ids:
                for seq in tokenize(article(id)):
                    f.write(' '.join(seq) + '\n')

def word_freq(top_n=100):
    files = glob.glob('/Users/Nozomi/files/news/thairath/json/*.txt')  # open tokenized files
    TR.word_freq = collections.Counter()
    for file in files:
        with open(file, 'r') as f:
            for word in f.read().replace('\n', ' ').split():
                TR.word_freq[word] += 1
    for tpl in TR.word_freq.most_common(top_n):
        print(tpl[0], tpl[1])
    with open('freq.txt', 'w') as f:
        for tpl in TR.word_freq.most_common():
            f.write(tpl[0]+ ' ' + str(tpl[1]) + '\n')

######################################################################