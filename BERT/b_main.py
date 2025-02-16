import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_path = r'/Alexa 2.0/BERT/Intent-Recognition/trained_model'

tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
bert_model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)

intent_lable = {
    'AddToPlaylist': 0,
    'BookRestaurant': 1,
    'GetWeather': 2,
    'PlayMusic': 3,
    'RateBook': 4,
    'SearchCreativeWork': 5,
    'SearchScreeningEvent': 6
}

id_to_intent_label = {v: k for k, v in intent_lable.items()}


def preprocess_text(text, max_len=32):
    encoding = tokenizer(
        text,
        add_special_tokens=True,
        max_length=max_len,
        padding='max_length',
        truncation=True,
        return_tensors="pt"
    )
    return encoding['input_ids'], encoding['attention_mask']


def recognize_intent(text):
    input_ids, attention_mask = preprocess_text(text)
    with torch.inference_mode():
        outputs = bert_model(input_ids, attention_mask=attention_mask)

    logits = outputs.logits
    predicted_id = torch.argmax(logits, dim=1).item()
    input_lable = id_to_intent_label.get(predicted_id, 'Unknown Intent')

    return input_lable

# Tokenize a sample input
sample_text = "Hello, I am testing the model."


print("Output from the model:", recognize_intent(sample_text))



