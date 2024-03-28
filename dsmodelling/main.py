import matplotlib.pyplot as plt
import json
import nltk
from wordcloud import WordCloud, ImageColorGenerator

jsn = json.load(open(input("file containing json data: "), encoding="utf8"))

mode = input("which kind of visualization would you like?\n[1] Word Cloud\n[2] AI analysis plot\nSelection: ")

def pos_color (word, font_size, position, orientation, random_state=None, **kwargs):
    match nltk.pos_tag([word])[0][1]:
        case "NN":
            return "rgb(255,0,0)"
        case _:
            return "rgb(0,255,0)"

match mode:
    case "1":
        #wordcloud code
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('omw-1.4')
        nltk.download('stopwords')
        tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
        txt = '\n'.join(jsn)
        """stpw = list()
        stopwords = nltk.corpus.stopwords.words('english') + stpw
        words = [w for w in tokenizer.tokenize(txt) if w.lower() not in stopwords]
        wordDist = nltk.FreqDist(words)"""
        wc = WordCloud().generate_from_text(txt)
        plt.imshow(wc.recolor(color_func=pos_color, random_state=3), interpolation="bilinear")
        plt.axis('off')
        plt.show()
    case "2":
        #AI analysis code
        plt.plot([1,2,3,4], [1,4,9,16])
        plt.axis([0,6,0,20])
        plt.show()