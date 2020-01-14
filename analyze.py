import os, json, glob, re, csv, shutil, html, itertools
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import numpy as np
import scipy as sp
import pandas as pd
from collections import Counter
from scipy.stats import chi2_contingency
from gensim.models import word2vec
from gensim.models import KeyedVectors
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
from pythainlp import word_tokenize as wt
from pythainlp import corpus

def js(filepath) -> list:
    with open(filepath, 'r') as f:
        return json.load(f)

def clean(text:str) -> list:
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

def cossim(v1, v2) -> float:
    return np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2)

stopwords = corpus.thai_stopwords()

class NewsAnalyze:
    def __init__(self, publisher:str): # publisher: thairath, matichon, dailynews, sanook, nhk
        self.publisher = publisher
        self.path = f'/Users/Nozomi/gdrive/scraping/{publisher}/'
        self.tokenized = sorted(glob.glob(self.path+'*tokenized.tsv')) # list of tokenized file

    def tokenize(self, only_one=False):
        jsons = set(glob.glob(self.path + '*.json')) # all json files
        tokenized_txt = {f.split('tokenized')[0]+'.json' for f in glob.glob(self.path + '*tokenized.tsv')} # already tokenized file
        to_be_tokenized = sorted(jsons - tokenized_txt) # untokenized json files
        for json_path in to_be_tokenized:
            save_name = json_path.split('.json')[0] + 'tokenized.tsv' # thairath01.json -> thairath01tokenized.tsv
            lst = [clean(each_dic['article']) for each_dic in js(json_path)]
            # lst = [[each_dic['id']] + clean(each_dic['article']) for each_dic in js(json_path)] # with id
            with open(save_name, 'w', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t', lineterminator='\n')
                writer.writerows(lst)
            if only_one:
                return

    def get_no_article(self):
        self.no_article = sum(len(js(i)) for i in glob.glob(self.path + '*.json'))
        print(f'No. of articles: {self.no_article}')

    def period(self):
        jsons = set(glob.glob(self.path + '*.json')) # all json files
        date_set = set()
        for j in jsons:
            data = js(j)
            for dic in data:
                if self.publisher != 'dailynews':
                    date_set.add(dic['date'].split('T')[0].rsplit('-',1)[0])
        return sorted(date_set)

    def make_wf(self): # make csv files of word frequency 
        count1, count2 = Counter(), Counter() # count1: with stopwords, count2: w/o stopwords
        for t in self.tokenized:
            with open(t) as f:
                for line in csv.reader(f, delimiter='\t'):
                    for word in line[1:]:
                        count1[str(word)] += 1
                        if word not in stopwords:
                            count2[str(word)] += 1
        # with stopwords
        df = pd.DataFrame(count1.most_common(),columns=['word','count'],index=None)
        df.to_csv(self.path + 'wf.csv',index=None)
        # without stopwords
        df = pd.DataFrame(count2.most_common(),columns=['word','count'],index=None)
        df.to_csv(self.path + 'wf_stop.csv',index=None)

    def make_df(self): # make document frequnecy for tf-idf
        self.get_no_article()
        document_count = Counter()
        for each_file in self.tokenized:
            with open(each_file, encoding='utf-8') as f:
                for document in csv.reader(f, delimiter='\t'):
                    word_set = set(document)
                    for word in word_set:
                        document_count[word] += 1
        document_count = [(word, count, round(count*100/self.no_article, 2)) for word, count in document_count.most_common()]
        df = pd.DataFrame(document_count, columns=['word','count','percentage'], index=None)
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

    def load_df(self):
        df_table = pd.read_csv(self.path + 'df.csv', encoding='utf-8') # document frequency
        self.df = {word:df/100 for word,df in zip(df_table['word'], df_table['percentage'])}

    def release_memory(self):
        self.wf1, self.wf2, self.df = [],[],[]

    def make_tfidf(self):
        """
        tfidf = (1 + log10tf) * log10(N/df)

        tfidf_dic is dictionary of dictionaries:
        tfidf_dic = {
            100:{'go':3.5, 'come':3.0,...}
            101:{'go':3.0, 'come':2.0,...}
            ,...
        }
        """
        self.get_no_article()
        self.load_df()
        tfidf_dic = {} # dictionary of tf, key is article ID
        for each_file in self.tokenized: # iterate files
            with open(each_file) as f:
                for line in csv.reader(f, delimiter='\t'): # iterate articles
                    tf = Counter(line[1:])
                    tfidf = {w:(1+np.log10(v)) * np.log10(1/self.df[w]) for w,v in tf.items()}
                    tfidf_dic[line[0]] = sorted(tfidf.items(), key=lambda x:x[1], reverse=True)[:20]
            return tfidf_dic

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
        only_th4 = [w for w in self.df.iloc[:3*n,0] if re.match(r'^[ก-๙][ก-๙ \.]*$', str(w)) and str(w) not in stopwords][:n]
        print(f'wf with stopwords\n{delimiter.join(only_th1)}\n')
        print(f'wf w/o stopwords\n{delimiter.join(only_th2)}\n')
        print(f'df with stopwords\n{delimiter.join(only_th3)}\n')
        print(f'df w/o stopwords\n{delimiter.join(only_th4)}')
        self.release_memory()

    def zipf(self, remove_punct=True, rho=0): # plot zipf law of the publisher
        """
        f(r) ∝　(r+ρ)^-k 
        """
        self.load_freq()
        x1, x2 = np.arange(1, len(self.wf1)+1)+rho, np.arange(1, len(self.wf2)+1)+rho
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

    def textlength(self): # relationship between vocab and text length
        x, y = np.array([]), np.array([]) # x:text length, y:vocab 
        for each_file in self.tokenized:
            with open(each_file) as f:
                for line in csv.reader(f, delimiter='\t'): # iterate articles
                    if len(line[1:]) != 0:
                        x = np.append(x, len(line[1:]))
                        y = np.append(y, len(set(line[1:])))
        plt.figure(figsize=(5,5))
        plt.scatter(x, y, s=1)
        plt.title(f'vocabulary - text length : {self.publisher}')
        plt.xlabel('text length')
        plt.ylabel('vocabulary')
        plt.xscale('log'); plt.yscale('log')
        plt.xlim([1e1,1e4]), plt.ylim([1e1,1e4])
        plt.show()

        # linear regression
        x = np.log10(x).reshape(-1,1)
        y = np.log10(y).reshape(-1,1)
        LR = LinearRegression()
        LR.fit(x, y)
        print('coef:', LR.coef_[0])
        print('intercept:', LR.intercept_)
        print('R2:', r2_score(LR.predict(x), y))

    def ngram(self, n=2, topn=50):
        ngram_count = Counter()
        for t in self.tokenized: # iterate files
            with open(t) as f:
                for line in csv.reader(f, delimiter='\t'): # iterate articles
                    for i in range(len(line)-n): # iterate words
                        if any([(w in stopwords) or not re.match(r'^[A-zก-๙]', w) for w in line[i:i+n]]): # stop word or punct
                            continue
                        ngram_count[tuple(line[i:i+n])] += 1
        for tpl, count in ngram_count.most_common(topn):
            print('|'+'|'.join(tpl+[count])+'|')

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

    def make_w2v(self):
        pass

    def make_d2v(self,epoch=10):
        for j, each_file in enumerate(self.tokenized):
            with open(each_file,'r') as f:
                if j == 0:
                    self.trainings = [TaggedDocument(words = line[1:], tags = [line[0]]) for line in csv.reader(f, delimiter='\t')]
                else:
                    self.trainings += [TaggedDocument(words = line[1:], tags = [line[0]]) for line in csv.reader(f, delimiter='\t')]
        model = Doc2Vec(documents=self.trainings, dm = 0, vector_size=300, window=8, min_count=5, workers=4, epochs=epoch)
        return model

    def show_content(self, article_id):
        if self.publisher == 'nhk':
            for dic in js(self.path + 'nhk.json'):
                if dic['id'] == str(article_id):
                    print('Headline\n', dic['headline'], '\n')
                    print('Article\n', dic['article'])
                    return

### instantiation ###
tr = NewsAnalyze('thairath')
mc = NewsAnalyze('matichon')
dn = NewsAnalyze('dailynews')
sn = NewsAnalyze('sanook')
nhk = NewsAnalyze('nhk')

def zipf_all(publishers=[tr,dn,mc,sn,nhk], rho=0): # plot zipf of all publishers 
    plt.style.use("ggplot")
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    for p in publishers:
        p.load_freq()
        cx, sx = np.arange(1, len(p.wf1)+1)+rho, np.arange(1, len(p.wf2)+1)+rho
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

def chi_square(self, publishers=[tr,dn,mc,sn,nhk]):
    chi_array = np.zeros((len(publishers), len(publishers)))
    for i in range(len(publishers)):
        publishers[i].load_freq()
        for j in range(i+1, len(publishers)):
            publishers[j].load_freq()
            chi,_,_,_ = chi2_contingency(publishers[i].wf2['count'],publishers[j].wf2['count'])
            chi_array[i][j] = chi
            print(chi)
            publishers[j].release_memory()
        publishers[i].release_memory()
    pub_names = [p.publisher for p in publishers]
    print(pd.DataFrame(chi_array, index=pub_names,columns=pub_names))

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


