import csv, json, html
import re, os, glob
import collections
import numpy as np
from pythainlp import word_tokenize

files = glob.glob('/Users/Nozomi/files/news/matichon/*.json')


with open('matichon_tokenized.txt', 'w', encoding='utf-8') as fo:
    for file in files:
        writer = csv.writer(fo, delimiter=' ')
        with open(file, 'r', encoding='utf-8') as fi:
            dic = json.load(fi)
            for i in dic.values():
                line = word_tokenize(i['article'], keep_whitespace=False)
                line = list(filter(lambda x: x !='"' or x!='\n', line))
                writer.writerow(line)