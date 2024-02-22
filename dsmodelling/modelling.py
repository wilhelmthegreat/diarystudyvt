import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
def wordcloud(text):
    words = nltk.tokenize.word_tokenize(text)
    stopwords = nltk.corpus.stopwords.words('english')
    wordDist = nltk.FreqDist(w.lower() for w in words if w not in stopwords)
    return(wordDist.most_common(num))