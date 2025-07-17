import streamlit as st
import fitz
import os
from dotenv import load_dotenv
from src.matchpapers import match_papers, find_best_match, recommend_top_k, papers

load_dotenv()
api_key = os.getenv("FOS_API_KEY")

st.title("Research Paper Analyzer")

uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    results = match_papers(doc, api_key)

    st.subheader("Extracted Title:")
    st.write(results["raw_title"])

    st.subheader("Preprocessed Title:")
    st.write(results["preprocessed_title"])

    if results["abstract"]:
        st.subheader("Extracted Abstract:")
        st.write(results["abstract"])

        if results["fos_tags"]:
            st.subheader("Extracted FOS Tags:")
            st.write(results["fos_tags"])
        else:
            st.warning("FOS tags could not be extracted (missing API key or abstract).")
    else:
        st.warning("No abstract found in the document.")

    # --- Find best match ---
    if results["raw_title"]:
        idx, sim_score = find_best_match(results["raw_title"])
        st.subheader("Best Matched Paper in Dataset:")
        st.write(f"**Index:** {idx}")
        st.write(f"**Title:** {papers[idx]['title']}")
        st.write(f"**Similarity:** {sim_score:.4f}")
        st.write(f"**FOS:** {papers[idx].get('fos', [])}")

        # --- Recommend top 5 similar papers ---
        st.subheader("Top 5 Recommended Papers:")
        top_papers = recommend_top_k(idx, k=5)
        for i, p in enumerate(top_papers, 1):
            st.markdown(f"**{i}. [{p['score']}] {p['title']}**")
            st.write(f"FOS: {p['fos']}")