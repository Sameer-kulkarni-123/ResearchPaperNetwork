import json
import re
from collections import Counter

def getDistinctEntities():
  with open("output_json.json", "r", encoding="utf-8") as file:
    data = json.load(file)


  # filtered_ents = set(ent for ent in data)

  count = Counter(data)
  print(count.keys())

  top_100_ents = [i for i in count.keys()]
  print(top_100_ents)

  with open("outputs/top_distinct_ents.json", "w") as file:
    json.dump(top_100_ents, file)
    
def preprocessEnts():
  with open("outputs/top_distinct_ents.json", "r") as file:
    data = json.load(file)

  pattern = re.compile(r"[^\x00-\x7F]+") 
  cleaned_ents = [re.sub(pattern, "", ent).replace("\n", "") for ent in data]

  print(cleaned_ents)
  output = open("outputs/cleaned_ents.json", "w")
  json.dump(cleaned_ents, output)

preprocessEnts()
