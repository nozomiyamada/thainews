import requests
from bs4 import BeautifulSoup
import json, re

category_list = ['politics', 'regional', 'entertainment', 'economic', 'crime', 'foreign', 'royalnews',
'women', 'education', 'bangkok', 'it', 'agriculture', 'sports']

"""
HOW TO USE

thairath(start_id, end_id)
dailynews(start_id, end_id, category)
"""

class NewsScrape:
    def __init__(self, url:str, publisher:str):
        self.url = url
        self.publisher = publisher

    def request(self, article_id:int):   
        request_url = self.url + str(article_id)
        try:
            response = requests.get(request_url, timeout=(12.0, 20.0))
        except:
            return None, None
        if response.status_code != 200:
            return None, None
        return BeautifulSoup(response.text, "html.parser"), response.url 

    def dic_thairath(self, soup, article_id:int):
        content_list = soup.find_all('script', type="application/ld+json")
        if content_list == []:
            return None
        try:
            content_dic = json.loads(content_list[-1].text)
        except:
            return None
        dic = {
            'headline':content_dic['headline'],
            'description':content_dic['description'],
            'article':content_dic['articleBody'],
            'date':content_dic['datePublished'],
            'id':article_id,
            'url':content_dic['mainEntityOfPage']['@id']}
        return dic

    def dic_matichon(self, soup, article_id:int, article_url):
        if soup.find('article') == None:
            return None
        headline = soup.find('h1', class_="entry-title").text
        article = '\n'.join([i.text for i in soup.find('article').find_all('p') if i.text not in ['', '\xa0']])
        date = soup.find('article').find('time').get('datetime')
        category = article_url.split('/')[-2]
        dic = {
            "headline":headline,
            "article":article,
            "date":date,
            "category":category,
            "url":article_url,
            "id":article_id
            }
        return dic
    
    def dic_dailynews(self, soup, article_id, article_url):
        content = soup.find('article', id="news-article")
        if content == None:
            return None   
        headline = content.find('h1', class_='title').text
        description = content.find('p', class_='desc').text
        article = '\n'.join([i.text for i in content.find('div', class_="entry textbox content-all").find_all('p') if i.text not in ['', '\xa0']])
        category = soup.find('ol', class_="breadcrumb").find_all('a')[-1].text
        date = content.find('span', class_="date").text  
        dic = {
            "headline":headline,
            "description":description,
            "article":article,
            "date":date,
            "category":category,
            "id":article_id
            }
        return dic

    def dic_sanook(self, soup, article_id):
        data = soup.find_all('script',type="application/ld+json")
        if data == []:
            return None
        try:
            data = json.loads(data[-1].text)
        except:
            return None
        dic = {
            "headline":data['headline'], 
            "article":data['articleBody'], 
            "date":data['datePublished'],
            "author":data['author']['name'],
            "url":data['mainEntityOfPage']['@id'],
            "id":article_id}
        return dic

    def save_json(self, start_id:int, end_id:int):
        all_list = []
        for article_id in range(start_id, end_id):
            soup, article_url = self.request(article_id)
            if soup == None:
                continue
            elif self.publisher == 'thairath':
                dic = self.dic_thairath(soup, article_id)
            elif self.publisher == 'matichon':
                dic = self.dic_matichon(soup, article_id, article_url)
            elif self.publisher == 'dailynews':
                dic = self.dic_dailynews(soup, article_id, article_url)
            elif self.publisher == 'sanook':
                dic = self.dic_sanook(soup, article_id)
            if dic != None:
                all_list.append(dic)

        with open('/Users/Nozomi/news/{0}/{0}{1}-{2}.json'.format(self.publisher, start_id, end_id), 'w', encoding='utf-8') as f:
            json.dump(all_list, f, indent=4, ensure_ascii=False)


### assign methods to functions ###
__tr = NewsScrape(url='https://www.thairath.co.th/content/', publisher='thairath')
thairath = __tr.save_json

__mc = NewsScrape(url='https://www.matichon.co.th/news/', publisher='matichon')
matichon = __mc.save_json

__dn = NewsScrape(url='https://www.dailynews.co.th/bangkok/', publisher='dailynews')
dailynews = __dn.save_json

__sn = NewsScrape(url='https://www.sanook.com/news/', publisher='sanook')
sanook = __sn.save_json