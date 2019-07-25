import requests
import csv
import json
import html
from bs4 import BeautifulSoup
import collections
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

"""
process of this program
1) get articles and headlines from Thairath
    (as many as possible & regardless of content for future works)
2) find articles that contains keyword (in this project, use 'countries')
3) supervised training with sk-learn
4) find words and metaphors that uniquely indicate the country

all process
1) scrape('thairath.tsv', 130000, 1000)
1) error_check ... 3 methods
    - column_check(open_tsv, num_of_row) 
        whether the number of column is correct  
    - print_content(open_tsv, id) 
        print one article by specifying id
    - delete_line(open_tsv, write_tsv, id) 
        delete one article

2) find_article(open_tsv, write_tsv, keyword, label)
2) count_label(open_tsv)

3) tokenize_all
3) tokenize_headline('country.tsv', 'headline.tsv', 0, 1000)

4) ml.train('headline.tsv', 1)
4) ml.evaluate('headline_test.tsv', 1)
4) get_features(0, 100)
"""

### 1. function for scraping ###

# all contents of Thairath are https://www.thairath.co.th/content/*******



def text_trim(text:str):
    text = html.unescape(text)
    text = text.replace('\t', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('\r', '')
    text = text.replace('\u200b', '')
    return text

def return_str(text):
    """
    return original text if any
    return '' if None
    (sometimes there is no content in certain keys of json)
    """
    if text is None:
        return ''
    else:
        return text_trim(text)

url = 'https://www.thairath.co.th/content/'

def scrape(start_id, end_id):
    """
    specify content id and the maximum number of request.get

    scrape(1000000, 100)
    >> save id, headline, description, article as json file

    get html, scrape with bs4, convert json to dict
    html structure is:

    <script type = "application/ld+json" async = "" class = "next-head">{
    "headline": "..."
    "description": "...."
    "articleBody": "....."
    .....
    }</script>

    ##note: all articles have the same structure "<script>...</script>" more than 2 times
    but always final one is the real content
    """
    json_name = '/Users/Nozomi/files/news/thairath/json/thairath0{}-0{}.json'.format(start_id, end_id)

    file = open(json_name, 'w', encoding='utf-8')

    all_dic = {}
    for article_id in range(start_id, end_id):
        response = requests.get(url + str(article_id))  # get html
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

            all_dic[id7] = content_dic
    
    json.dump(all_dic, file, indent=4, ensure_ascii=False)
    file.close()


# error check 1 (in case the number of columns are incorrect)
def column_check(open_tsv='thairath1.tsv', num_of_column=4):
    """
    the correct number of thairath.tsv is 4 (id, headline, description, article)
    the correct number of labeled tsv is 5 (id, headline, description, article, label)
    return the id and the incorrect number of columns

    column_check('thairath.tsv', 4)
    >> 1011000 5
    """
    with open(open_tsv, 'r', encoding='utf-8') as file:
        lines = csv.reader(file, delimiter='\t')
        for line in lines:
            if len(line) != num_of_column:
                print(line[0], len(line))  # print id of incorrect column


# error check 2 (specify how incorrect one incorrect)
def print_content(article_id, open_tsv='thairath1.tsv'):
    """
    print one article from id in order to check

    print_content('thairath.tsv', 1200000)
    >> 1200000
    >> headline
    >> description
    >> article
    """
    with open(open_tsv, 'r', encoding='utf-8') as file:
        lines = csv.reader(file, delimiter='\t')
        for line in lines:
            if line[0] == str(article_id):
                for i in range(len(line)):
                    print(i, line[i])
                    print('--------------------------------------')


# error check 3 (delete article)
def delete_line(open_tsv, write_tsv, id):
    """
    delete one line with ID
    """
    open_file = open(open_tsv, 'r', encoding='utf-8')
    write_file = open(write_tsv, 'w', encoding='utf-8')
    lines = list(csv.reader(open_file, delimiter='\t'))
    new_list = []
    for line in lines:
        if line[0] == str(id):
            pass
        else:
            new_list.append(line)

    # save as new tsv file
    writer = csv.writer(write_file, lineterminator='\n', delimiter='\t')
    writer.writerows(new_list)
    open_file.close()
    write_file.close()


### 2. function for find articles & save as tsv ###
def find_article(open_tsv, write_tsv, keyword, label):
    """
    find articles that contains keyword
    save as tsv with "label" for supervised learning

    keyword: "ญีปุ่น"
    article: "ประเทศญีปุ่นจัดงาน..."
    label: "JP"

    find_article('thairath.tsv', 'country.tsv', 'ญี่ปุ่น', 'JP')
    """
    open_file = open(open_tsv, 'r', encoding='utf-8')
    write_file = open(write_tsv, 'a', encoding='utf-8')  # append mode
    lines = csv.reader(open_file, delimiter='\t')

    # if article contains the keyword, add label and make new list of lists
    labeled_list = []
    for line in lines:
        description = line[2]
        article = line[3].strip('\n')
        if keyword in article or keyword in description:
            labeled_list.append(line + [label])

    # save as new tsv file
    writer = csv.writer(write_file, lineterminator='\n', delimiter='\t')
    writer.writerows(labeled_list)
    open_file.close()
    write_file.close()


def count_label(open_tsv):
    """
    open tsv file > tuple(id, headline, description, article, label)
    and print the number of each label

    count_tsv(country.tsv)
    >>[('JP', 3000), ('US', 2000), ('TH', 1000)]
    """
    ### open files ###
    file = open(open_tsv, 'r', encoding='utf-8')
    lines = csv.reader(file, delimiter='\t')

    ### make label list ###
    label_list = [line[-1] for line in lines]
    label_counter = collections.Counter()
    for label in label_list:
        label_counter[label] += 1
    print(label_counter)  # check the number of each label
    file.close()


### 4. function for train (need instance) ###
class ML:
    """
    method
    1: .train(train_tsv, target)
    2: .evaluate(test_tsv, target)
    3: .get_feature(label_index, top_k)

    target: 1 = headline, 2 = description, 3 = articlebody
    articlebody takes a lot of time (I gave up)

    instantiation: ml = ML()
    ml.train('headline.tsv', 1) > no printed result
    ml.evaluate('headline_test.tsv', 1) > print F score
    ml.get_feature(1, 30) > print top 30 of label 1
    """

    def __init__(self):
        self.model = LogisticRegression()
        self.dv = DictVectorizer()

    def train(self, train_tsv='headline.tsv', target=1):
        """
        train with tokenized data
        split tokenized data with '|'
        train target: headline...1, description...2, article...3
        """
        # make label list and feature dictionary
        file = open(train_tsv, 'r', encoding='utf-8')
        lines = csv.reader(file, delimiter='\t')

        label_list = []
        feat_dic_list = []
        for line in lines:
            word_list = line[target].split('|')
            # iff the first character is letter, add to feature dictionary
            feat_dic = {word: 1 for word in word_list if word != '' and word[0].isalpha()}
            feat_dic['LENGTH'] = len(word_list)  # length of sentence
            feat_dic_list.append(feat_dic)
            label_list.append(line[-1])

        # sparse matrix & train
        sparse_feature_matrix = self.dv.fit_transform(feat_dic_list)
        self.model.fit(sparse_feature_matrix, np.array(label_list))

    def get_feature(self, label_index, top_k):
        # get top k features of one label
        parameter_matrix = self.model.coef_
        top_features = parameter_matrix.argsort()[:, -(top_k) - 1:-1]
        label_top_features = [self.dv.get_feature_names()[x] for x
                            in top_features[label_index]]
        label_top_features.reverse()
        print(label_top_features)

    def evaluate(self, test_tsv, target):
        # the same way as train
        file = open(test_tsv, 'r', encoding='utf-8')
        lines = csv.reader(file, delimiter='\t')

        label_list = []
        feat_dic_list = []
        for line in lines:
            word_list = line[target].split('|')
            feat_dic = {word: 1 for word in word_list if word != '' and word[0].isalpha()}
            feat_dic['LENGTH'] = len(word_list)  # length of sentence
            feat_dic_list.append(feat_dic)
            label_list.append(line[-1])
        self.label_list = label_list

        # sparse matrix & test
        sparse_feature_matrix = self.dv.transform(feat_dic_list)
        self.result_list = self.model.predict(sparse_feature_matrix)

        # accuracy
        accuracy = accuracy_score(self.label_list, self.result_list)
        print("Accuracy")
        print(accuracy)

        # confusion matrix
        matrix = confusion_matrix(self.label_list, self.result_list)
        print("\nConfusion Matrix")
        print(matrix)

        # Precision, Recall, F score
        report = classification_report(self.label_list, self.result_list)
        print("\nReport")
        print(report)


# instantiation
ml = ML()