import requests
from bs4 import BeautifulSoup
import json

def add_zero(number:int, digits=7):
    return '0'*(digits-len(str(number))) + str(number)

def thairath(start_id, end_id):  # 7 digits
    all_list = []
    # scraping
    for article_id in range(int(start_id), int(end_id)):
        response = requests.get('https://www.thairath.co.th/content/' + str(article_id))
        if response.status_code == 200:  # if 404 pass
            soup = BeautifulSoup(response.text, "html.parser")  # get html

            # find more than 2 tags <script>, the final one is content
            content_list = soup.find_all('script', type="application/ld+json")

            # convert the final one from json into dict
            try:
                content_dic = json.loads(content_list[-1].text)
            except:
                continue  # no content -> skip for loop to next id

            dic = {'headline':content_dic['headline'], 'description':content_dic['description'],
            'article':content_dic['articleBody'], 'date':content_dic['datePublished'], 'id':str(article_id), 'url':content_dic['mainEntityOfPage']['@id']}
            all_list.append(dic)

    # open json file
    json_name = '/Users/Nozomi/files/news/thairath/json/thairath{}-{}.json'.format(add_zero(start_id), add_zero(end_id- 1))
    with open(json_name, 'w', encoding='utf-8') as f:
        json.dump(all_list, f, indent=4, ensure_ascii=False)


def matichon(start_id, end_id):  # 7 digits
    # open json file
    json_name = '/Users/Nozomi/files/news/matichon/matichon{}-{}.json'.format(add_zero(start_id), add_zero(end_id-1))
    file = open(json_name, 'w', encoding='utf-8')

    # dictionary: {id: content} - saved as json
    all_dic = {}

    # scraping
    for article_id in range(int(start_id), int(end_id)):
        response = requests.get('https://www.matichon.co.th/news/' + str(article_id))
        if response.status_code != 200:
            continue
        else:
            soup = BeautifulSoup(response.text, "html.parser")  # get html
            if soup.find('article') == None:
                continue
            else:
                try:
                    headline = soup.find('h1', class_="entry-title").text
                    article = '\n'.join([i.text for i in soup.find('article').find_all('p') if i.text not in ['', '\xa0']])
                    date = soup.find('article').find('time').get('datetime')
                    article_url = response.url
                    category = article_url.split('/')[-2]
                    id7 = '0'*(7-len(str(article_id))) + str(article_id) 

                    all_dic[id7] = {"headline":headline, "article":article, "date":date,
                    "category":category, "url":article_url}
                except:
                    continue
    json.dump(all_dic, file, indent=4, ensure_ascii=False)
    file.close()

def dailynews(start_id, end_id, category=None):  # 6 digits
    category_list = ['politics', 'regional', 'entertainment', 'economic', 'crime', 'foreign', 'royalnews',
    'women', 'education', 'bangkok', 'it', 'agriculture', 'sports']
    assert category in category_list, 'must choose category: {}'.format(' '.join(category_list))

    # open json file
    json_name = '/Users/Nozomi/files/news/dailynews/dailynews_{}{}-{}.json'.format(category, add_zero(start_id, 6), add_zero(end_id, 6))
    file = open(json_name, 'w', encoding='utf-8')

    # dictionary: {id: content} - saved as json
    all_dic = {}

    # scraping
    for article_id in range(int(start_id), int(end_id)):
        response = requests.get('https://www.dailynews.co.th/{}/'.format(category) + str(article_id))
        if response.status_code != 200:
            continue
        else:
            soup = BeautifulSoup(response.text, "html.parser")  # get html
            content = soup.find('article', id="news-article")
            if content == None:
                continue
            else:
                headline = content.find('h1', class_='title').text
                description = content.find('p', class_='desc').text
                article = '\n'.join([i.text for i in content.find('div', class_="entry textbox content-all").find_all('p') if i.text not in ['', '\xa0']])
                date = soup.find('meta', property="article:published_time").get('content')
                article_url = response.url
                id6 = '0'*(6-len(str(article_id))) + str(article_id) 
                
                all_dic[id6] = {"headline":headline, "description": description, "article":article, "date":date,
                "category":category, "url":article_url}
    json.dump(all_dic, file, indent=4, ensure_ascii=False)
    file.close()


def sanook(start_id, end_id):  # 6 digits
    # open json file
    json_name = '/Users/Nozomi/files/news/sanook/dailynews_{}-{}.json'.format(add_zero(start_id, 7), add_zero(end_id, 7))
    file = open(json_name, 'w', encoding='utf-8')

    # dictionary: {id: content} - saved as json
    all_dic = {}

    # scraping
    for article_id in range(int(start_id), int(end_id)):
        response = requests.get('https://www.sanook.com/news/' + str(article_id))
        if response.status_code != 200:
            continue
        else:
            soup = BeautifulSoup(response.text, "html.parser")  # get html
            content = soup.find('article', id="news-article")
            if content == None:
                continue
            else:
                headline = content.find('h1', class_='title').text
                description = content.find('p', class_='desc').text
                article = '\n'.join([i.text for i in content.find('div', class_="entry textbox content-all").find_all('p') if i.text not in ['', '\xa0']])
                date = soup.find('meta', property="article:published_time").get('content')
                article_url = response.url
                id6 = '0'*(6-len(str(article_id))) + str(article_id) 
                
                all_dic[id6] = {"headline":headline, "description": description, "article":article, "date":date,
                "category":category, "url":article_url}
    json.dump(all_dic, file, indent=4, ensure_ascii=False)
    file.close()