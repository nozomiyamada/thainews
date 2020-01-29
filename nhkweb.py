import pandas as pd
import re, json, csv, requests, shutil, tqdm
from bs4 import BeautifulSoup
import datetime

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

def scrape_easy_one(url_easy):
    response = requests.get(url_easy, timeout=(15.0, 30.0))
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content.decode('utf-8'), "html.parser")
    url_normal = soup.find('div', class_="link-to-normal").a.get('href')
    date = soup.find('p', class_="article-main__date").text[1:-1]
    title_easy = soup.find('h1', class_="article-main__title")
    title_easy = BeautifulSoup(remove_rt(str(title_easy)), "html.parser").text.strip()
    article_easy = soup.find('div', class_="article-main__body article-body")
    article_easy = BeautifulSoup(tag(remove_rt(str(article_easy))), "html.parser").text.strip()

    return {
        'id':url_easy.split('/')[-1].split('.html')[0],
        'title_easy':title_easy,
        'article_easy':retag(article_easy),
        'url_easy':url_easy,
        'url_normal':url_normal,
        'date_easy':date
    }

def scrape_normal_one(url_normal):
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

def easy(n=1000, reverse=False):
    # open json file
    with open('nhk/nhkwebeasy.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print('articles', len(data))
    with open('nhk/nhkwebeasy.log', 'r') as f:
        minid = min(int(f.readline()), int(data[0]['id'][1:-4]))
        maxid = min(int(f.readline()), int(data[-1]['id'][1:-4]))
    
    if reverse:
        r = range(minid-1, minid-n-1, -1)
    else:
        r = range(maxid+1, maxid+n+1, +1)

    for i in tqdm.tqdm(r):
        result = scrape_easy_one(f'https://www3.nhk.or.jp/news/easy/k{i}1000/k{i}1000.html')
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
        ID = int(f.readline().strip())
        print(date, ID)
    with open('nhk/nhkweb.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print('articles', len(data))

    endid = ID + n
    count = 0
    while ID < endid:
        print(f'ID: {ID}', end='\r')
        result = scrape_normal_one(f'https://www3.nhk.or.jp/news/html/{date}/k{ID}1000.html')
        if result != None:
            count = 0
            if result not in data:
                data.append(result)
                data = sorted(data, key=lambda x:x['id'])
                with open('nhk/nhkweb.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                with open('nhk/nhkweb.log', 'w') as f:
                        f.write(f'{date}\n{ID+1}')
            ID += 1
        else:
            count += 1
            ID += 1
            if count > 30:
                date = date+1
                with open('nhk/nhkweb.log', 'r', encoding='utf-8') as f:
                    _ = f.readline().strip()
                    ID = int(f.readline().strip())
            

def excel():
    pd.read_json('nhk/nhkweb.json', encoding='utf-8').to_excel('nhk/nhkweb.xlsx', encoding='utf-8', index=False)
    pd.read_json('nhk/nhkwebeasy.json', encoding='utf-8').to_excel('nhk/nhkwebeasy.xlsx', encoding='utf-8', index=False)