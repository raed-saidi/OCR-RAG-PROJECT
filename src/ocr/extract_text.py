import os
import re
import pytesseract
import pdfplumber
import sys
from pdf2image import convert_from_path

# Minimal text cleaning
def minimal_cleaning(text): 
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    text = re.sub(r' +', ' ', text)
    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(lines)

# Check if PDF is scanned
def is_scanned_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                return False 
    return True  

# Extract text from scanned PDF
def extract_text_from_scanned_pdf(pdf_path):
    text = ""
    pages = convert_from_path(pdf_path, dpi=300)
    for page in pages:
        page_text = pytesseract.image_to_string(page)
        text += page_text + "\n"
    return text

# Extract text from PDF (scan or texte)
def extract_text_pdf(file):
    text = ""
    if is_scanned_pdf(file["path"]):
        text = extract_text_from_scanned_pdf(file["path"])
    else:
        with pdfplumber.open(file["path"]) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    return minimal_cleaning(text)

# Extract text from image
def extract_text_image(file):
    text = pytesseract.image_to_string(file["path"])
    return minimal_cleaning(text)

# Extract file name without extension
def name_extractor(file_path):
    name = os.path.basename(file_path)
    name = os.path.splitext(name)[0]
    return name

# Save cleaned text to file
def storing_text(text, file_path):
    name = name_extractor(file_path)
    # Obtenir le chemin absolu vers la racine du projet
    script_dir = os.path.dirname(os.path.abspath(__file__))  # src/ocr/
    src_dir = os.path.dirname(script_dir)  # src/
    project_root = os.path.dirname(src_dir)  # racine du projet
    output_path = os.path.join(project_root, "data", "text", name + ".txt")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

# Main iteration over file list
def iterating(files_list):
    if not files_list:
        return
    
    for i, file in enumerate(files_list, 1):
        try:
            if file["type"] == "application":  # PDF
                text = extract_text_pdf(file)
            else:  # Image
                text = extract_text_image(file)
            storing_text(text, file["path"])
        except Exception as e:
            print(f"[ERREUR] Échec pour {file['path']}: {str(e)}")

