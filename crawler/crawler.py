from bs4 import BeautifulSoup
import requests

# #CRAWLING THE GUARDIAN BUSINESS TAB

#request guarding business tab URL
url = "http://www.theguardian.com/uk/business"

#extracting data from the request
r = requests.get(url) #request sto url tou guardian

data = r.text

#parse the data using BeautifulSoup
soup = BeautifulSoup(data, "html.parser")

#extract list of articles from the soup object
arr = soup.select('#tabs-popular-1 > ul > li > a')

#create a list of article links
links = [ article["href"] for article in arr ]

#create an empty list to store article bodies
articles1 = []

#iterate over links, extract article body, and append to list of articles
for link in links:
    r  = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")
    body = " ".join([ p.text for p in soup.select("#maincontent > div > p") ])
    import re
    reg = re.compile(r'[.,\-"“(]\'’–')
    reg = reg.sub(" ", body).split(" ")
    articles1.append(" ".join(reg))






#CRAWLING NBC NEWS BUSINESS TAB
url = "https://www.nbcnews.com/business"

#request to the NBC News url
r  = requests.get(url) 

#extracting data from the request
data = r.text

#parse the data using BeautifulSoup
soup = BeautifulSoup(data, "html.parser")
arr = soup.select('#content > div:nth-child(7) > div > div.fullWidth.layout-grid-container.layout-index-1 > div > section.pkg.multiUp.multiUp--fourUp.pkg-index-6.multi-up__four-up > div.multi-up__content > div > div > article > div.tease-card__picture > a')
arr2 = soup.select("#content > div:nth-child(7) > div > div.fullWidth.layout-grid-container.layout-index-1 > div > section.pkg.multiUp.multiUp--fourUp.pkg-index-8.multi-up__four-up > div.multi-up__content > div > div > article > div.tease-card__picture > a")

#create a list of article links
links1 = [ article["href"] for article in arr ]
links2 = [ article["href"] for article in arr ]

#combine lists of links
links = links1 + links2

#create an empty list to store article bodies
articles2 = []

#iterate over links, extract article body, and append to list of articles
for link in links:
    r  = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")
    body = " ".join([ p.text for p in soup.select("#content > div:nth-child(7) > div > div > article > div > div.article-body__section.layout-grid-container.article-body__last-section > div.article-body.layout-grid-item.layout-grid-item--with-gutter-s-only.grid-col-10-m.grid-col-push-1-m.grid-col-6-xl.grid-col-push-2-xl.article-body--custom-column > div > p") ])
    import re
    reg = re.compile(r'[.,\-"“(]\'’–')
    reg = reg.sub(" ", body).split(" ")
    articles2.append(" ".join(reg))

#combine articles from both sources
articles = articles2 + articles1


#import nltk library
import nltk


import pickle

#define closed class tags
closed_class_tags = [ "CD","CC","DT","EX","IN","ILS","MD","PDT","POS","PRP","PRP$","RP","TO","UH","WDT", "WP" ,"WP$","WRB"]

#create empty list to store tokenized articles
tokenised_articles = []
i = -1

#iterate over articles, tokenize and tag, and store open class pairs in pickled file
for  article in articles:
    i += 1

    #tokenize and tag article
    tokens = nltk.word_tokenize(article)
    tagged = nltk.pos_tag(tokens)

    #extract open class pairs
    open_class_pairs = []
    for pair in tagged:
        if not pair[1] in closed_class_tags:
            open_class_pairs.append(pair)

    #pickle open class pairs
    with open(f"./taged_articles/taged_article_{i}", "wb") as fp:   #Pickling
        pickle.dump(open_class_pairs, fp)

#unpickle tokenized articles and create a list of all tokens
import pickle
tokenised_articles = []
for i in range(18):
    with open(f"./taged_articles/taged_article_{i}", "rb") as fp:   # Unpickling
        b = pickle.load(fp)
        tokenised_articles.append(b)

            


 #import nltk library and PorterStemmer module
import nltk
from nltk.stem import PorterStemmer

#create PorterStemmer object
ps = PorterStemmer()

#create empty dictionary for reversed index
reversed_index_dict = {}

#create empty list to store stemmed articles
stemmed_articles = []

#iterate over tokenized articles, stem words, and append to list of stemmed articles
for article in tokenised_articles:
    stemmed_words = []
    for word in article:
        stemmed_words.append( ps.stem(word[0]))

    stemmed_articles.append(stemmed_words)

#create empty list to store frequency dictionaries for each stemmed article
freq_words_of_articles_list = []

#iterate over stemmed articles, create frequency dictionary, and append to list
for stemmed_article in stemmed_articles: 

    #create frequency dictionary
    freq_dict = dict(nltk.FreqDist(stemmed_article))

    #normalize frequency dictionary by dividing each value by the length of the dictionary
    for word in freq_dict: 
        freq_dict[word] = freq_dict[word] / len(freq_dict)

    #append frequency dictionary to list
    freq_words_of_articles_list.append(freq_dict)

#create list of unique words in stemmed articles
unique_words = list(set(sum(stemmed_articles, [])))

reversed_index_dict = {}

#iterate over unique words and create reversed index dictionary
for unique_word in unique_words:

    #create list of article ids containing the unique word
    article_ids =  [ i for i, article in enumerate(stemmed_articles) if unique_word in article]

    #create list of id/weight pairs for each article containing the unique word
    id_weight_pairs_list = [{"id": id, "weight": freq_words_of_articles_list[id][unique_word]} for id in article_ids]

    #add entry to reversed index dictionary for the unique word
    reversed_index_dict[unique_word] = { "article_ids": article_ids, "weights_per_article": id_weight_pairs_list }

#dump reversed index dictionary to json file
import json
reversed_index_dict_string = json.dumps(reversed_index_dict)
with open("reversed_index.json" , "w") as outfile:
    outfile.write(reversed_index_dict_string)

#load reversed index dictionary from json file
import json
with open("reversed_index.json") as json_file:
    reversed_index_dict = json.load(json_file)

#prompt user for search term and stem search term
import time
search_term = input("Enter a search term: ")
start = time.time()
from nltk.stem import  PorterStemmer

#create PorterStemmer object
ps = PorterStemmer()

#stem search term
stemmed_words = []
for word in search_term.split(" "):
    stemmed_words.append( ps.stem(word))

#search reversed index dictionary for stemmed words and create list of matching article ids
[ id  for id in reversed_index_dict[word]["weights_per_article"] for word in stemmed_words ]

#create empty dictionary to store scores for each matching article
scored_articles = {}

#iterate over stemmed words and update scores for matching articles
for word in stemmed_words:
    for document in reversed_index_dict[word]["weights_per_article"]:
        if not f"{document['id']}" in scored_articles:
            scored_articles[f"{document['id']}"] = 0
        scored_articles[f"{document['id']}"] += float(document['weight'])

#print scored articles
print(scored_articles)

#calculate search time
end=time.time()
search_time = end - start
print(search_time)