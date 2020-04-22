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
            # ie not feature selection beyond simply picking words as the features
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
        #Iterating through each of theses sentencences and assign a score

        #!!! Understand member and class functions/variables


