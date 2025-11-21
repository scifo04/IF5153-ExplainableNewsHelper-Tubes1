import json
import pandas as pd
import re
import numpy as np

with open("added_column_from_prompt.json", "r", encoding="utf-8") as f:
    data = json.load(f)

ner_json_list = data[0]
summary_json_list = data[1]

ner_list = []
summary_list = []

for ner in ner_json_list:
    ner_list.append(json.loads(ner['answer']))

for i, summary in enumerate(summary_json_list):
    summary_list.append(summary['answer'])

df = pd.read_csv("../scraper/investor_articles_full.csv")

df["body_text"] = df["body_text"].apply(
    lambda x: re.sub(r"^[^—–-]*[—–-]\s*", "", x)
)

df['ner'] = ner_list
df['summary'] = summary_list

df.to_csv('investor_articles_with_ner_and_summaries.csv', index=False)