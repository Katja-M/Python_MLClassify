# Import for FrequencySummarizer class
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest

# Import for Classification
import urllib.request
from bs4 import BeautifulSoup

# For later
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Frequency summarizer class
# Input: title, article - body

class FrequencySummarizer:
    # Class constructor 
    def __init__(self, min_cut = 0.1, max_cut = 0.9):
        self._min_cut = min_cut
        self._max_cut = max_cut
        # Defining a SET, not a list, of stopwords
        # In a set, there is no order
        self._stopwords = set(stopwords.word('english') + list(punctuation) + [u"'s", '"'])
    
    # member function
    def _compute_frequencies(self, word_sent, customStopWords = None):
        # Dictionaries with key: word and value: frequency
        freq = defaultdict(int)
        
        if customStopWords is None:
            stopwords = set(self._stopwords)
        else:
            stopwords = set(customStopWords).union(self._stopwords)
        for sentence in word_sent:
            for word in sentence:
                # If the word is not a stopword...
                if word not in stopwords:
                    #...we will increment its frequency
                    freq[word] += 1

        # Normalizing the frequency of all the words
        m = float(max(freq.values()))
        for word in freq.keys():
            freq[word] = freq[word]/m
            # Checking if the frequency is between the min and max cutoffs, which were defined earlier
            if freq[word] >= self._max_cut or freq[word] <= self._min_cut:
                # Deleting the word if beyond cutlines
                del freq[word]
        return freq

    def extractFeatures(self, article, n, customStopWords = None):
        # The arcticle is given as a tuple (text, title)
        text = article[0]
        title = article[1]
        # Split text into sentences
        sentences = sent_tokenize(text)
        # Split sentences into words
        word_sent = [word_tokenize(s.lower() for s in sentences)]
        # Calculate the word frequencies using the member function above
        self._freq = self._compute_frequencies(word_sent, customStopWords)
        if n < 0:
            # If the user has asked for a negative number, it means, that we return all features
            # ie no feature selection beyond simply picking words as the features
            return nlargest(len(self._freq_keys()), self._freq, key = self._freq.get)
        else:
            # If the calling function has asked for a subset then return only the 'n' largest features
            # ie. the most important words (important = frequent; not considering stopwords)
            return nlargest(n, self._freq, key = self._freq.get)

    def extractRawFrequencies(self, article):
        # This method only returns the raw frequencies, i.e. litterally only the word count
        # No normalizing and no filtering out
        text = article[0]
        title = article[1]
        
        sentences = sent_tokenize(text)
        word_sent = [word_tokenize(s.lower() for s in sents)]
        freq = defaultdict(int)
        for s in word_sent:
            for word in s:
                if word not in self._stopwords:
                    freq[word] += 1
        return freq

    def summarize(self, article, n):
        # Summarizes the n most important sentences
        text = article[0]
        title = article[1]

        sentences = sent_tokenize(text)
        word_sent = [word_tokenize(s.lower()) for s in sentences]
        self._freq = self._compute_frequencies(word_sent)

        # Ranking will save the score for each sentence in word_sent
        ranking = defaultdict(int)

        #Iterating through each of theses sentencences...
        for i, sentence in enumerate(word_sent):
            # Iterating through each word in each sentences and ...
            for word in sentence:
                if word in self._freq:
                    # ...assigning a score to sentence i if a word of that sentence
                    # is in the dictionary self._freq
                    ranking[i] += self._freq[word]
            
            sentences_index = nlargest(n, ranking, key = ranking.get)
            # The sentences that are returned can be used as a feature vector
            return [sentences[j] for j in sentences_index]

# Classify a newspaper article into a technical article or non technical article
# Using the k-nearest neighbor algorithm
# Also sentiment analysis and how it can be seen as a special case of a classification problem

# 1. Create a corpus of news articles which are already classified into tech and non-tech
# 1a) Download all technews articles from NYT and Washington Post and label them as tech articles
# 1b) Download all sport articles from NYT and Washington Post and label them as non-tech articles

