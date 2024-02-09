import nltk
def wordcloud(text):
    words = nltk.tokenize.word_tokenize(text, num)
    stopwords = nltk.corpus.stopwords.words('english')
    wordDist = nltk.FreqDist(w.lower() for w in words if w not in stopwords)
    return(wordDist.most_common(num))