import json
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import nltk
from src.extractTitle import extract_title_from_pdf, preprocess_title
from src.extractFOS import extract_abstract_from_pdf, get_fos_from_abstract
import os

nltk.download('stopwords')

# ------------------------------------
# Step 1: Title Preprocessing Function
# ------------------------------------
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

def preprocess_title(title):
    words = re.findall(r'\b[a-z]+\b', title.lower())
    return ' '.join([stemmer.stem(w) for w in words if w not in stop_words])

# ------------------------------------
# Step 2: Load dataset and similarity matrix
# ------------------------------------
currDir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(currDir, "batch_0.json"), "r", encoding="utf8") as f:
    papers = json.load(f)

similarity_matrix = np.load(os.path.join(currDir, "final_similarity_matrix_batch0.npy"))

# ------------------------------------
# Step 3: Build title list and TF-IDF vectorizer
# ------------------------------------
preprocessed_titles = [preprocess_title(p["title"]) for p in papers if p.get("title")]
vectorizer = TfidfVectorizer()
title_vectors = vectorizer.fit_transform(preprocessed_titles)

# ------------------------------------
# Step 4: Find best match for uploaded paper's title
# ------------------------------------
def find_best_match(uploaded_title):
    processed = preprocess_title(uploaded_title)
    uploaded_vec = vectorizer.transform([processed])
    similarities = cosine_similarity(uploaded_vec, title_vectors).flatten()
    best_index = np.argmax(similarities)
    best_score = similarities[best_index]
    return best_index, best_score

# ------------------------------------
# Step 5: Recommend top-K similar papers from .npy
# ------------------------------------
def recommend_top_k(paper_idx, k=5):
    scores = similarity_matrix[paper_idx]
    top_k_indices = np.argsort(-scores)[:k+1]  # include self
    results = []
    for idx in top_k_indices:
        if idx == paper_idx:
            continue
        results.append({
            "index": idx,
            "title": papers[idx].get("title", "Unknown"),
            "score": round(scores[idx], 4),
            "fos": papers[idx].get("fos", []),
            "url": papers[idx].get("url")
        })
    return results

# ------------------------------------
# Match papers function
# ------------------------------------
def match_papers(doc, api_key):
    # Extract title
    raw_title = extract_title_from_pdf(doc)
    preprocessed_title = preprocess_title(raw_title)

    # Extract abstract
    abstract = extract_abstract_from_pdf(doc)

    # Extract FOS tags if abstract and api_key are present
    fos_tags = None
    if abstract and api_key:
        fos_tags = get_fos_from_abstract(abstract, api_key)

    return {
        "raw_title": raw_title,
        "preprocessed_title": preprocessed_title,
        "abstract": abstract,
        "fos_tags": fos_tags
    }

# ------------------------------------
# Example usage
# ------------------------------------
if __name__ == "__main__":
    uploaded_title = "Identifying Compelled Edges in a DAG - A Constraint Satisfaction Problem."
    idx, sim_score = find_best_match(uploaded_title)
    print("\n📄 Best matched paper in dataset:")
    print(f"Index: {idx}\nTitle: {papers[idx]['title']}\nSimilarity: {sim_score:.4f}")
    print("FOS:", papers[idx].get("fos", []))

    print("\n🔍 Top 5 recommended papers:")
    top_papers = recommend_top_k(idx, k=5)
    for i, p in enumerate(top_papers, 1):
        print(f"\n{i}. [{p['score']}] {p['title']}")
        print(f"   FOS: {p['fos']}")
