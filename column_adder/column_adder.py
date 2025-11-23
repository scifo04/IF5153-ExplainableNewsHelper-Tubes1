import json
import pandas as pd
import re

with open("added_data_from_prompts_new.json", "r", encoding="utf-8") as f:
    data = json.load(f)

ner_json_list = data[0]
summary_json_list = data[1]

ner_list = []
summary_list = []

for ner in ner_json_list:
    print(ner['prompt'])
    ner_list.append(json.loads(ner['answer']))

for i, summary in enumerate(summary_json_list):
    summary_list.append(summary['answer'])

df = pd.read_csv("../scraper/final_dataset.csv")

df['ner'] = ner_list
df['summary'] = summary_list

df.to_csv('final_processed_dataset.csv', index=False)