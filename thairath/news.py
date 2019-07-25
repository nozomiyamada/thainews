from glob import glob
import json
from pythainlp import word_tokenize
from gensim.models import word2vec
from gensim.models import KeyedVectors
import html
import numpy as np
import re
import os

class News:

    ### instance: tr.method

    def __init__(self, newspaper='thairath'):
        self.newspaper = newspaper  # publisher: thairath, matichon, dailynews ...
        self.dic = {}  # loaded json file
        self.opened = False  # opened file yet or not
        self.path = ''  # path of json file
        self.file_name = ''  # name of json file

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

    def text_trim(self, text:str):
        text = html.unescape(text)
        #text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        text = text.replace('\r', '')
        text = text.replace('\u200b', '')
        text = text.replace('\xa0', ' ')
        text = re.sub(' +', ' ', text)
        text = re.sub('[\'\"‘’“”`]', '', text)
        return text.strip(' ')

###################################################################################

    def id_check(self, article_id):
        assert self.add_zero(article_id) in self.ids, 'no article id'
        return self.add_zero(article_id)

    def all_num(self):
        self.check_open()
        return len(self.dic.keys())

    def all_date(self):
        self.check_open()
        date = set()
        for id in self.ids:
            date.add(self.dic[id]['datePublished'].split('T')[0])
        return date

    def get_article(self, article_id):
        self.check_open()
        article_id = self.id_check(article_id)
        return self.dic[article_id]['articleBody']

    def get_date(self, article_id):
        self.check_open()
        article_id = self.id_check(article_id)
        return self.dic[article_id]['datePublished']

    def get_headline(self, article_id, print_text=False):
        self.check_open()
        article_id = self.id_check(article_id)
        if print_text:
            print()
        return self.dic[article_id]['headline']

    def get_description(self, article_id):
        self.check_open()
        article_id = self.id_check(article_id)
        return self.dic[article_id]['description']

    def get_url(self, article_id):
        self.check_open()
        article_id = self.id_check(article_id)
        return self.dic[article_id]['mainEntityOfPage']['@id']

#################################################################

    def tokenize(self, text:str):
        # raw string -> list of tokenized sentences (list of tokens)
        seqs = [self.text_trim(seq) for seq in text.split('\n')]
        return [word_tokenize(seq, keep_whitespace=False) for seq in seqs if seq !='' and seq != ' '] 
    
    def output(self):
        path = self.path.replace('.json', '.txt')
        if os.path.exists(path):
            print('file exists')
        else:
            with open(path, 'w', encoding='utf-8') as f:
                for id in self.ids:
                    for seq in self.tokenize(self.get_article(id)):
                        f.write(' '.join(seq) + '\n')

tr = News()


######################################################################

def make_model(text_file='/Users/Nozomi/files/news/thairath/json/cat.txt', skipgram=0, epoch=3):
    if skipgram == 0:
        save_name = text_file.rsplit('/', 1)[0] + '/cbow'
    else:
        save_name = text_file.rsplit('/', 1)[0] + '/skip'
    sentences = word2vec.LineSentence(text_file)
    model = word2vec.Word2Vec(sentences, sg=skipgram, size=300, min_count=5, window=5, iter=epoch)  # CBOW: sg=0, skip-gram: sg=1
    model.save(save_name+'.model')
    model.wv.save_word2vec_format(save_name+'.bin', binary=True)