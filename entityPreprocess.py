import json
from collections import Counter

with open("output_json.json", "r", encoding="utf-8") as file:
  data = json.load(file)


# filtered_ents = set(ent for ent in data)

count = Counter(data)
print(count.keys())

top_100_ents = [i for i in count.keys()]
print(top_100_ents)

with open("outputs/top_distinct_ents.json", "w") as file:
  json.dump(top_100_ents, file)