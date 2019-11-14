import csv, json, html
import re, os, glob
import collections
import numpy as np
from pythainlp import word_tokenize
from pythainlp import corpus
import matplotlib.pyplot as plt

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

def text_trim(text:str):
    text = html.unescape(text)
    #text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = text.replace('\r', '')
    text = text.replace('\u200b', '')
    text = text.replace('\xa0', ' ')
    text = re.sub(' +', ' ', text)
    text = re.sub(r'[\'\"‘’“”`\)\(]', '', text)
    return text.strip(' ')

def tokenize(text:str):
    # raw string -> list of tokenized sentences (list of tokens)
    seqs = [text_trim(seq) for seq in text.split('\n')]
    return [word_tokenize(seq, keep_whitespace=False) for seq in seqs if seq !='' and seq != ' '] 

class News:
    def __init__(self, publisher): # publisher: thairath, matichon, dailynews ...
        self.__publisher = publisher
        self.__opened = False  # opened file yet or not
        self.dic = {}  # loaded json file
        self.file_name = ''  # name of json file
        self.word_freq = None  # word frequency
        self.path = ''  # path of json file

    def __check_open(self):
        assert self.__opened, 'open json file first'

    def __add_zero(self, article_id):
        # 5003 -> 0005003 (7 digits) 
        return '0'*(7-len(str(article_id))) + str(article_id)  

    def get_json(self):
        if self.__publisher == 'thairath':
            return glob.glob('/Users/Nozomi/files/news/thairath/*.json')
        elif self.__publisher == 'matichon':
            return glob.glob('/Users/Nozomi/files/news/matichon/*.json')
        elif self.__publisher == 'dailynews':
            return glob.glob('/Users/Nozomi/files/news/dailynews/*.json')

    def load(self, start_id:int):  # start_id = n (* 1000)
        start = '0'*(4-len(str(start_id))) + '{}001'.format(start_id)
        end = self.__add_zero(int(start) + 999)

        if self.__publisher == 'thairath':
            self.path = '/Users/Nozomi/files/news/thairath/json/thairath{}-{}.json'.format(start, end)
        elif self.__publisher == 'matichon':
            self.path = '/Users/Nozomi/files/news/matichon/json/matichon{}-{}.json'.format(start, end)
        elif self.__publisher == 'dailynews':
            self.path = '/Users/Nozomi/files/news/dailynews/json/dailynews{}-{}.json'.format(start, end)
        
        with open(self.path, 'r') as f:
            self.dic = json.load(f)
            self.ids = list(self.dic.keys())

        self.file_name = self.path.rsplit('/')[-1]
        print('opened {}'.format(self.file_name))  # print 'open XXXX.json'
        print('{} articles'.format(len(self.ids)))
        self.__opened = True

    def id_check(self, article_id):
        assert self.__add_zero(article_id) in self.ids, 'no article id'
        return self.__add_zero(article_id)

    def article(self, article_id):
        self.__check_open()
        article_id = self.id_check(article_id)
        return self.dic[article_id]['article']

    def date(self, article_id):
        self.__check_open()
        article_id = self.id_check(article_id)
        return self.dic[article_id]['date']

    def all_date(self):
        self.__check_open()
        date = set()
        for id in self.ids:
            date.add(self.dic[id]['date'].split('T')[0])
        return date

    def headline(self, article_id, print_text=False):
        self.__check_open()
        article_id = self.id_check(article_id)
        if print_text:
            print()
        return self.dic[article_id]['headline']

    def category(self, article_id):
        self.__check_open()
        article_id = self.id_check(article_id)
        return self.dic[article_id]['category']

    def description(self, article_id):
        self.__check_open()
        article_id = self.id_check(article_id)
        return self.dic[article_id]['description']

    def url(self, article_id):
        self.__check_open()
        article_id = self.id_check(article_id)
        return self.dic[article_id]['url']

    def output(self, overwrite=False):
        path = self.path.replace('.json', '.txt')
        if os.path.exists(path) and not overwrite:
            print('file exists')
        else:
            with open(path, 'w', encoding='utf-8') as f:
                for id in self.ids:
                    for seq in tokenize(self.article(id)):
                        f.write(' '.join(seq) + '\n')

    def get_freq(self, top_n=100):
        files = glob.glob(self.path.rsplit('/', 1) + '/*.txt')  # open tokenized files
        self.word_freq = collections.Counter()
        for file in files:
            with open(file, 'r') as f:
                for word in f.read().replace('\n', ' ').split():
                    self.word_freq[word] += 1
        for tpl in self.word_freq.most_common(top_n):
            print(tpl[0], tpl[1])
        with open('freq.csv', 'w') as f:
            writer = csv.writer(f, delimiter=',', lineterminator='\n')
            for tpl in self.word_freq.most_common():
                writer.writerow(tpl)

    def zipf(self, n=10000, remove_stop=False):
        with open('freq.csv' ,'r') as f:
            words = csv.reader(f, delimiter=',')
            if remove_stop:
                y = [int(word[-1]) for word in words if word[0] not in corpus.thai_stopwords()][:n]
            else:
                y = [int(word[-1]) for word in words][:n]
            plt.plot(range(len(y)), y)
            plt.xscale('log')
            plt.yscale('log')
            plt.show()

tr = News('thairath')
mc = News('matichon')
dn = News('dailynews')
