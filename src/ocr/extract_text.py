import os
import re
import pytesseract
import pdfplumber
import sys
from pdf2image import convert_from_path



# ⚡ Optionnel : préciser le chemin de Tesseract sur Windows
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -----------------------------
# Minimal text cleaning
# -----------------------------
def minimal_cleaning(text): 
    # Supprimer les caractères non imprimables
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    # Remplacer plusieurs espaces par un seul
    text = re.sub(r' +', ' ', text)
    # Supprimer les lignes vides
    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(lines)

# -----------------------------
# Check if PDF is scanned
# -----------------------------
def is_scanned_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                return False  # PDF texte natif
    return True  # PDF scanné

# -----------------------------
# Extract text from scanned PDF
# -----------------------------
def extract_text_from_scanned_pdf(pdf_path):
    text = ""
    pages = convert_from_path(pdf_path, dpi=300)
    for page in pages:
        page_text = pytesseract.image_to_string(page)
        text += page_text + "\n"
    return text

# -----------------------------
# Extract text from PDF (scan or texte)
# -----------------------------
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

# -----------------------------
# Extract text from image
# -----------------------------
def extract_text_image(file):
    text = pytesseract.image_to_string(file["path"])
    return minimal_cleaning(text)

# -----------------------------
# Extract file name without extension
# -----------------------------
def name_extractor(file_path):
    name = os.path.basename(file_path)
    name = os.path.splitext(name)[0]
    return name

# -----------------------------
# Save cleaned text to file
# -----------------------------
def storing_text(text, file_path):
    name = name_extractor(file_path)
    output_path = os.path.join("data", "text", name + ".txt")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"[SAVED] {output_path}")

# -----------------------------
# Main iteration over file list
# -----------------------------
def iterating(files_list):
    for file in files_list:
        if file["type"] == "application":  # PDF
            text = extract_text_pdf(file)
        else:  # Image
            text = extract_text_image(file)
        storing_text(text, file["path"])

# -----------------------------
# Exemple d'utilisation
# -----------------------------
if __name__ == "__main__":
   
    # Ajouter le dossier courant au Python path pour trouver list_files.py
    sys.path.append(os.path.dirname(__file__))

    from list_file import files  # fichiers listés
    iterating(files)
