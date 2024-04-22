import json
from gensim import corpora
from gensim.models import LdaModel
from gensim.parsing.preprocessing import preprocess_string
import pyLDAvis
import pyLDAvis.gensim
import nltk

tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
stopwords = nltk.corpus.stopwords.words('english')

def preprocess(text):
    return preprocess_string(text)

# Have a function that receives a list of texts and returns the LDA model
def lda_model(texts: list[str], num_topics=10, passes=15) -> list[LdaModel, list[tuple[list[tuple[int, int]]]], corpora.Dictionary]:
    processed_texts = [preprocess(text) for text in texts]
    dictionary = corpora.Dictionary(processed_texts)
    corpus = [dictionary.doc2bow(text) for text in processed_texts]
    return LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=passes), corpus, dictionary

def lda_visualization_html(lda_model: LdaModel, corpus: list[tuple[int, int]], dictionary: corpora.Dictionary):
    vis_data = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary)
    return pyLDAvis.prepared_data_to_html(vis_data)

