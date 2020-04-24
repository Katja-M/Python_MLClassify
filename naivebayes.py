# Naive Bayes classification needs to know the probability distribution of the words in the article
# Compute the frequency of the words in all tech articles and in all non tech articles
cumulativeRawFrequencies = {'Tech': defaultdict(int),
                            'Non-Tech': defaultdict(int)}
trainingData = {'Tech': nytTimesTechArticles, 'Non-Tech': nytTimesNonTechArticles}

for label in trainingData:
    for articleUrl in trainingData[label]:
        if len(trainingData[label][articleUrl]) > 0:
            fs = FrequencySummarizer()
            rawFrequencies = fs.extractRawFrequencies(trainingData[label][articleUrl])
            for word in rawFrequencies:
                # The frequency of each word that was found in articleUrl by the function extractRawFrequencies()
                # is now added to the total word frequencies respectively for each label
                cumulativeRawFrequencies[label][word] += rawFrequencies[word]
# Assumption: The probability of all words is indepent
# Formula: Techiness = P(Article is Tech/Words in Article) = P(Tech) *P(Word1/ Tech) * P(Word2/Tech)*.../P(Words in Article)

techiness = 1.0
nontechniness = 1.0

# Compute the techiness
for word in testArticleSummary:
    if word in cumulativeRawFrequencies['Tech']:
       # For each word in the test instance, multiply by the probability of this word being in a tech article
       techiness *= 1e3 * cumulativeRawFrequencies['Tech'][word] / float(sum(cumulativeRawFrequencis['Tech'].values())) 
    else:
        # If the word does not exist in tech - assign very low probability to avoid making the probability 0
        # Which would lead to a tech probability of zero right away
        techiness /= 1e3

    # Compute the non techiness
    if word in cumulativeRawFrequencies['Non-Tech']:
        nontechiness *= 1e3 * cumulativeRawFrequencies['Non-Tech'][word] / float(sum(cumulativeRawFrequencies['Non-Tech'].values()))
    else:
        nontechiness /= 1e3

# Scaling the techiness by probability of overall techiness
techiness *= float(sum(cumulativeRawFrequencies['Tech'].values())) / (float(sum(cumulativeRawFrequencies['Tech'].values())) + float(sum(cumulativeRawFrequencies['Non-Tech'].values())))
nontechiness *= float(sum(cumulativeRawFrequencies['Non-Tech'].values())) / (float(sum(cumulativeRawFrequencies['Tech'].values())) + float(sum(cumulativeRawFrequencies['Non-Tech'].values())))
if techiness > nontechiness:
    label = 'Tech'
else:
    label = 'Non-Tech'
print(label, techiness, nontechiness)

