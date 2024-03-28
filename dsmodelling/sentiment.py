from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import json

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

dat = json.load(open("sample.json", encoding="utf8"))

sntmts = []
for entry in dat:
    tkns = tokenizer(entry, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**tkns)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
    base_values = probabilities[0].tolist()
    sntmts.append(round((base_values[1]-base_values[0])*100)/100)
print(sntmts)