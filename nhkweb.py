import pandas as pd
import re, json, csv, requests, shutil, tqdm
from collections import Counter
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime

### functions for nhk web easy ###

def remove_rt(text):
    return re.sub('<rt>.+?</rt>', '', text)

def tag(text):
    text = re.sub(r'<span class="colorC">(.+?)</span>', r"{org}\1{/org}", text)
    text = re.sub(r'<span class="colorL">(.+?)</span>', r"{plc}\1{/plc}", text)
    text = re.sub(r'<span class="colorN">(.+?)</span>', r"{per}\1{/per}", text)
    return text

def retag(text):
    text = re.sub(r'{org}(.+?){/org}', r"<org>\1</org>", text)
    text = re.sub(r'{plc}(.+?){/plc}', r"<plc>\1</plc>", text)
    text = re.sub(r'{per}(.+?){/per}', r"<per>\1</per>", text)
    return text

def remove_a(text):
    text = re.sub(r'</?a.*?>', '', text)
    text = re.sub(r'<span class="under">(\w+)</span>', r'\1', text)
    return text

def easy_one_new(url_easy):
    response = requests.get(url_easy, timeout=(15.0, 30.0))
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content.decode('utf-8'), "html.parser")
    url_normal = soup.find('div', class_="link-to-normal").a.get('href')
    date = soup.find('p', class_="article-main__date").text[1:-1]
    title_easy = soup.find('h1', class_="article-main__title")
    title_easy_ruby = ''.join([str(t) for t in title_easy.contents]).strip()
    title_easy = BeautifulSoup(remove_rt(str(title_easy)), "html.parser").text.strip()
    article_easy = soup.find('div', class_="article-main__body article-body")
    article_easy = BeautifulSoup(tag(remove_rt(str(article_easy))), "html.parser").text.strip()
    article_easy_ruby = soup.find('div', class_="article-main__body article-body").find_all('p')
    article_easy_ruby = '\n'.join([''.join([remove_a(str(l)) for l in p.contents]) for p in article_easy_ruby if p != []]).strip()
    
    return {
        'id':url_easy.split('/')[-1].split('.html')[0],
        'title_easy':title_easy,
        'title_easy_ruby':title_easy_ruby,
        'article_easy':retag(article_easy),
        'article_easy_ruby':article_easy_ruby,
        'url_easy':url_easy,
        'url_normal':url_normal,
        'date_easy':date
    }

def easy_one_old(html):
    soup = BeautifulSoup(html, "html.parser")
    url_normal = soup.find('div', id="regularnews").a.get('href').split('/http://')[-1]
    url_normal = 'http://' + url_normal
    date = soup.find('p', id="newsDate").text[1:-1]
    url_easy = soup.find('meta', attrs={'name':'shorturl'}).get('content')
    title_easy = soup.find('div', id='newstitle').h2
    title_easy_ruby = ''.join([str(t) for t in title_easy.contents]).strip()
    title_easy = BeautifulSoup(remove_rt(str(title_easy)), "html.parser").text.strip()
    article_easy = soup.find('div', id="newsarticle")
    article_easy = BeautifulSoup(tag(remove_rt(str(article_easy))), "html.parser").text.strip()
    article_easy_ruby = soup.find('div', id="newsarticle").find_all('p')
    article_easy_ruby = '\n'.join([''.join([remove_a(str(l)) for l in p.contents]) for p in article_easy_ruby if p != []]).strip()
    
    return {
        'id':url_easy.split('/')[-1].split('.html')[0],
        'title_easy':title_easy,
        'title_easy_ruby':title_easy_ruby,
        'article_easy':retag(article_easy),
        'article_easy_ruby':article_easy_ruby,
        'url_easy':url_easy,
        'url_normal':url_normal,
        'date_easy':date
    }

### functions for nhk web normal ###

def normal_one_new(url_normal):
    response = requests.get(url_normal, timeout=(15.0, 30.0))
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content.decode('utf-8'), "html.parser")
    json_data = json.loads(soup.find_all("script", type="application/ld+json")[-1].text)
    title = json_data['headline']
    date = json_data['datePublished']
    date_m = json_data['dateModified']
    genre = json_data['genre']
    keywords = json_data['keywords']
    article = soup.find('div', id="news_textbody").text
    if soup.find_all('div', id="news_textmore") != []:
        for textmore in soup.find_all('div', id="news_textmore"):
            article += ('\n' + textmore.text)
    if soup.find_all('div', class_="news_add") != []:
        for newsadd in soup.find_all('div', class_="news_add"):
            if newsadd.h3 != None:
                newsadd.h3.extract()
            article += ('\n' + newsadd.text)
            
    return {
        'id':url_normal.split('/')[-1].split('.html')[0],
        'title':title,
        'article':article.strip(),
        'genre':genre,
        'keywords':keywords,
        'url':url_normal,
        'datePublished':date,
        'dateModified':date_m
    }


