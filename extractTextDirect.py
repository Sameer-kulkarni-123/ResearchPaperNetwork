import pymupdf
import torch
from transformers import pipeline
import spacy

deviceToUse = 0 if torch.cuda.is_available() else -1

nlp = spacy.load("en_core_sci_sm")
re_pipeline = pipeline("text2text-generation", model="Babelscape/rebel-large", device=deviceToUse)

text = pymupdf.open("testPdf.pdf")

full_text = ""

for page in text:
  full_text += page.get_text()

spacy_doc = nlp(full_text)

for sent in spacy_doc.sents:
  output = re_pipeline(sent.text)
  RE_output = open("outputs/RE_outputs_from_transformer.txt", "a", encoding="utf-8")
  RE_output.write(output[0]['generated_text'])
  RE_output.write("\n")
  print(output[0]['generated_text'])


