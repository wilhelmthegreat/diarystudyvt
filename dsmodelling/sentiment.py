from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

text = "I hate programming!"
tokens = tokenizer(text, padding=True, truncation=True, return_tensors="pt")

with torch.no_grad():
    outputs = model(**tokens)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=1)

label_ids = torch.argmax(probabilities, dim=1)
labels = ['Negative', 'Positive']
label = labels[label_ids]
print(f"The sentiment is: {label}")