import json
import streamlit as st
import pymupdf
import spacy

st.title("PDF Extractor")
nlp = spacy.load("en_core_sci_sm")

uploaded_file = st.file_uploader("Upload a pdf", type="pdf")

if uploaded_file is not None:
  doc = pymupdf.open(stream=uploaded_file)
  out = open("outputs/output.txt", "wb")
  
  for page in doc:
    text = page.get_text().encode("utf8")
    out.write(text)
    out.write(b"\f")
  out.close()


with open("output.txt", "r", encoding="utf-8") as file:
  text_input = file.read()
  entity_doc = nlp(text_input)

with open("entity_output.txt", "w", encoding="utf-8") as file:
  for ent in entity_doc.ents:
   file.write(f"{ent.text}\t{ent.label_}\n") 

entList = []
for ent in entity_doc.ents:
  entList.append(ent.text)


with open("output_json.json", "w") as file:
  json.dump(entList, file)





# print(entity_doc)
# entity_output.write(entity_doc)
# entity_output.close()




