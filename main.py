import streamlit as st
import pymupdf
from extractAndPreprocess import extract_abstract_from_pdf, extractEntitiesFromAbstract, extractText, getDistinctEntities, filterImpRelations, preprocessEnts
from createNetwork import runPyvis
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("PDF Extractor")

uploaded_file = st.file_uploader("Upload a pdf", type="pdf")

if uploaded_file is not None:
  with st.spinner("Processing PDF and building knowledge graph..."): 
    doc = pymupdf.open(stream=uploaded_file)

    abstract = extract_abstract_from_pdf(doc)
    print(abstract)
    entitiesFromAbstract = extractEntitiesFromAbstract(abstract)
    print(entitiesFromAbstract)
    preprocessedEnts = preprocessEnts(entitiesFromAbstract)
    print(preprocessedEnts)
    distinctEntities = getDistinctEntities(preprocessedEnts)

    sor_list = extractText("testPdf.pdf")

    impRelations = filterImpRelations(sor_list, distinctEntities)

    runPyvis(impRelations)
    # runPyvis()

  st.title("Knowledge Graph")

  with open("graph.html", "r", encoding="utf-8") as f:
    html_string = f.read()

  components.html(html_string, height=600, width=0, scrolling=True)
