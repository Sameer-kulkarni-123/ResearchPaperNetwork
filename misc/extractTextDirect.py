import pymupdf
import json
import torch
from transformers import pipeline
import spacy

def extractText():

  deviceToUse = 0 if torch.cuda.is_available() else -1

  nlp = spacy.load("en_core_sci_sm")
  re_pipeline = pipeline("text2text-generation", model="Babelscape/rebel-large", device=deviceToUse)

  text = pymupdf.open("testPdf.pdf")

  full_text = ""

  for page in text:
    full_text += page.get_text()

  spacy_doc = nlp(full_text)

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


extractText()
