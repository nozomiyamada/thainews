import requests, json, os, csv, re, sys, shutil, tqdm
import numpy as np
from sklearn.linear_model import LinearRegression
from bs4 import BeautifulSoup as BS

def show_data():
    with open ('nhk/nhk.json', 'r', encoding='utf-8') as f:
        global ids
        ids = sorted(x['id'] for x in json.load(f))
        print('oldest ID: %s' % ids[0])
        print('newest ID: %s' % ids[-1])
        print(len(ids), 'articles')

if __name__ != '__main__':
    sys.exit()
else:
    show_data()

def nhk_scrape(n=1000):
    total_list = []
    for i in tqdm.tqdm(range(int(ids[-1])+1, int(ids[-1])+n)):
        url = f"https://www3.nhk.or.jp/nhkworld/th/news/{i}/"
        response = requests.get(url)
        response.encoding='utf-8'
        if response.status_code == 200:
            dic = {}
            soup = BS(response.text, "html.parser")
            data = soup.find('script',type="application/ld+json")
            data = json.loads(data.text)
            dic['headline'] = data['headline']
            dic['article'] = data['articleBody']
            dic['date'] = data['datePublished']
            dic['url'] = url
            dic['id'] = str(i)
            total_list.append(dic)

    with open ('nhk/nhk_new.json', 'w', encoding='utf-8') as f:
        with open ('nhk/nhk.json', 'r', encoding='utf-8') as g:
            old_list = json.load(g)
            for dic in total_list:
                if dic not in old_list:
                    old_list.append(dic)
        json.dump(old_list, f, ensure_ascii=False, indent=4)

    if os.path.exists('nhk/nhk.json') and os.path.exists('nhk/nhk_new.json') and os.path.getsize('nhk/nhk_new.json') >= os.path.getsize('nhk/nhk.json'):
        os.remove('nhk/nhk.json')
        os.rename('nhk/nhk_new.json', 'nhk/nhk.json')
        shutil.copy('nhk/nhk.json', '/Users/Nozomi/gdrive/scraping/nhk')

    show_data()