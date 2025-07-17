import streamlit as st
import fitz
import os
import json
from dotenv import load_dotenv
from src.matchpapers import match_papers, find_best_match, recommend_top_k, papers # Ensure 'papers' is correctly imported and available

load_dotenv()
api_key = os.getenv("FOS_API_KEY")

st.title("Research Paper Analyzer")

# --- Load FOS Hierarchy Data ---
HIERARCHY_JSON_PATH = os.path.join("src", "fos_hierarchy.json")
fos_hierarchy = {}
if os.path.exists(HIERARCHY_JSON_PATH):
    try:
        with open(HIERARCHY_JSON_PATH, "r", encoding="utf8") as f:
            fos_hierarchy = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        st.sidebar.error("Could not load FOS hierarchy data.")
else:
    st.sidebar.warning("FOS hierarchy file not found. Run FOSHierarchy.py to generate it.")

# NEW HELPER FUNCTION: Get all relevant FOS tags (direct + parents)
def get_all_related_fos(fos_tags_list, hierarchy_data):
    """
    Expands a list of FOS tags to include their direct parents from the hierarchy.
    Returns a list of unique FOS tags.
    """
    all_related = set(fos_tags_list) # Start with the direct tags
    for tag in fos_tags_list:
        parents = hierarchy_data.get(tag)
        if parents:
            all_related.update(parents)
    return list(all_related)

# NEW HELPER FUNCTION: Compute Jaccard Similarity between two sets
def compute_jaccard_similarity(set_a, set_b):
    """
    Computes the Jaccard similarity between two sets.
    Returns 0.0 if either set is empty or their union is zero.
    """
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0


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

            # Get and display all relevant FOS tags for the uploaded paper (direct + parents)
            uploaded_paper_all_fos = get_all_related_fos(results["fos_tags"], fos_hierarchy)
            if uploaded_paper_all_fos:
                st.subheader("Uploaded Paper's Extended FOS (including parents):")
                st.write(uploaded_paper_all_fos)
            else:
                st.info("No extended FOS could be determined for the uploaded paper based on hierarchy.")

        else:
            st.warning("FOS tags could not be extracted (missing API key or abstract).")
    else:
        st.warning("No abstract found in the document.")

    # --- Find best match ---
    if results["raw_title"]:
        idx, sim_score = find_best_match(results["raw_title"])
        matched_paper = papers[idx]

        st.subheader("Best Matched Paper in Dataset:")
        st.write(f"**Index:** {idx}")
        st.write(f"**Title:** {matched_paper['title']}")
        st.write(f"**Similarity:** {sim_score:.4f}")

        matched_fos = matched_paper.get('fos', [])
        st.write(f"**FOS:** {matched_fos}")

        # --- Display FOS Hierarchy (existing) ---
        if fos_hierarchy and matched_fos:
            st.subheader("Field of Study Hierarchy (Parents)")
            for fos_tag in matched_fos:
                parents = fos_hierarchy.get(fos_tag)
                if parents:
                    st.markdown(f"- **{fos_tag}** is a sub-field of: `{', '.join(parents)}`")
                else:
                    st.markdown(f"- **{fos_tag}**: No parents found in hierarchy.")
        elif not fos_hierarchy:
            st.warning("FOS hierarchy data is not loaded or is empty. Cannot display hierarchy for matched paper.")
        elif not matched_fos:
            st.warning("No FOS tags found for the matched paper to display hierarchy.")

        # --- Recommend top 5 similar papers (existing by Title Similarity) ---
        st.subheader("Top 5 Recommended Papers (by Title Similarity):")
        top_papers = recommend_top_k(idx, k=5)
        for i, p in enumerate(top_papers, 1):
            st.markdown(f"**{i}. [{p['score']}] {p['title']}**")
            st.write(f"FOS: {p['fos']}")

        # --- NEW: Recommend papers based on FOS Hierarchy (Parental) Similarity ---
        st.subheader("Top 5 Recommended Papers (by FOS Hierarchy Similarity):")

        if results["fos_tags"] and fos_hierarchy:
            uploaded_combined_fos = set(get_all_related_fos(results["fos_tags"], fos_hierarchy))
            
            if uploaded_combined_fos:
                fos_recommendations = []
                
                for i, paper_in_dataset in enumerate(papers):
                    # Skip the uploaded paper's best match if it's the same paper being analyzed
                    if i == idx: 
                        continue

                    dataset_paper_direct_fos = paper_in_dataset.get("fos", [])
                    # Get the extended FOS for this paper in the dataset
                    dataset_paper_combined_fos = set(get_all_related_fos(dataset_paper_direct_fos, fos_hierarchy))

                    if uploaded_combined_fos and dataset_paper_combined_fos: # Only compare if both have FOS
                        sim = compute_jaccard_similarity(uploaded_combined_fos, dataset_paper_combined_fos)
                        if sim > 0: # Only add if there's some similarity
                            fos_recommendations.append({
                                "index": i,
                                "title": paper_in_dataset.get("title", "Unknown"),
                                "score": sim,
                                "fos": dataset_paper_direct_fos
                            })

                # Sort by score in descending order
                fos_recommendations.sort(key=lambda x: x["score"], reverse=True)

                if fos_recommendations:
                    for i, p in enumerate(fos_recommendations[:5], 1): # Get top 5
                        st.markdown(f"**{i}. [{p['score']:.4f}] {p['title']}**")
                        st.write(f"FOS: {p['fos']}")
                else:
                    st.info("No papers found with similar FOS hierarchy tags in the dataset.")
            else:
                st.warning("Could not determine extended FOS for the uploaded paper, so cannot recommend by FOS hierarchy.")
        else:
            st.warning("FOS tags from uploaded paper or FOS hierarchy data are missing, cannot recommend by FOS hierarchy.")