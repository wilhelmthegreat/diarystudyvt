import nltk
from nltk.text import Text
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import textrank_algorithm
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
class processor:
    stpw = nltk.corpus.stopwords.words('english')
    def _dist_to_dict(self, l):
        acc = dict()
        for s in l:
            acc[s[0]] = s[1]
        return(acc)
    def word_cloud(self, text, num):
        words = tokenizer.tokenize(text)
        words = [w for w in words if w.lower() not in self.stpw]
        wordDist = nltk.FreqDist(words)
        distObj = wordDist.most_common(num)
        return(self._dist_to_dict(distObj))
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
        distObj = wordDist.most_common(num)
        return(self._dist_to_dict(distObj))
    def get_sentences(self, lst):
        result = [textrank_algorithm.get_best_sentence(e) for e in lst]
        return(result)
    def get_sentences(self, lst, wrd):
            result = []
            for e in lst:
                if (wrd in e):
                    conc = Text(tokenizer.tokenize(e)).concordance_list(wrd, width=40)
                    rslt = (' '.join(conc[0].left))+' '+wrd+' '+(' '.join(conc[0].right))
                    result.append(rslt)
                else:
                    result.append(textrank_algorithm.get_best_sentence(e))
            return result