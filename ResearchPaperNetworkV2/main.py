import streamlit as st
import fitz
import os
import json
from dotenv import load_dotenv
from src.matchpapers import match_papers, find_best_match, recommend_top_k, papers # Ensure 'papers' is correctly imported and available

load_dotenv()
api_key = os.getenv("FOS_API_KEY")

# --- Custom CSS for beautification ---
st.markdown(
    """
    <style>
    body {
        background-color: #181c20;
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        color: #f5f6fa;
    }
    .main {
        background-color: #232946;
        border-radius: 16px;
        padding: 2.5rem 2.5rem 1.5rem 2.5rem;
        box-shadow: 0 4px 24px rgba(20,20,40,0.25);
        margin-bottom: 2.5rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6c63ff 0%, #48c6ef 100%);
        color: #fff;
        border-radius: 10px;
        font-size: 1.08rem;
        padding: 0.6rem 2rem;
        border: none;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(76, 110, 245, 0.18);
        transition: background 0.2s, box-shadow 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #48c6ef 0%, #6c63ff 100%);
        box-shadow: 0 4px 16px rgba(76, 110, 245, 0.25);
    }
    .st-bb {
        background: #232946;
        color: #f5f6fa;
        border-radius: 10px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 1px 6px rgba(20,20,40,0.18);
        font-size: 1.13rem;
        font-weight: 500;
        letter-spacing: 0.01em;
        border: 1px solid #353b48;
    }
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1v0mbdj * {
        background: #232946 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
        color: #f5f6fa !important;
    }
    .stAlert, .stInfo, .stWarning {
        color: #f5f6fa !important;
        background: #232946 !important;
        border-radius: 10px !important;
        font-weight: 500;
        border-left: 6px solid #6c63ff !important;
        box-shadow: 0 1px 6px rgba(20,20,40,0.18);
    }
    .stAlert[data-baseweb="notification"] {
        border-left: 6px solid #ff595e !important;
    }
    .stInfo[data-baseweb="notification"] {
        border-left: 6px solid #48c6ef !important;
    }
    .stWarning[data-baseweb="notification"] {
        border-left: 6px solid #ffd166 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #181c20;
        border-radius: 10px;
        padding: 0.3rem 0.3rem 0 0.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(20,20,40,0.18);
    }
    .stTabs [data-baseweb="tab"] {
        color: #48c6ef;
        font-weight: 600;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.2rem;
        margin-right: 0.5rem;
        background: transparent;
        transition: background 0.2s, color 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: #232946;
        color: #f5f6fa;
        box-shadow: 0 2px 8px rgba(76, 110, 245, 0.18);
    }
    .st-expander {
        background: #232946 !important;
        border-radius: 10px !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 1px 6px rgba(20,20,40,0.18);
        color: #f5f6fa !important;
    }
    .st-expanderHeader {
        color: #48c6ef !important;
        font-weight: 600 !important;
        font-size: 1.08rem !important;
    }
    .stSidebar {
        background: linear-gradient(135deg, #232946 0%, #181c20 100%) !important;
        color: #f5f6fa !important;
    }
    .stSidebar .css-1d391kg, .stSidebar .css-1v0mbdj {
        color: #f5f6fa !important;
    }
    .stSidebar .stImage img {
        filter: drop-shadow(0 2px 8px rgba(44,62,80,0.10));
    }
    .stSidebar .stTitle, .stSidebar .stMarkdown {
        color: #f5f6fa !important;
    }
    a {
        color: #48c6ef;
        text-decoration: none;
        transition: color 0.2s;
    }
    a:hover {
        color: #6c63ff;
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar with branding/info ---
st.sidebar.title("📚 Research Paper Network")
st.sidebar.markdown("""
**Welcome!**

Upload a research paper PDF to analyze its title, abstract, and field of study (FOS). Get recommendations and explore FOS hierarchies.

---
*Powered by Streamlit*  
""")

st.title("🔬 Research Paper Analyzer")

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


uploaded_file = st.file_uploader("📄 Upload a PDF document", type="pdf")

if uploaded_file is not None:
    with st.spinner("Extracting information from your PDF..."):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        results = match_papers(doc, api_key)

    st.success("PDF processed successfully!")

    # --- Display extracted info in columns ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Extracted Title:")
        st.markdown(f"<div class='st-bb'>{results['raw_title']}</div>", unsafe_allow_html=True)

        st.subheader("🔧 Preprocessed Title:")
        st.markdown(f"<div class='st-bb'>{results['preprocessed_title']}</div>", unsafe_allow_html=True)

    with col2:
        if results["abstract"]:
            st.subheader("📑 Extracted Abstract:")
            st.markdown(f"<div class='st-bb'>{results['abstract']}</div>", unsafe_allow_html=True)
        else:
            st.warning("No abstract found in the document.")

        if results["fos_tags"]:
            st.subheader("🏷️ Extracted FOS Tags:")
            st.markdown(f"<div class='st-bb'>{results['fos_tags']}</div>", unsafe_allow_html=True)
        else:
            st.warning("FOS tags could not be extracted (missing API key or abstract).")

    # --- Extended FOS ---
    uploaded_paper_all_fos = get_all_related_fos(results["fos_tags"], fos_hierarchy) if results["fos_tags"] else []
    with st.expander("🔗 Uploaded Paper's Extended FOS (including parents)"):
        if uploaded_paper_all_fos:
            st.info(uploaded_paper_all_fos)
        else:
            st.info("No extended FOS could be determined for the uploaded paper based on hierarchy.")

    # --- Find best match ---
    if results["raw_title"]:
        idx, sim_score = find_best_match(results["raw_title"])
        matched_paper = papers[idx]

        with st.expander("🎯 Best Matched Paper in Dataset"):
            st.write(f"**Index:** {idx}")
            # Make title clickable if url exists
            matched_url = matched_paper.get('url')
            if matched_url:
                st.markdown(f"**Title:** [ {matched_paper['title']} ]({matched_url})", unsafe_allow_html=True)
            else:
                st.write(f"**Title:** {matched_paper['title']}")
            st.write(f"**Similarity:** {sim_score:.4f}")
            matched_fos = matched_paper.get('fos', [])
            st.write(f"**FOS:** {matched_fos}")

            # --- Display FOS Hierarchy (existing) ---
            if fos_hierarchy and matched_fos:
                st.subheader("🧬 Field of Study Hierarchy (Parents)")
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

        # --- Recommendations Tabs ---
        tab1, tab2 = st.tabs(["🔍 By Title Similarity", "🌐 By FOS Hierarchy Similarity"])

        with tab1:
            st.subheader("Top 5 Recommended Papers (by Title Similarity):")
            top_papers = recommend_top_k(idx, k=5)
            for i, p in enumerate(top_papers, 1):
                # Make title clickable if url exists
                url = p.get('url')
                if url:
                    st.markdown(f"**{i}. [{p['score']}] [ {p['title']} ]({url})**", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{i}. [{p['score']}] {p['title']}**")
                st.write(f"FOS: {p['fos']}")

        with tab2:
            st.subheader("Top 5 Recommended Papers (by FOS Hierarchy Similarity):")
            if results["fos_tags"] and fos_hierarchy:
                uploaded_combined_fos = set(get_all_related_fos(results["fos_tags"], fos_hierarchy))
                if uploaded_combined_fos:
                    fos_recommendations = []
                    for i, paper_in_dataset in enumerate(papers):
                        if i == idx:
                            continue
                        dataset_paper_direct_fos = paper_in_dataset.get("fos", [])
                        dataset_paper_combined_fos = set(get_all_related_fos(dataset_paper_direct_fos, fos_hierarchy))
                        if uploaded_combined_fos and dataset_paper_combined_fos:
                            sim = compute_jaccard_similarity(uploaded_combined_fos, dataset_paper_combined_fos)
                            if sim > 0:
                                fos_recommendations.append({
                                    "index": i,
                                    "title": paper_in_dataset.get("title", "Unknown"),
                                    "score": sim,
                                    "fos": dataset_paper_direct_fos,
                                    "url": paper_in_dataset.get("url")
                                })
                    fos_recommendations.sort(key=lambda x: x["score"], reverse=True)
                    if fos_recommendations:
                        for i, p in enumerate(fos_recommendations[:5], 1):
                            url = p.get('url')
                            if url:
                                st.markdown(f"**{i}. [{p['score']:.4f}] [ {p['title']} ]({url})**", unsafe_allow_html=True)
                            else:
                                st.markdown(f"**{i}. [{p['score']:.4f}] {p['title']}**")
                            st.write(f"FOS: {p['fos']}")
                    else:
                        st.info("No papers found with similar FOS hierarchy tags in the dataset.")
                else:
                    st.warning("Could not determine extended FOS for the uploaded paper, so cannot recommend by FOS hierarchy.")
            else:
                st.warning("FOS tags from uploaded paper or FOS hierarchy data are missing, cannot recommend by FOS hierarchy.")