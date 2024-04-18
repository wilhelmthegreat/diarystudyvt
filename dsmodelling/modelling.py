import nltk
from nltk.text import Text
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from dsmodelling import textrank_algorithm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

#Download NLTK libraries
nltk.download('punkt', download_dir='./cache')
nltk.download('wordnet', download_dir='./cache')
nltk.download('omw-1.4', download_dir='./cache')
nltk.download('stopwords', download_dir='./cache')
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
aitokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
def _dist_to_dict(l):
    return([{'text': s[0], 'value': s[1]} for s in l])
stopwords = nltk.corpus.stopwords.words('english')
#Generates frequency distribution object to be used in a word cloud
def word_cloud(text, stpw, num):
    words = tokenizer.tokenize(text)
    words = [w for w in words if w.lower() not in (stopwords+stpw)]
    wordDist = nltk.FreqDist(words)
    distObj = wordDist.most_common(num)
    return(_dist_to_dict(distObj))
#Generates distribution to be used in a word cloud based on both frequency and proximity to a chosen word
def associated_word_cloud(text, words, stpw, num=12):
    txt = Text(tokenizer.tokenize(text))
    acc = list()
    for word in words:
        con_list = txt.concordance_list(word, width=40)
        for line in con_list:
            acc+=line.left
            acc+=line.right
    newWords = [w for w in acc if w.lower() not in (stopwords+stpw+words)]
    wordDist = nltk.FreqDist(newWords)
    distObj = wordDist.most_common(num)
    return(_dist_to_dict(distObj))
#Gets a list of user entries with no keyword to search for and generates the most characteristic/important sentence for each one
def get_sentence_no_word(e):
    return(textrank_algorithm.get_best_sentence(e))
#Gets a list of user entries with a keyword to search for and shows the context in which the word was used if it's present and just shows the most characteristic sentence if not present.
def get_sentence(e, wrds):
        tokens = tokenizer.tokenize(e)
        if (len(set(wrds).intersection(set(tokens))) > 0):
            return(textrank_algorithm.get_best_sentence_from_word(e, wrds))
        else:
            return(textrank_algorithm.get_best_sentence(e))
#Analyzes the sentiment of a user post and rates it from -1 being very negative to 1 being very positive
def sentiment(t):
    tkns = aitokenizer(t, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**tkns)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
    base_values = probabilities[0].tolist()
    return(round((base_values[1]-base_values[0])*100)/100)
def word_count(t):
    return(len(tokenizer.tokenize(t)))