# -*- coding: utf-8 -*-
"""mrpc_bert.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ufpKydv03yWngPUBuHAb_xxZdc-refAt
"""

#!pip install transformers

#!pip install datasets

import transformers
import torch
import os
os.environ['CUDA_LAUNCH_BLOCKING'] = "1"

from datasets import load_dataset
from transformers import AutoTokenizer 
from transformers import DataCollatorWithPadding
from transformers import TrainingArguments
#from transformers import RobertaTokenizerFast, RobertaForSequenceClassification
from transformers import AutoModelForSequenceClassification
from transformers import Trainer

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

splits = ['train[:100]', 'validation[:100]' , 'test[:100]']

raw_datasets = load_dataset("glue", "mrpc", split=splits)

checkpoint = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(checkpoint, max_length = 512)



#train_encodings = tokenizer(train_texts, truncation=True, padding=True,max_length = 512)
#test_encodings = tokenizer(test_texts, truncation=True, padding=True,max_length = 512)

def tokenize_function(example):
   return tokenizer(example["sentence1"], example["sentence2"], truncation=True)
   
tokenized_train = raw_datasets[0].map(tokenize_function, batched=True)
  #tokenized_validation = raw_datasets[1].map(tokenize_function, batched=True)
tokenized_test = raw_datasets[2].map(tokenize_function, batched=True)
 
 

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

tokenized_train[0]

import numpy as np

#!pip install evaluate

import evaluate
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


# define accuracy metrics
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
}


#training_args = TrainingArguments("test-trainer", evaluation_strategy="epoch")

training_args = TrainingArguments(
    num_train_epochs=3,
    evaluation_strategy = "epoch",
    warmup_steps=100,
    weight_decay=0.01,
    logging_steps = 8,
    output_dir='/bert'
)


model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=2)

trainer = Trainer(
    model,
    training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.train()

