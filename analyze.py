import os, json, glob, time, re, csv, shutil, html
import matplotlib.pyplot as plt
plt.style.use("ggplot")
import numpy as np
import scipy as sp
import pandas as pd
from collections import Counter
from gensim.models import word2vec
from gensim.models import KeyedVectors
from pythainlp import word_tokenize as wt
from pythainlp import corpus

def js(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def trim(text:str):
    """
    teim text & tokenize
    """
    text = html.unescape(text)
    text = re.sub(r'(\n|\t|\xa0)', ' ', text)
    text = re.sub(r'(\r|\u200b)', '', text)
    text = re.sub(r'https?://\S* ', '', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'[\'\"‘’“”`\)\(]', '', text)
    return wt(text.strip(' '), keep_whitespace=False) 

def cossim(v1, v2):
    return np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2)

class NewsAnalyze:
    def __init__(self, publisher:str): # publisher: thairath, matichon, dailynews, sanook, nhk
        self.publisher = publisher
        self.path = f'/Users/Nozomi/news/{publisher}/'

    def tokenize(self):
        jsons = set(glob.glob(self.path + '*.json')) # all json files
        tokenized_txt = {f.split('tokenized')[0]+'.json' for f in glob.glob(self.path + '*tokenized.tsv')} # already tokenized file
        to_be_tokenized = jsons - tokenized_txt # untokenized json files
        for json_path in to_be_tokenized:
            save_name = json_path.split('.json')[0] + 'tokenized.txt'
            lst = [trim(news_dic['article']) for news_dic in js(json_path)]
            with open(save_name, 'w', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t', lineterminator='\n')
                writer.writerows(lst)

    def no_article(self):
        return sum(len(js(i)) for i in glob.glob(self.path + '*.json'))

    def make_wf(self):
        txt_list = glob.glob(self.path+'*tokenized.txt')
        count, stop = Counter(), Counter()
        stops = corpus.thai_stopwords()
        for t in txt_list:
            with open(t) as f:
                for line in csv.reader(f, delimiter='\t'):
                    for word in line:
                        count[word] += 1
                        if word not in stops:
                            stop[word] += 1
        # with stopwords
        with open(self.path + 'wf.csv', 'w') as f:
            wr = csv.writer(f, delimiter=',', lineterminator='\n')
            wr.writerows(count.most_common())
        # without stopwords
        with open(self.path + 'wf_stop.csv', 'w') as f:
            wr = csv.writer(f, delimiter=',', lineterminator='\n')
            wr.writerows(stop.most_common())

    def load_wf(self):
        """
        self.count, self.stop are pd.DataFrame
            aaaa 2000
            bbbb 1000
        """
        self.count = pd.read_csv(self.path + 'wf.csv', encoding='utf-8', header=None)
        self.stop  = pd.read_csv(self.path + 'wf_stop.csv', encoding='utf-8', header=None)

    def topn(self, n=50, delimiter=' '):
        print(f'with stopwords\n{delimiter.join(self.count.iloc[:n,0])}\n')
        print(f'w/o stopwords\n{delimiter.join(self.stop.iloc[:n,0])}')

    def topn_th(self, n=50, delimiter=' '):
        only_th = [w for w in self.count.iloc[:3*n,0] if re.match(r'^[ก-๙][ก-๙ \.]*$', w)][:n]
        only_th2 = [w for w in self.stop.iloc[:3*n,0] if re.match(r'^[ก-๙][ก-๙ \.]*$', w)][:n]
        print(f'with stopwords\n{delimiter.join(only_th)}\n')
        print(f'w/o stopwords\n{delimiter.join(only_th2)}')

    def zipf(self):
        cx, sx = range(1, len(self.count)+1), range(1, len(self.stop)+1)
        plt.figure(figsize=(5,5))
        plt.plot(cx, self.count.iloc[:,1], label='with stopwords')
        plt.plot(sx, self.stop.iloc[:,1], label='w/o stopwords')
        plt.title(f'word frequency : {self.publisher}')
        plt.ylabel('word frequency [log]')
        plt.xscale('log'); plt.yscale('log')
        plt.legend(loc='best')
        plt.xlim([1e0,1e7]), plt.ylim([1e0,1e7])
        plt.show()

    def entropy(self):
        """
        entropy = -Σ p*log2(p) = -Σ c/N * log2(c/N) = -1/N Σ c*(log2(c) - log2(N))
        """
        # with stopwords
        N = sum(self.count.iloc[:,1])
        V = len(self.count)
        print(f'token: {N}\nvocab: {V}\nt/v: {N/V:.2f}')
        logN = np.log2(N)
        print(f'entropy with stop: {-1/N * sum(c * (np.log2(c)-logN) for c in self.count.iloc[:,1]):.2f}\n')

        # without stopwords
        N = sum(self.stop.iloc[:,1])
        V = len(self.stop)
        print(f'token: {N}\nvocab: {V}\nt/v: {N/V:.2f}')
        logN = np.log2(N)
        print(f'entropy w/o stop: {-1/N * sum(c * (np.log2(c)-logN) for c in self.stop.iloc[:,1]):.2f}')

### instantiation ###
tr = NewsAnalyze('thairath')
mc = NewsAnalyze('matichon')
dn = NewsAnalyze('dailynews')
sn = NewsAnalyze('sanook')
nhk = NewsAnalyze('nhk')

def zipf_all(publishers=[tr,mc,dn,sn,nhk]):
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    for p in publishers:
        p.load_wf()
        cx, sx = range(1, len(p.count)+1), range(1, len(p.stop)+1)
        ax1.plot(cx, p.count.iloc[:,1], label=p.publisher)
        ax2.plot(sx, p.stop.iloc[:,1], label=p.publisher)
        p.count, p.stop = None, None  # release memory
    ax1.set_title('word frequency with stop')
    ax2.set_title('word frequency w/o stop')
    ax1.set_ylabel('word frequency')
    ax1.set_xscale('log'); ax2.set_xscale('log')
    ax1.set_yscale('log'); ax2.set_yscale('log')
    ax1.legend(loc='best'); ax2.legend(loc='best')
    ax1.set_xlim([1e0,1e7]); ax1.set_ylim([1e0,1e7])
    ax2.set_xlim([1e0,1e7]); ax2.set_ylim([1e0,1e7])
    ax1.set_aspect('equal'); ax2.set_aspect('equal')
    fig.show()

