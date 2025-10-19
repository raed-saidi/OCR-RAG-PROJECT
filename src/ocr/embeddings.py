import os
import pickle
import sys
from sentence_transformers import SentenceTransformer

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
text_folder = os.path.join(project_root, "data", "text")
output_path = os.path.join(project_root, "data", "embeddings.pkl")

if not os.path.exists(text_folder):
    print(f"[ERROR] Text folder not found: {text_folder}")
    sys.exit(1)

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = []
file_paths = []

def process_file(filename):
    full_path = os.path.join(text_folder, filename)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if text.strip():
            emb = model.encode(text)
            embeddings.append(emb)
            file_paths.append(full_path)
    except Exception as e:
        print(f"[ERROR] {filename}: {e}")

# Process all text files
files = [f for f in os.listdir(text_folder) if f.endswith('.txt')]

if not files:
    print("[ERROR] No text files found")
    sys.exit(1)

print(f"[INFO] Processing {len(files)} file(s)...\n")

for file in files:
    process_file(file)

# Save embeddings
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "wb") as f:
    pickle.dump({"embeddings": embeddings, "file_paths": file_paths}, f)

print(f"[SUCCESS] Generated {len(embeddings)} embeddings")
print(f"[SUCCESS] Saved to: {output_path}\n")