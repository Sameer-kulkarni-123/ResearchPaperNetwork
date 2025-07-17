import fitz  # PyMuPDF
import re
import google.generativeai as genai

def extract_abstract_from_pdf(doc, max_pages=2):
    text = ""
    
    for page_num in range(min(max_pages, len(doc))):
        text += doc[page_num].get_text()

    text = text.replace('\r', '\n')

    pattern = re.compile(
        r"(?:^|\n)(?:abstract|ABSTRACT)\s*[:\n]*\s*(.*?)"
        r"(?=\n(?:\s{0,4}[1-9][\.\s]|introduction|keywords|background|methods|related work)[^\n]{0,80}\n)",
        re.IGNORECASE | re.DOTALL
    )

    match = pattern.search(text)
    if match:
        abstract = match.group(1).strip()
        return abstract
    else:
        return None

def get_fos_from_abstract(abstract, api_key):
    genai.configure(api_key=api_key)
    
    prompt = f"""
        You are an AI assistant trained to classify academic abstracts. 

        Given the abstract below, extract the top 3 Fields of Study (FOS) relevant to it. 
        Respond **only** with a Python list of strings. The strings should be FOS tags such as 
        "Physics", "Education", "Pedagogy", etc.

        Abstract:
        \"\"\"{abstract}\"\"\" 
        end the output with fos
        """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    try:
        tags = eval(response.text.strip())
        if isinstance(tags, list):
            return tags
    except:
        pass

    return ["Unknown"]  # fallback