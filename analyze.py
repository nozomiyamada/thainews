import os, json, glob, re, csv, shutil, html, itertools
import matplotlib.pyplot as plt
plt.style.use('ggplot')
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
    text = re.sub(r'\bhttps?://\S*\b', '', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'[\'\"‘’“”`\)\(]', '', text)
    return wt(text.strip(' '), keep_whitespace=False) 

def cossim(v1, v2):
    return np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2)

class NewsAnalyze:
    def __init__(self, publisher:str): # publisher: thairath, matichon, dailynews, sanook, nhk
        self.publisher = publisher
        self.path = f'/Users/Nozomi/gdrive/scraping/{publisher}/'
        self.stop = corpus.thai_stopwords()

    def tokenize(self, only_one=False):
        jsons = set(glob.glob(self.path + '*.json')) # all json files
        tokenized_txt = {f.split('tokenized')[0]+'.json' for f in glob.glob(self.path + '*tokenized.tsv')} # already tokenized file
        to_be_tokenized = jsons - tokenized_txt # untokenized json files
        for json_path in to_be_tokenized:
            save_name = json_path.split('.json')[0] + 'tokenized.tsv' # thairath01.json -> thairath01tokenized.tsv
            lst = [trim(news_dic['article']) for news_dic in js(json_path)]
            with open(save_name, 'w', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t', lineterminator='\n')
                writer.writerows(lst)
            if only_one:
                return

    def no_article(self):
        self.num_article = sum(len(js(i)) for i in glob.glob(self.path + '*.json'))
        print(f'No. of articles: {self.num_article}')

    def make_wf(self): # make csv files of word frequency 
        tokenized_list = glob.glob(self.path+'*tokenized.tsv')
        count1, count2 = Counter(), Counter() # count1: with stopwords, count2: w/o stopwords
        for t in tokenized_list:
            with open(t) as f:
                for line in csv.reader(f, delimiter='\t'):
                    for word in line:
                        count1[str(word)] += 1
                        if word not in self.stop:
                            count2[str(word)] += 1
        # with stopwords
        df = pd.DataFrame(count1.most_common(),columns=['word','count'],index=None)
        df.to_csv(self.path + 'wf.csv',index=None)
        # without stopwords
        df = pd.DataFrame(count2.most_common(),columns=['word','count'],index=None)
        df.to_csv(self.path + 'wf_stop.csv',index=None)

    def make_df(self): # make document frequnecy for tf-idf
        document_count = Counter()
        tokenized_files = glob.glob(self.path+'*tokenized.tsv')
        for each_file in tokenized_files:
            with open(each_file, encoding='utf-8') as f:
                for document in csv.reader(f, delimiter='\t'):
                    word_set = set(document)
                    for word in word_set:
                        document_count[word] += 1
        df = pd.DataFrame(document_count.most_common(),columns=['word','count'],index=None)
        df.to_csv(self.path + 'df.csv',index=None)

    def load_freq(self):
        """
        self.wf1, self.wf2 are pd.DataFrame
            word count
            aaaa 2000
            bbbb 1000

        self.df is pd.DataFrame too
            word df
            aaaa 100
        """
        self.wf1 = pd.read_csv(self.path + 'wf.csv', encoding='utf-8') # with stopwords
        self.wf2 = pd.read_csv(self.path + 'wf_stop.csv', encoding='utf-8') # without stopwords
        self.df = pd.read_csv(self.path + 'df.csv', encoding='utf-8') # document frequency

    def release_memory(self):
        self.wf1, self.wf2, self.df = [],[],[]

    def tfidf(self, word):
        pass

    def topn(self, n=50, delimiter=' '): # show top n words 
        self.load_freq()
        print(f'wf with stopwords\n{delimiter.join(self.wf1["word"][:n])}\n')
        print(f'wf w/o stopwords\n{delimiter.join(self.wf2["word"][:n])}\n')
        print(f'df\n{delimiter.join(self.df["word"][:n])}')
        self.release_memory()

    def topn_th(self, n=50, delimiter=' '): # show top n Thai words 
        self.load_freq()
        only_th1 = [w for w in self.wf1.iloc[:3*n,0] if re.match(r'^[ก-๙][ก-๙ \.]*$', str(w))][:n]
        only_th2 = [w for w in self.wf2.iloc[:3*n,0] if re.match(r'^[ก-๙][ก-๙ \.]*$', str(w))][:n]
        only_th3 = [w for w in self.df.iloc[:3*n,0] if re.match(r'^[ก-๙][ก-๙ \.]*$', str(w))][:n]
        only_th4 = [w for w in self.df.iloc[:3*n,0] if re.match(r'^[ก-๙][ก-๙ \.]*$', str(w)) and str(w) not in self.stop][:n]
        print(f'wf with stopwords\n{delimiter.join(only_th1)}\n')
        print(f'wf w/o stopwords\n{delimiter.join(only_th2)}\n')
        print(f'df with stopwords\n{delimiter.join(only_th3)}\n')
        print(f'df w/o stopwords\n{delimiter.join(only_th4)}')
        self.release_memory()

    def zipf(self,remove_punct=True): # plot zipf law of the publisher
        self.load_freq()
        x1, x2 = range(1, len(self.wf1)+1), range(1, len(self.wf2)+1)
        plt.figure(figsize=(5,5))
        plt.plot(x1, self.wf1["count"], label='with stopwords')
        plt.plot(x2, self.wf2["count"], label='w/o stopwords')
        plt.title(f'word frequency : {self.publisher}')
        plt.ylabel('word frequency [log]')
        plt.xscale('log'); plt.yscale('log')
        plt.legend(loc='best')
        plt.xlim([1e0,1e7]), plt.ylim([1e0,1e7])
        plt.show()
        self.release_memory()

    def ngram(self, n=2, topn=50):
        tokenized_list = glob.glob(self.path+'*tokenized.tsv')
        ngram_count = Counter()
        for t in tokenized_list: # iterate files
            with open(t) as f:
                for line in csv.reader(f, delimiter='\t'): # iterate articles
                    for i in range(len(line)-n): # iterate words
                        if any([(w in self.stop) or not re.match(r'^[A-zก-๙]', w) for w in line[i:i+n]]): # stop word or punct
                            continue
                        ngram_count[tuple(line[i:i+n])] += 1
        for tpl, count in ngram_count.most_common(topn):
            print(f'| {tpl[0]} | {tpl[1]} | {count} |')

    def entropy(self, remove_punct=True):
        """
        entropy = -Σ p*log2(p) = -Σ c/N * log2(c/N) = -1/N Σ c*(log2(c) - log2(N))
        """
        self.load_freq()
        # remove punctuations
        wf1_removed = [c for i,w,c in self.wf1.itertuples() if re.match(r'^[A-zก-๙]', str(w))]
        wf2_removed = [c for i,w,c in self.wf2.itertuples() if re.match(r'^[A-zก-๙]', str(w))]
        wf1 = self.wf1['count']
        wf2 = self.wf2['count']
        self.release_memory()
        
        # calculate entropies: with or w/o stop, with of w/o punct
        result = []
        for i in [wf1, wf1_removed, wf2, wf2_removed]:
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

def zipf_all(publishers=[tr,dn,mc,sn,nhk]): # plot zipf of all publishers 
    plt.style.use("ggplot")
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    for p in publishers:
        p.load_freq()
        cx, sx = range(1, len(p.wf1)+1), range(1, len(p.wf2)+1)
        ax1.plot(cx, p.wf1.iloc[:,1], label=p.publisher)
        ax2.plot(sx, p.wf2.iloc[:,1], label=p.publisher)
        p.release_memory()
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
        p.load_freq()
        if i == 0:
            word_order = p.wf2['word']
            common_words = set(p.wf2['word'])
        else:
            common_words &= set(p.wf2['word'])
        p.wf1, p.df = [], [] # release memory
    print(f'common words: {len(common_words)}\n')

    # make a ordered list of words
    if only_thai:
        word_order = [w for w in word_order if w in common_words if re.match(r'^[ก-๙][ก-๙ \.]*$', str(w))][:nmax]
    else:
        word_order = [w for w in word_order if w in common_words][:nmax]

    # make an array of vectors
    vecs = np.zeros((len(publishers), nmax), dtype=float)
    for i, p in enumerate(publishers):
        word_count_dic = dict(zip(p.wf2['word'], p.wf2['count']))
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
        plt.xlabel('dimension of vector')
        plt.ylabel('cosine similarity')
        plt.show()

    if show_words:
        return word_order


