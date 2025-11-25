import json
import pandas as pd
import re

with open("10.json", "r", encoding="utf-8") as f:
    data = json.load(f)

ner_json_list = data[0]
summary_json_list = data[1]

ner_list = []
summary_list = []

# le_empty = 0
# le_error = 0

# for ner in ner_json_list:
#     if (ner['answer'] == '[]'):
#         le_empty += 1
#     try:
#         json.loads(ner['answer'])
#     except:
#         le_error += 1

# print(le_empty)
# print(le_error)

le_error = []

for i, ner in enumerate(ner_json_list):
    try:
        if (ner['answer'] != '[]'):
            ner_list.append(json.loads(ner['answer']))
        else:
            le_error.append(i)
    except:
        le_error.append(i)

for i, summary in enumerate(summary_json_list):
    if (not i in le_error):
        summary_list.append(summary['answer'])

df = pd.read_csv("../scraper/final_dataset.csv")

df = df.drop(df.index[le_error])

df['ner'] = ner_list
df['summary'] = summary_list

df.to_csv('final_processed_dataset.csv', index=False)