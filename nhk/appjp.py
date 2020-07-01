import MeCab, re, tqdm
from collections import Counter
import pandas as pd

### CONSTANTS ###

DATA = pd.read_csv('nhkweb.csv')
KANJI = re.compile(r'[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]{2,10}')
HIRAGANA = re.compile(r'[ぁ-ゞ]{1,2}')
KATAKANA = re.compile(r'[ァ-ヾ]{1,2}')

### FUNCTIONS ###

def suru(topn=30, genre=None, filename=None, min_count=3):
    count = Counter()

    # only one genre (str) -> set of genres
    if type(genre) == str:
        genre = [genre]
    genre = set(genre)
    
    for i, row in DATA.iterrows():
        if not genre <= set(eval(row.genre)):
            continue
        lemmas = eval(row.lemma)
        for j, lemma in enumerate(lemmas):
            if j > 0 and lemma == 'する' and re.match(KANJI,lemmas[j-1]):
                count[''.join(lemmas[j-1:j+1])] += 1

    if filename != None:
        df = pd.DataFrame(count.most_common(), columns=['word','count'])
        df = df[df.count >= min_count]
        df.to_csv(filename)
    return count.most_common(topn)

### import this module ###
print('import module appjp.py')
genre = Counter()
for genres in DATA.genre:
    for g in eval(genres):
        genre[g] += 1
print(pd.DataFrame(genre.most_common()), columns=['genre','count'])