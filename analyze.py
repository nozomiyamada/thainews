import os, json, glob, re, csv, shutil, html, itertools
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
        tokenized_txt = {f.split('tokenized')[0]+'.json' for f in glob.glob(self.path + '*tokenized.txt')} # already tokenized file
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
        df = pd.DataFrame(count.most_common(),columns=['word', 'count'],index=None)
        df.to_csv(self.path + 'wf.csv',index=None)
        # without stopwords
        df = pd.DataFrame(stop.most_common(),columns=['word', 'count'],index=None)
        df.to_csv(self.path + 'wf_stop.csv',index=None)

    def load_wf(self):
        """
        self.count, self.stop are pd.DataFrame
            word count
            aaaa 2000
            bbbb 1000
        """
        self.count = pd.read_csv(self.path + 'wf.csv', encoding='utf-8')
        self.stop  = pd.read_csv(self.path + 'wf_stop.csv', encoding='utf-8')

    def topn(self, n=50, delimiter=' '):
        self.load_wf()
        print(f'with stopwords\n{delimiter.join(self.count["word"][:n])}\n')
        print(f'w/o stopwords\n{delimiter.join(self.stop["word"][:n])}')

    def topn_th(self, n=50, delimiter=' '):
        self.load_wf()
        only_th = [w for w in self.count.iloc[:3*n,0] if re.match(r'^[ก-๙][ก-๙ \.]*$', w)][:n]
        only_th2 = [w for w in self.stop.iloc[:3*n,0] if re.match(r'^[ก-๙][ก-๙ \.]*$', w)][:n]
        print(f'with stopwords\n{delimiter.join(only_th)}\n')
        print(f'w/o stopwords\n{delimiter.join(only_th2)}')

    def zipf(self):
        self.load_wf()
        cx, sx = range(1, len(self.count)+1), range(1, len(self.stop)+1)
        plt.figure(figsize=(5,5))
        plt.plot(cx, self.count["count"], label='with stopwords')
        plt.plot(sx, self.stop["count"], label='w/o stopwords')
        plt.title(f'word frequency : {self.publisher}')
        plt.ylabel('word frequency [log]')
        plt.xscale('log'); plt.yscale('log')
        plt.legend(loc='best')
        plt.xlim([1e0,1e7]), plt.ylim([1e0,1e7])
        plt.show()

    def entropy(self, remove_punct=True):
        """
        entropy = -Σ p*log2(p) = -Σ c/N * log2(c/N) = -1/N Σ c*(log2(c) - log2(N))
        """
        self.load_wf()
        # remove punctuations
        count_removed = [c for i,w,c in self.count.itertuples() if re.match(r'^[A-zก-๙]', w)]
        stop_removed = [c for i,w,c in self.stop.itertuples() if re.match(r'^[A-zก-๙]', w)]
        count = self.count['count']
        stop = self.stop['count']
        
        result = []
        for i in [count, count_removed, stop, stop_removed]:
            N, V = sum(i), len(i)
            logN = np.log2(N)
            entropy = round(-1/N * sum(c * (np.log2(c)-logN) for c in i), 2)
            result.append([N, V, round(N/V,2), entropy])
        return (pd.DataFrame(result, columns=['token','vocab','t/v','entropy'],
        index=['with stop with punct:', 'with stop w/o  punct:', 'w/o  stop with punct:', 'w/o  stop w/o  punct:']))

### instantiation ###
tr = NewsAnalyze('thairath')
mc = NewsAnalyze('matichon')
dn = NewsAnalyze('dailynews')
sn = NewsAnalyze('sanook')
nhk = NewsAnalyze('nhk')

def zipf_all(publishers=[tr,dn,mc,sn,nhk]):
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

def freq_vec_sim(publishers=[tr,dn,mc,sn], nmax=10000, step=10, only_thai=True, plot=False, show_words=False):
    """
    calculate cosine similarity of each frequency vector (w/o stopwords)
    :nmax: the size of vector
    :only_thai: exclude non-thai character
    :show_words: return word list 
    """
    # make a common word set
    for i, p in enumerate(publishers):
        p.load_wf()
        if i == 0:
            word_order = p.stop['word']
            common_words = set(p.stop['word'])
        else:
            common_words &= set(p.stop['word'])

    # make a ordered list of words
    if only_thai:
        word_order = [w for w in word_order if w in common_words if re.match(r'^[ก-๙][ก-๙ \.]*$', w)][:nmax]
    else:
        word_order = [w for w in word_order if w in common_words][:nmax]

    # make an array of vectors
    vecs = np.zeros((len(publishers), nmax), dtype=float)
    for i, p in enumerate(publishers):
        word_count_dic = dict(zip(p.stop['word'], p.stop['count']))
        for j, w in enumerate(word_order):
            vecs[i,j] = float(word_count_dic[w])

    # calculate cosine similarity for each size
    length = nmax // step
    sim_array = np.zeros((len(publishers), len(publishers), length)) # tensor of rank 3
    for i in range(len(publishers)):
        for j in range(i+1, len(publishers)):
            for n in range(length):
                sim_array[i][j][n] = cossim(vecs[i][:step*(n+1)], vecs[j][:step*(n+1)])
    pub_names = [p.publisher for p in publishers]
    print(pd.DataFrame(sim_array[:,:,-1], index=pub_names,columns=pub_names))

    # plot
    if plot:
        x = np.arange(step, nmax+1, step)
        for i in range(len(publishers)):
            for j in range(i+1, len(publishers)):
                plt.plot(x, sim_array[i][j], label=f'{pub_names[i]}-{pub_names[j]}')
        plt.xscale('log')
        plt.legend(loc='best')
        plt.title('cosine similarity of frequency vector')
        plt.ylabel('size of vector')
        plt.ylabel('cosine similarity')
        plt.show()

    if show_words:
        return word_order