# Function that will scrape a webpage of the Washington Post
def getWashPostText(url, token):
    # This function takes the url of an article in the washington post and then returns the article minus all of the crud html, javascript etc.
    # Assumption: All articles in the WashPo are enclosed in <article></article> tags
    try:
        # Downloading the webpage
        page = urllib.request.urlopen(url).read().decode('utf8')
    except:
        return (None,None)
    
    # Use BeautifulSoup to remove all the div and tags that are present
    soup = BeautifulSoup(page)
    if soup is None:
        return(None, None)
    
    # Removing the hmtl divs/tags and get on string with text
    text = ''
    # By taking a token. This is a token in which between all the text of the article is kept
    # This is specific to the structure of the webpage that is parsed
    if soup.find_all(token) is not None:
        # Finding all the text between that token and mushes it together
        text = ''.join(map(lambda p: p.text, soup.find_all(token)))
        # Second soup because the structure of the WashingtonPost page is such that the article is enclosed within article tags
        # and there are paragraphs within the article which are enclosed in p tags.
        soup2 = BeautifulSoup(text)
        if soup2.find_all('p') is not None:
            # Takes all the p-tags within that text and mushes it all together
            # text should be one string with the text of the articles without any tags like article or p
            text = ''.join(map(lambda p: p.text, soup2.find_all('p')))
    # Return the text of the article and the title of the article as a tuple
    return text, soup.title.text

# Function that will scrape the NYT
def getNYTText(url, token):
    # Alternative way to get the contents of a URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    page = str(soup)
    title = soup.find('title').text

    # In the NYT, the article is contained within the tags story-body-text class
    mydivs = soup.findAll('p', {'class':'story-body-text story-content'})
    # Find all the all the text that is between p tags and smush it together to get one string
    text = ''.join(map(lambda p: p.text, mydivs))
    return text, title

# Function that takes in the URL of an entire section of a newspapers and parses all of the URLs linked off that section
# It returns all the corresponding articles of all the URLs of that section as a dictionary
# The function will use getWashPostText() and getNYTText()
def scrapeSource(url, magicFrag = '2020', scraperFunction = getNYTText, token = 'None'):
    # The scraperFunction is a website specific function in order to scrape that specific webpage
    # magicFrag: allows us to check URLs for dates

    # Setting up a soup for the section page to find all the links that are in that section page
    urlBodies = {}
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    soup = BeautifulSoup(response)

    # We will only consider URLs with a date line, i.e.
    # We need to check whether the URL contains a date
    # To do so, we will use the magicFrag argument
    numErrors = 0
    for a in soup.findAll('a'):
        try:
            # Links are always of the form <a href = 'link-url'> link-text </a>
            url = a['href']
            if( (url not in urlBodies) and ((magicFrag is not None and magicFrag in url) or magicFrag is None)):
                # Employing the website specific scraper function to download the article
                body = scraperFunction(url, token)

                if body and len(body > 0 ):
                    urlBodies[url] = body
        # Except block so that we can keep track of parsing errors
        except:
            numErrors += 1
        
        # Returns are dictionary with key: url and corresponding article title and value: text
        return urlBodies



# 3. Use the K-Nearest Neighbours algorithm to classify the test instance
    # Represent each articles as a vector of the 25 most important words in an articles by using natural language processing
    # The distance between the articles is calculated using the number of important words they have in common
    # Find the K-nearest neighbours and carry out a majority vote of those

# URLs we want to download articles from
urlWashingtonPostNonTech = 'https://www.washingtonpost.com/sports'
urlNewYorkTimesNonTech = 'https://www.nytimes.com/pages/sports/index.html'
urlWashingtonPostTech = 'https://www.washingtonpost.com/business/technology'
urlNewYorkTimesTech = 'http://www.nytimes.com/pages/technology/index.html'


# This function will download all the article that are linked to a particular section of the newspaper
# Download all tech and non tech articles from the Washington Post
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
def getDoxyDonkeyText(testUrl, token):
    # Downloading the content of the url
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
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
    testArticleSummary = fs.extractFeatures(testArtice, 25)

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
    nlargest(1, labels, key = labels.get)