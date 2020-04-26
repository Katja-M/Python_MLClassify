# Import for FrequencySummarizer class
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest

# Import for Classification
from languageprocessing import FrequencySummarizer
from parsewebsites import *
import urllib.request
from bs4 import BeautifulSoup
import requests

# For later
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans

# Classify a newspaper article into a technical article or non technical article
# Using the k-nearest neighbor algorithm

# 1. Create a corpus of news articles which are already classified into tech and non-tech
# 1a) Download all technews articles from NYT and Washington Post and label them as tech articles
# 1b) Download all sport articles from NYT and Washington Post and label them as non-tech articles

# URLs we want to download articles from
urlWashingtonPostNonTech = 'https://www.washingtonpost.com/sports'
urlNewYorkTimesNonTech = 'https://www.nytimes.com/pages/sports/index.html'
urlWashingtonPostTech = 'https://www.washingtonpost.com/business/technology'
urlNewYorkTimesTech = 'http://www.nytimes.com/pages/technology/index.html'

# This function will download all the article that are linked to a particular section of the newspaper
# Download all tech and non tech articles from the Washington Post
# Output: Dictionary with key: url value: text body
washingtonPostTechArticles = scrapeSource(urlWashingtonPostTech, '2020',getWashPostText, 'article')
washingtonPostNonTechArticles = scrapeSource(urlWashingtonPostNonTech, '2020',getWashPostText, 'article')
# Download all tech and non tech articles from the New York Times
# NYT does not require a token
newYorkTimesTechArticles = scrapeSource(urlNewYorkTimesTech, '2020',getNYTText, None)
newYorkTimesNonTechArticles = scrapeSource(urlNewYorkTimesNonTech, '2020',getNYTText, None)

# Setting up training data set for tech articles
# The training data set is set up as tuples (article, label)
articleSummaries = {}
# Each article is represented by a feature vector. The feature vector  is the most important words in the article
# The for loop helps to mark an article as tech article
for techUrlDictionary in [newYorkTimesTechArticles, washingtonPostTechArticles]:
    for articleUrl in techUrlDictionary:
        # Check whether article contains a body of text
        if len(techUrlDictionary[articleUrl][0]) > 0:
            # Finding the most important 25 words for each of the article
            fs = FrequencySummarizer()
            # extractFeatures() computes the frequency of the words and will return the top 25 words
            summary = fs.extractFeatures(techUrlDictionary[articleUrl],25)
            # Representing each article in a dictionary with the feature-vector and the assigned the label 'tech'
            articleSummaries[articleUrl] = {'feature-vector': summary,
                                            'label': 'Tech'}
# Setting up the training set for non tech articles
# Each article is represented by a feature vector. The feature vector  is the most important words in the article/
# The for loop helps to mark an article as non-tech article
for nontechUrlDictionary in [newYorkTimesNonTechArticles, washingtonPostNonTechArticles]:
    for articleUrl in nontechUrlDictionary:
        if len(nontechUrlDictionary[articleUrl][0]) > 0:
            # Finding the most important 25 words for each of the article
            fs = FrequencySummarizer()
            # extractFeatures() computes the frequency of the words and will return the top 25 words
            summary = fs.extractFeatures(nontechUrlDictionary[articleUrl],25)
            # # Representing each article in a dictionary with the feature-vector and the assigned the label 'non-tech'
            articleSummaries[articleUrl] = {'feature-vector': summary,
                                            'label': 'Non-Tech'}

# 2. Get a new problem instance from a blog - an article that needs to be classified
def getDoxyDonkeyText(url, token):
    # Downloading the content of the url
    # request = urllib.request.Request(url)
    # response = urllib.request.urlopen(request)
    response = requests.get(url)
    soup = BeautifulSoup(response.content)

    page = str(soup)
    # Finding the title of the article
    title = soup.find('title').text
    # Fiinding text that is enclosed in that article
    mydivs = soup.findAll('div',{"class": token})
    text = ''.join(map(lambda p: p.text, mydivs))
    # Test instance is set up as tuple (title, text), just like our training data
    return text, title

testurl = 'http://doxydonkey.blogspot.in'
testArticle = getDoxyDonkeyText(testurl, 'post-body')
# Instantiate a Frequency Summarizer in order to extract the 25 most important words for this article
fs = FrequencySummarizer()
testArticleSummary = fs.extractFeatures(testArticle, 25)

# 3. Use the K-Nearest Neighbours algorithm to classify the test instance
    # Represent each articles as a vector of the 25 most important words in an articles by using natural language processing
    # The distance between the articles is calculated using the number of important words they have in common
    # Find the K-nearest neighbours and carry out a majority vote of those

# Goal: Finding similarities between the test article and all articles in a corpus
# Similarity = Number of important words two vectors have in common

# In the dicitionary similarities, we will keep adding of 
# what is the distance between our test instance and each of the articles in our training data
similarities = {}

for articleUrl in articleSummaries:
    oneArticleSummary = articleSummaries[articleUrl]['feature-vector']
    similarities[articleUrl] = len(set(testArticleSummary)).intersection(set(oneArticleSummary))

    # The dict labels will have as keys: label, ie Tech or Non-Tech and values: how many of the nearest neighbors are tech or non-tech
    labels = defaultdict(int)
    # Get of list of the 5 nearest neighbours which have the most words in common with the test instance
    knn = nlargest(5, similarities, key = similarities.get)

    # Return the label that most of the nearest neighbbor belong to
    for oneNeighbor in knn:
        labels[articleSummaries[oneNeighbor]['label']] += 1
    # Label with the maximum number of words is assigned to article
    print(nlargest(1, labels, key = labels.get))

print('The end')