from news import *

# all contents of Thairath are https://www.thairath.co.th/content/******* (7digits)

def scrape(start_id, end_id):
    
    json_name = '/Users/Nozomi/files/news/thairath/json/thairath0{}-0{}.json'.format(start_id, end_id)

    file = open(json_name, 'w', encoding='utf-8')

    all_dic = {}

    for article_id in range(start_id, end_id):
        response = requests.get('https://www.thairath.co.th/content/' + str(article_id))  # get html
        if response.status_code == 200:  # if 404 pass
            soup = BeautifulSoup(response.text, "html.parser")  # get text

            # find more than 2 tags <script>
            content_list = soup.find_all('script', type="application/ld+json")

            # convert final one from json into dict
            try:
                content_dic = json.loads(content_list[-1].text)
            except IndexError:
                continue  # no content -> skip to next id
            
            if len(str(article_id)) < 7: # make all id have 7 digits  e.g. 123 -> 0000123
                id7 = '0'*(7-len(str(article_id)))+str(article_id)
            else:
                id7 = str(article_id)

            all_dic[id7] = {'headline':content_dic['headline'], 'description':content_dic['description'],
            'article':content_dic['articleBody'], 'date':content_dic['datePublished'], 'url':content_dic['mainEntityOfPage']['@id']}
    
    json.dump(all_dic, file, indent=4, ensure_ascii=False)
    file.close()