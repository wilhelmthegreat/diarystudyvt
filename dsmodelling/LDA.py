import json
from gensim import corpora
from gensim.models import LdaModel
from gensim.parsing.preprocessing import preprocess_string

# Sample text data
with open("sample.json", "r") as json_file:
    texts = json.load(json_file)


# Preprocess the text
def preprocess(text):
    return preprocess_string(text)


# Apply preprocessing to texts
processed_texts = [preprocess(text) for text in texts]

# Create a dictionary representation of the documents
dictionary = corpora.Dictionary(processed_texts)

# Convert the dictionary into a bag-of-words corpus
corpus = [dictionary.doc2bow(text) for text in processed_texts]

# Train the LDA model
lda_model = LdaModel(corpus, num_topics=2, id2word=dictionary, passes=15)

# Get topics and their words
topics = []
for topic_id in range(lda_model.num_topics):
    words = [word for word, _ in lda_model.show_topic(topic_id)]
    topics.append(words)

# Save topics to a JSON file
topics_dict = {"topics": topics}
with open("topics.json", "w") as json_file:
    json.dump(topics_dict, json_file)

print("Topics saved to topics.json")
