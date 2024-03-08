import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
class processor:
    stpw = list()
    def word_cloud(self, text, num):
        words = tokenizer.tokenize(text)
        stopwords = nltk.corpus.stopwords.words('english') + self.stpw
        wordDist = nltk.FreqDist(w for w in words if w.lower() not in stopwords)
        return(wordDist.most_common(num))
    def add_stop_words(self, word):
        self.stpw.append(word)