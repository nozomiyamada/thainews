from bs4 import BeautifulSoup
from pythainlp import word_tokenize, corpus
from gensim.models import word2vec
import requests
import json

url = 'https://www.siamzone.com/music/thailyric/' # + id 5 digits

def scrape(start_id, end_id):
    with open('siamzone{}-{}.json'.format(start_id, end_id), 'w') as f:
        all_dic = {}
        for id in range(start_id, end_id):
            response = requests.get(url + str(id))
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                lyrics = soup.find('div', id="lyrics-content").text.split('\n\n', 1)[-1].strip('\r\n').strip('\t').strip('\n')
                date = soup.find('meta', itemprop="datePublished").get('content')

                try:
                    title_artist = soup.find('meta', property="og:title").get('content').split('-')
                    title = title_artist[0].split(' ', 1)[-1].strip()
                    artist = title_artist[1].strip()
                    all_dic[id] = {'artist':artist, 'title':title, 'lyrics':lyrics, 'date':date}
                except:
                    print(id)

                
            else:
                pass
        json.dump(all_dic, f, indent=4, ensure_ascii=False)

def tokenize(lyrics):
    seqs = lyrics.split('\n')
    tokens = [word_tokenize(seq, keep_whitespace=False) for seq in seqs]
    tokens = [seq for seq in tokens if seq != []]
    return tokens

def make_txt():
    with open('siamzone.txt', 'w') as f:
        ids = data.keys()
        writer = csv.writer(f, delimiter=' ', lineterminator='\n')
        for id in ids:
            lyr = data[id]['lyrics']
            tokens = tokenize(lyr)
            writer.writerows(tokens)

def make_model(skip_gram=True, epoch=5):
    with open('siamzone.txt', 'r') as f:
        if skip_gram:
            skip = 1
            savename = 'siamzone_skip'
        else:
            skip = 0
            savename = 'siamzone_cbow'
        sentences = word2vec.LineSentence(f)
        model = word2vec.Word2Vec(sentences, sg=skip, size=300, min_count=3, window=5, iter=epoch)
        model.save(savename + '.model')
        model.wv.save_word2vec_format(savename + '.bin', binary=True)

