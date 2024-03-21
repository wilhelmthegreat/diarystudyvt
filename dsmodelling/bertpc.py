from bertopic import BERTopic
import json

f = open('sample.json', encoding='utf8')
sample= json.load(f)
f.close()

topic_model = BERTopic()
topics, probs = topic_model.fit_transform(sample)

print(topic_model.get_topic_info())