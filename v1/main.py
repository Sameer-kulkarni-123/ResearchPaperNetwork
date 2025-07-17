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
    print("abstract : ", abstract)
    print("======================================")
    entitiesFromAbstract = extractEntitiesFromAbstract(abstract)
    print("entitiesFromAbstract", entitiesFromAbstract)
    print("======================================")
    preprocessedEnts = preprocessEnts(entitiesFromAbstract)
    print("preprocessedEnts", preprocessedEnts)
    print("======================================")
    distinctEntities = getDistinctEntities(preprocessedEnts)
    print("distinctEntities : ", distinctEntities)
    print("======================================")

    sor_list = extractText(doc)
    print("sor_list : ", sor_list)
    print("======================================")

    impRelations = filterImpRelations(sor_list, distinctEntities)
    print("impRelations : ", impRelations)
    print("======================================")

    runPyvis(impRelations)
    # runPyvis()

  st.title("Knowledge Graph")

  with open("graph.html", "r", encoding="utf-8") as f:
    html_string = f.read()

  components.html(html_string, height=600, width=0, scrolling=True)
