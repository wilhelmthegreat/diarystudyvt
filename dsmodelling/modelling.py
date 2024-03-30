import nltk
from nltk.text import Text
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
class processor:
    stpw = nltk.corpus.stopwords.words('english')
    def word_cloud(self, text, num):
        words = tokenizer.tokenize(text)
        words = [w for w in words if w.lower() not in self.stpw]
        wordDist = nltk.FreqDist(words)
        return(wordDist.most_common(num))
    def add_stop_words(self, word):
        self.stpw.append(word)
    def associated_word_cloud(self, text, word, num):
        txt = Text(tokenizer.tokenize(text))
        con_list = txt.concordance_list(word, width=40)
        acc = list()
        for line in con_list:
            acc+=line.left
            acc+=line.right
        words = [w for w in acc if w.lower() not in (self.stpw+[word])]
        wordDist = nltk.FreqDist(words)
        return(wordDist.most_common(num))