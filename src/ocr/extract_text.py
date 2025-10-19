import os
import re
import sys

try:
    import pytesseract
    import pdfplumber
    from pdf2image import convert_from_path
except ImportError as e:
    print(f"[ERROR] Missing library: {e}")
    print("Install: pip install pytesseract pdfplumber pdf2image Pillow")
    sys.exit(1)

def minimal_cleaning(text): 
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    text = re.sub(r' +', ' ', text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return '\n'.join(lines)

def is_scanned_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.extract_text() and page.extract_text().strip():
                    return False
        return True
    except:
        return True

def extract_text_from_scanned_pdf(pdf_path):
    text = ""
    try:
        pages = convert_from_path(pdf_path, dpi=300)
        for page in pages:
            text += pytesseract.image_to_string(page) + "\n"
    except Exception as e:
        print(f"[ERROR] OCR failed: {e}")
    return text

def extract_text_pdf(file_info):
    try:
        if is_scanned_pdf(file_info["path"]):
            text = extract_text_from_scanned_pdf(file_info["path"])
        else:
            text = ""
            with pdfplumber.open(file_info["path"]) as pdf:
                for page in pdf.pages:
                    if page.extract_text():
                        text += page.extract_text() + "\n"
        return minimal_cleaning(text)
    except Exception as e:
        print(f"[ERROR] PDF processing failed: {e}")
        return ""

def extract_text_image(file_info):
    try:
        text = pytesseract.image_to_string(file_info["path"])
        return minimal_cleaning(text)
    except Exception as e:
        print(f"[ERROR] Image processing failed: {e}")
        return ""

def save_text(text, file_path):
    if not text or not text.strip():
        return False
    
    name = os.path.splitext(os.path.basename(file_path))[0]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_path = os.path.join(project_root, "data", "text", f"{name}.txt")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"[ERROR] Save failed: {e}")
        return False

def get_files_recursive(folder_path):
    files = []
    supported = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported:
                files.append({
                    "path": os.path.join(root, filename),
                    "name": filename,
                    "type": "application" if ext == '.pdf' else "image"
                })
    return files

def process_files(files_list):
    if not files_list:
        print("[WARNING] No files to process")
        return
    
    print(f"\n{'='*60}\nProcessing {len(files_list)} file(s)\n{'='*60}\n")
    
    success = 0
    for i, file in enumerate(files_list, 1):
        print(f"[{i}/{len(files_list)}] {file['name']}")
        try:
            text = extract_text_pdf(file) if file["type"] == "application" else extract_text_image(file)
            
            if save_text(text, file["path"]):
                success += 1
                print(f"  ✓ {len(text)} chars\n")
            else:
                print(f"  ✗ No text\n")
        except Exception as e:
            print(f"  ✗ {str(e)}\n")
    
    print(f"{'='*60}\nComplete: {success}/{len(files_list)} processed\n{'='*60}\n")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    raw_folder = os.path.join(project_root, "data", "raw")
    
    if not os.path.exists(raw_folder):
        print(f"[ERROR] Folder not found: {raw_folder}")
        sys.exit(1)
    
    files = get_files_recursive(raw_folder)
    
    if not files:
        print("[ERROR] No supported files found")
        print("Supported: PDF, PNG, JPG, JPEG, TIFF, BMP")
        sys.exit(1)
    
    process_files(files)
    
    text_folder = os.path.join(project_root, "data", "text")
    if os.path.exists(text_folder):
        count = len([f for f in os.listdir(text_folder) if f.endswith('.txt')])
        print(f"✅ {count} text file(s) generated\n")