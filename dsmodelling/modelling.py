import nltk
from nltk.text import Text
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import textrank_algorithm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

#Download NLTK libraries
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
aitokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
class processor:
    stpw = nltk.corpus.stopwords.words('english')
    def _dist_to_dict(self, l):
        acc = dict()
        for s in l:
            acc[s[0]] = s[1]
        return(acc)
    #Generates frequency distribution object to be used in a word cloud
    def word_cloud(self, text, num):
        words = tokenizer.tokenize(text)
        words = [w for w in words if w.lower() not in self.stpw]
        wordDist = nltk.FreqDist(words)
        distObj = wordDist.most_common(num)
        return(self._dist_to_dict(distObj))
    #Adds stop words to the class stop words field
    def add_stop_words(self, word):
        self.stpw.append(word)
    #Generates distribution to be used in a word cloud based on both frequency and proximity to a chosen word
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
    #Gets a list of user entries with no keyword to search for and generates the most characteristic/important sentence for each one
    def get_sentences_no_word(self, lst):
        result = [textrank_algorithm.get_best_sentence(e) for e in lst]
        return(result)
    #Gets a list of user entries with a keyword to search for and shows the context in which the word was used if it's present and just shows the most characteristic sentence if not present.
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
    #Analyzes the sentiment of a user post and rates it from -1 being very negative to 1 being very positive
    def sentiment(self, t):
        tkns = aitokenizer(t, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**tkns)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
        base_values = probabilities[0].tolist()
        return(round((base_values[1]-base_values[0])*100)/100)