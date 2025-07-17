import pymupdf
import json
import torch
from transformers import pipeline
import spacy
import re
from collections import Counter



def extract_abstract_from_pdf(doc, max_pages=2):
    """
    Extracts the abstract from a scientific PDF using PyMuPDF and improved heuristics.
    
    Args:
        doc (pymudf.document) : Doc to extract abstract from.
        max_pages (int): Number of initial pages to search for abstract.
        
    Returns:
        str: The extracted abstract or a message if not found.
    """
    text = ""
    
    for page_num in range(min(max_pages, len(doc))):
        text += doc[page_num].get_text()

    text = text.replace('\r', '\n')

    if text:
      # print(text)
      return text
    else:
      return "Abstract not found or couldn't be reliably extracted."


    # Updated pattern: capture Abstract followed by multiple lines, stopping at known section titles
    # pattern = re.compile(
    #     r"(?:^|\n)(?:abstract|ABSTRACT)\s*[:\n]*\s*(.*?)"
    #     r"(?=\n(?:\s{0,4}[1-9][\.\s]|introduction|keywords|background|methods|related work)[^\n]{0,80}\n)",
    #     re.IGNORECASE | re.DOTALL
    # )

    # match = pattern.search(text)
    # if match:
    #     abstract = match.group(1).strip()
    #     print(abstract)
    #     return abstract
    # else:
    #     return "Abstract not found or couldn't be reliably extracted."

def extractEntitiesFromAbstract(abstract):
  nlp = spacy.load("en_core_sci_sm")
  spacy_doc = nlp(abstract)

  entList = []

  for ent in spacy_doc.ents:
    entList.append(ent.text)

  return entList


def extractText(doc):

  deviceToUse = 0 if torch.cuda.is_available() else -1

  nlp = spacy.load("en_core_sci_sm")
  re_pipeline = pipeline("text2text-generation", model="Babelscape/rebel-large", device=deviceToUse)


  text = ""
  
  for page in doc:
      text += page.get_text()

  text = text.replace('\r', '\n')

  spacy_doc = nlp(text)

  entList = []
  for ent in spacy_doc.ents:
    entList.append(ent.text)


  # with open("outputs/output_json.json", "w") as file:
  #   json.dump(entList, file)

  sor_list = [] #sub-obj-relation list

  for sent in spacy_doc.sents:
    output = re_pipeline(sent.text)
    split_sentence = output[0]['generated_text'].split("  ")
    if len(split_sentence) == 3:
      sor_list.append(split_sentence)
      # print(split_sentence)
    elif len(split_sentence) > 3:
        multiple_sor_list = [split_sentence[i:i+3] for i in range(0, len(split_sentence), 3)]
        for sorList in multiple_sor_list:
          sor_list.append(sorList)
          # print(sorList)


  # output = open("outputs/sor_list.json", "w")
  # json.dump(sor_list, output)
  return sor_list





def getDistinctEntities(data):

  count = Counter(data)
  count = count.most_common(30)
  # print(count.keys())

  distinctEnts = [i for i, _ in count]

  # with open("outputs/top_distinct_ents.json", "w") as file:
  #   json.dump(distinctEnts, file)

  return distinctEnts
    
def preprocessEnts(data):

  pattern = re.compile(r"[^\x00-\x7F]+") 
  cleaned_ents = [re.sub(pattern, "", ent).replace("\n", "") for ent in data]

  output = open("outputs/cleaned_ents_from_abstract.json", "w")
  json.dump(cleaned_ents, output)

  return cleaned_ents

def filterImpRelations(allRelations, impEnts):
  impRelations = []

  for relation in allRelations:
    if len(relation) == 3 and (relation[0] in impEnts or relation[1] in impEnts):
      if relation not in impRelations:
        impRelations.append(relation)

  # output = open("outputs/imp_sor_list.json", "w")
  # json.dump(impRelations, output)

  return impRelations


# extractEntitiesFromAbstract()
# # print(extract_abstract_from_pdf("testPdf.pdf"))
# extractText()
# getDistinctEntities()
# preprocessEnts()

# filterImpRelations()

""" Run createNetwork.py to visualize the relations """