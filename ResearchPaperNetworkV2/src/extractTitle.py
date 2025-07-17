import pymupdf  # PyMuPDF
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import nltk
import fitz

# Ensure required resources are downloaded
nltk.download('stopwords')

# Initialize
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()


def extract_title_from_pdf(doc):
    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]

    title_lines = []
    max_font_size = 0

    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text or len(text) < 5:
                    continue
                font_size = span["size"]

                # Heuristic: find largest font on top part of page
                if span["bbox"][1] < 200:  # near top
                    if font_size > max_font_size:
                        max_font_size = font_size
                        title_lines = [text]
                    elif abs(font_size - max_font_size) < 0.5:  # similar size
                        title_lines.append(text)

    title = " ".join(title_lines)
    return title.strip()
    
def preprocess_title(title):
    """
    Tokenize, remove stopwords, apply stemming.
    """
    words = re.findall(r'\b[a-z]+\b', title.lower())
    return ' '.join([stemmer.stem(word) for word in words if word not in stop_words])