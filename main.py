import pymupdf
import json
import torch
from transformers import pipeline
import spacy
import re
from collections import Counter



def extract_abstract_from_pdf(pdf_path, max_pages=2):
    """
    Extracts the abstract from a scientific PDF using PyMuPDF and improved heuristics.
    
    Args:
        pdf_path (str): Path to the PDF file.
        max_pages (int): Number of initial pages to search for abstract.
        
    Returns:
        str: The extracted abstract or a message if not found.
    """
    doc = pymupdf.open(pdf_path)
    text = ""
    
    for page_num in range(min(max_pages, len(doc))):
        text += doc[page_num].get_text()

    # Normalize spacing
    text = text.replace('\r', '\n')

    # Updated pattern: capture Abstract followed by multiple lines, stopping at known section titles
    pattern = re.compile(
        r"(?:^|\n)(?:abstract|ABSTRACT)\s*[:\n]*\s*(.*?)"
        r"(?=\n(?:\s{0,4}[1-9][\.\s]|introduction|keywords|background|methods|related work)[^\n]{0,80}\n)",
        re.IGNORECASE | re.DOTALL
    )

    match = pattern.search(text)
    if match:
        abstract = match.group(1).strip()
        return abstract
    else:
        return "Abstract not found or couldn't be reliably extracted."

def extractEntitiesFromAbstract():
  nlp = spacy.load("en_core_sci_sm")
  abstract = extract_abstract_from_pdf("testPdf.pdf")
  spacy_doc = nlp(abstract)

  entList = []

  for ent in spacy_doc.ents:
    entList.append(ent.text)

  with open("outputs/entities_from_abstract.json", "w") as file:
    json.dump(entList, file)


def extractText():

  deviceToUse = 0 if torch.cuda.is_available() else -1

  nlp = spacy.load("en_core_sci_sm")
  re_pipeline = pipeline("text2text-generation", model="Babelscape/rebel-large", device=deviceToUse)

  text = pymupdf.open("testPdf.pdf")

  full_text = ""

  for page in text:
    full_text += page.get_text()

  spacy_doc = nlp(full_text)

  entList = []
  for ent in spacy_doc.ents:
    entList.append(ent.text)


  with open("outputs/output_json.json", "w") as file:
    json.dump(entList, file)

  sor_list = [] #sub-obj-relation list

  for sent in spacy_doc.sents:
    output = re_pipeline(sent.text)
    split_sentence = output[0]['generated_text'].split("  ")
    if len(split_sentence) == 3:
      sor_list.append(split_sentence)
      print(split_sentence)
    elif len(split_sentence) > 3:
        multiple_sor_list = [split_sentence[i:i+3] for i in range(0, len(split_sentence), 3)]
        for sorList in multiple_sor_list:
          sor_list.append(sorList)
          print(sorList)


  output = open("outputs/sor_list.json", "w")
  json.dump(sor_list, output)





def getDistinctEntities():
  with open("outputs/output_json.json", "r", encoding="utf-8") as file:
    data = json.load(file)



  count = Counter(data)
  print(count.keys())

  top_100_ents = [i for i in count.keys()]
  print(top_100_ents)

  with open("outputs/top_distinct_ents.json", "w") as file:
    json.dump(top_100_ents, file)
    
def preprocessEnts():
  with open("outputs/entities_from_abstract.json", "r") as file:
    data = json.load(file)

  pattern = re.compile(r"[^\x00-\x7F]+") 
  cleaned_ents = [re.sub(pattern, "", ent).replace("\n", "") for ent in data]

  print(cleaned_ents)
  output = open("outputs/cleaned_ents_from_abstract.json", "w")
  json.dump(cleaned_ents, output)

def filterImpRelations():
  impRelations = []
  sor_list = open("outputs/sor_list.json", "r")
  allRelations = json.load(sor_list)
  cleaned_ents_from_abstract = open("outputs/cleaned_ents_from_abstract.json", "r")
  impEnts = json.load(cleaned_ents_from_abstract)

  for relation in allRelations:
    if len(relation) == 3 and (relation[0] in impEnts or relation[1] in impEnts):
      impRelations.append(relation)

  output = open("outputs/imp_sor_list.json", "w")

  json.dump(impRelations, output)

# extractEntitiesFromAbstract()
# print(extract_abstract_from_pdf("testPdf.pdf"))
# extractText()
# getDistinctEntities()
# preprocessEnts()

filterImpRelations()