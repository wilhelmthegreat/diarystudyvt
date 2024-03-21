from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups
import json

f = open('sample.json', encoding='utf8')
txt = json.load(f)
f.close()

topic_model = BERTopic()
topics, probs = topic_model.fit_transform(txt)

print(topic_model.get_topic_info())