### scrape new articles ###

def easy(n=1000, reverse=False):
    # open json file
    with open('nhk/nhkwebeasy.json', 'r', encoding='utf-8') as f:
        print('articles', len(json.load(f)))
    with open('nhk/nhkwebeasy.log', 'r') as f:
        minid = min(int(f.readline()), int(data[0]['id'][1:-4]))
        maxid = min(int(f.readline()), int(data[-1]['id'][1:-4]))
    if reverse:
        r = range(minid-1, minid-n-1, -1)
    else:
        r = range(maxid+1, maxid+n+1, +1)

    for i in tqdm.tqdm(r):
        result = easy_one_new(f'https://www3.nhk.or.jp/news/easy/k{i}1000/k{i}1000.html')
        if result != None:
            data.append(result)
            data = sorted(data, key=lambda x:x['id'])
            with open('nhk/nhkwebeasy.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

    if reverse:
        with open('nhk/nhkwebeasy.log', 'w') as f:
            f.write(f'{minid-n}\n{maxid}')
    else:
        with open('nhk/nhkwebeasy.log', 'w') as f:
            f.write(f'{minid}\n{maxid+n}')
    #shutil.copy('nhk/nhkwebeasy.json', '/Users/Nozomi/gdrive/scraping/')

def normal(n=1000):
    # open json file
    with open('nhk/nhkweb.log', 'r', encoding='utf-8') as f:
        date = int(f.readline().strip())
        firstID = int(f.readline().strip())
        print(date, firstID)
    with open('nhk/nhkweb.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print('articles', len(data))

    ID, lastID = firstID, firstID
    endid = ID + n
    count = 0
    while ID < endid:
        print(f'ID: {ID}', end='\r')
        result = normal_one_new(f'https://www3.nhk.or.jp/news/html/{date}/k{ID}1000.html')
        if result != None:
            count = 0
            if result not in data:
                data.append(result)
                data = sorted(data, key=lambda x:x['id'])
                with open('nhk/nhkweb.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                with open('nhk/nhkweb.log', 'w') as f:
                        f.write(f'{date}\n{ID+1}')
                lastID = ID
            ID += 1
        else:
            count += 1
            ID += 1
            if count > 30:
                date = date+1
                ID = lastID

def change_tag(text):
    text = re.sub(r'<(per|org|plc)>', r"<span class='\1'>", text)
    text = re.sub(r'</(per|org|plc)>', '</span>', text)
    return text

def join():
    """
    make .js file
    """
    with open('nhk/nhkweb.json', encoding='utf-8') as f:
        normal = json.load(f)
    with open('nhk/nhkwebeasy.json', encoding='utf-8') as f:
        easy = json.load(f)
    ids = set(dic['id'] for dic in normal) & set(dic['id'] for dic in easy)
    normal = sorted([dic for dic in normal if dic['id'] in ids], key=lambda x:x['id'], reverse=True)
    easy = sorted([dic for dic in easy if dic['id'] in ids], key=lambda x:x['id'], reverse=True)
    print(len(normal), len(easy))

    joined = [{
            'id':n['id'], 
            'article_n':n['article'],
            #'article_e':change_tag(e['article_easy']),
            'article_e':e.get('article_easy_ruby', change_tag(e['article_easy'])),
            'genre':n['genre'],
            'title_n':n['title'],
            'title_e':e['title_easy'],
            'title_e_ruby':e['title_easy_ruby'], 
            'date':n['datePublished'].split('T')[0],
            'urlnormal':n['url'],
            'urleasy':e['url_easy']
            } for n, e in zip(normal, easy)]

    # make article list of each category
    # category = ['社会', '国際', 'ビジネス', 'スポーツ', '政治', '科学・文化', '暮らし', '地域', '気象・災害']
    
    # 社会
    with open('../nozomiyamada.github.io/js/nhk/social.js', 'w', encoding='utf-8') as f:
        article_data = [dic for dic in joined if '社会' in dic['genre']]
        f.write('article_data = ' + json.dumps(article_data, indent=4, ensure_ascii=False))
    # 国際
    with open('../nozomiyamada.github.io/js/nhk/international.js', 'w', encoding='utf-8') as f:
        article_data = [dic for dic in joined if '国際' in dic['genre']]
        f.write('article_data = ' + json.dumps(article_data, indent=4, ensure_ascii=False) +';\n')
    # ビジネス
    with open('../nozomiyamada.github.io/js/nhk/business.js', 'w', encoding='utf-8') as f:
        article_data = [dic for dic in joined if 'ビジネス' in dic['genre']]
        f.write('article_data = ' + json.dumps(article_data, indent=4, ensure_ascii=False) +';\n')
    # スポーツ
    with open('../nozomiyamada.github.io/js/nhk/sport.js', 'w', encoding='utf-8') as f:
        article_data = [dic for dic in joined if 'スポーツ' in dic['genre']]
        f.write('article_data = ' + json.dumps(article_data, indent=4, ensure_ascii=False) +';\n')
    # 政治
    with open('../nozomiyamada.github.io/js/nhk/politic.js', 'w', encoding='utf-8') as f:
        article_data = [dic for dic in joined if '政治' in dic['genre']]
        f.write('article_data = ' + json.dumps(article_data, indent=4, ensure_ascii=False) +';\n')
    # 科学
    with open('../nozomiyamada.github.io/js/nhk/science.js', 'w', encoding='utf-8') as f:
        article_data= [dic for dic in joined if '科学・文化' in dic['genre']]
        f.write('article_data = ' + json.dumps(article_data, indent=4, ensure_ascii=False) +';\n')
    # 暮らし
    with open('../nozomiyamada.github.io/js/nhk/life.js', 'w', encoding='utf-8') as f:
        article_data = [dic for dic in joined if '暮らし' in dic['genre']]
        f.write('article_data = ' + json.dumps(article_data, indent=4, ensure_ascii=False) +';\n')
    # 地域
    with open('../nozomiyamada.github.io/js/nhk/local.js', 'w', encoding='utf-8') as f:
        article_data = [dic for dic in joined if '地域' in dic['genre']]
        f.write('article_data = ' + json.dumps(article_data, indent=4, ensure_ascii=False) +';\n')
    # 気象
    with open('../nozomiyamada.github.io/js/nhk/weather.js', 'w', encoding='utf-8') as f:
        article_data = [dic for dic in joined if '気象・災害' in dic['genre']]
        f.write('article_data = ' + json.dumps(article_data, indent=4, ensure_ascii=False) +';\n')

    # make summary data as js file
    with open('../nozomiyamada.github.io/js/nhk/data_summary.js', 'w', encoding='utf-8') as f:

        # article number, category
        category_count = Counter()
        for dic in normal:
            for genre in dic['genre']:
                category_count[genre] += 1
        jsonarray = f"article_number = {len(ids)};\n"
        jsonarray += "category = " + json.dumps(category_count.most_common(), ensure_ascii=False) + ';\n'
        f.write(jsonarray)

        # kanji frequency
        n_count, e_count = Counter(), Counter()
        n_total, e_total = 0, 0
        for dic in joined:
            for ch in dic['article_n']:
                if 19968 <= ord(ch) <= 40912:
                    n_count[ch] += 1
                    n_total += 1
            for ch in dic['article_e']:
                if 19968 <= ord(ch) <= 40912:
                    e_count[ch] += 1
                    e_total += 1
        n_count = [[word, count, round(count/n_total*100, 6)] for word, count in n_count.most_common()]
        e_count = [[word, count, round(count/n_total*100, 6)] for word, count in e_count.most_common()]
        jsonarray = 'rank_n = ' + json.dumps(n_count, ensure_ascii=False) + ';\nrank_e = ' + json.dumps(e_count, ensure_ascii=False)
        jsonarray = jsonarray + f';\ntotal_n = {n_total};\ntotal_e = {e_total}'
        f.write(jsonarray)


def duplicate():
    with open('./nhk/nhkweb.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    newlist = []
    for dic in data:
        if dic not in newlist:
            newlist.append(dic)
    with open('./nhk/nhkweb.json', 'w', encoding='utf-8') as f:
        data = sorted(newlist, key=lambda x:x['id'])
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_link(start=0):
    notyet = []
    n_list = pd.read_json('nhk/nhkweb.json', encoding='utf-8')['url'].tolist()
    df_e = pd.read_json('nhk/nhkwebeasy.json', encoding='utf-8') 
    for i in df_e['url_normal'][start:]:
        if i not in n_list:
            notyet.append(i)
    return notyet
