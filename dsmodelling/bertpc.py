from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import json

f = open("sample.json", encoding="utf8")
sample = json.load(f)
f.close()

# Adding stopwords from json file
with open("smart-stop-words.json", "r") as f:
    stopwords_data = json.load(f)

# adding stopwords to vectorizer model
vectorizer_model = CountVectorizer(stop_words=stopwords_data)

topic_model = BERTopic(
    vectorizer_model=vectorizer_model,  # added it to the model
    nr_topics=5,
    calculate_probabilities=True,
    verbose=True,
)
topics, probs = topic_model.fit_transform(sample)

print(topic_model.get_topic_info())
