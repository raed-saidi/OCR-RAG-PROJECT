import os
import re
import sys

try:
    import pytesseract
    import pdfplumber
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError as e:
    print(f"[ERROR] Missing required library: {e}")
    print("Install with: pip install pytesseract pdfplumber pdf2image Pillow")
    sys.exit(1)

def minimal_cleaning(text): 
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    text = re.sub(r' +', ' ', text)
    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(lines)

def is_scanned_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    return False 
        return True
    except Exception as e:
        print(f"[ERROR] Failed to check if PDF is scanned: {e}")
        return True

def extract_text_from_scanned_pdf(pdf_path):
    text = ""
    try:
        pages = convert_from_path(pdf_path, dpi=300)
        for page in pages:
            page_text = pytesseract.image_to_string(page)
            text += page_text + "\n"
    except Exception as e:
        print(f"[ERROR] OCR failed: {e}")
    return text

def extract_text_pdf(file):
    text = ""
    try:
        if is_scanned_pdf(file["path"]):
            text = extract_text_from_scanned_pdf(file["path"])
        else:
            with pdfplumber.open(file["path"]) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        return minimal_cleaning(text)
    except Exception as e:
        print(f"[ERROR] Failed to process PDF: {e}")
        return ""

def extract_text_image(file):
    try:
        text = pytesseract.image_to_string(file["path"])
        return minimal_cleaning(text)
    except Exception as e:
        print(f"[ERROR] Failed to process image: {e}")
        return ""

def name_extractor(file_path):
    name = os.path.basename(file_path)
    name = os.path.splitext(name)[0]
    return name

def storing_text(text, file_path):
    if not text or not text.strip():
        return False
    
    name = name_extractor(file_path)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(script_dir)
    project_root = os.path.dirname(src_dir)
    output_path = os.path.join(project_root, "data", "text", name + ".txt")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save file: {e}")
        return False

def get_files_list_recursive(folder_path):
    """Recursively get all files from folder and subfolders"""
    files = []
    supported_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported_extensions:
                file_type = "application" if ext == '.pdf' else "image"
                files.append({
                    "path": filepath,
                    "name": filename,
                    "type": file_type
                })
    
    return files

def iterating(files_list):
    if not files_list:
        print("[WARNING] No files to process!")
        return
    
    print(f"\n{'='*60}")
    print(f"Processing {len(files_list)} file(s)")
    print(f"{'='*60}\n")
    
    success_count = 0
    
    for i, file in enumerate(files_list, 1):
        print(f"[{i}/{len(files_list)}] {file['name']}")
        try:
            if file["type"] == "application":
                text = extract_text_pdf(file)
            else:
                text = extract_text_image(file)
            
            if storing_text(text, file["path"]):
                success_count += 1
                print(f"  ✓ Extracted {len(text)} characters\n")
            else:
                print(f"  ✗ No text extracted\n")
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}\n")
    
    print(f"{'='*60}")
    print(f"Complete: {success_count}/{len(files_list)} files processed")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(script_dir)
    project_root = os.path.dirname(src_dir)
    raw_folder = os.path.join(project_root, "data", "raw")
    
    if not os.path.exists(raw_folder):
        print(f"[ERROR] Raw folder doesn't exist: {raw_folder}")
        sys.exit(1)
    
    files = get_files_list_recursive(raw_folder)
    
    if not files:
        print("[ERROR] No supported files found in data/raw/")
        print("Supported formats: PDF, PNG, JPG, JPEG, TIFF, BMP")
        sys.exit(1)
    
    iterating(files)
    
    text_folder = os.path.join(project_root, "data", "text")
    if os.path.exists(text_folder):
        text_files = [f for f in os.listdir(text_folder) if f.endswith('.txt')]
        print(f"✅ {len(text_files)} text file(s) generated\n")