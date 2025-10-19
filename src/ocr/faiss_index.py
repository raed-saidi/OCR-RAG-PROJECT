import faiss
from faiss import normalize_L2
import pickle
import numpy as np
import os
import sys

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
embeddings_path = os.path.join(project_root, "data", "embeddings.pkl")
faiss_dir = os.path.join(project_root, "data", "faiss")
index_path = os.path.join(faiss_dir, "index.faiss")
mapping_path = os.path.join(faiss_dir, "file_mapping.pkl")

if not os.path.exists(embeddings_path):
    print(f"[ERROR] Embeddings not found: {embeddings_path}")
    print("[TIP] Run: python src/ocr/embeddings.py")
    sys.exit(1)

# Load embeddings
with open(embeddings_path, "rb") as f:
    data = pickle.load(f)

embeddings = data["embeddings"]
file_paths = data["file_paths"]

print(f"[INFO] Loaded {len(embeddings)} embeddings")

# Prepare for FAISS
emb_array = np.array(embeddings).astype('float32')
embedding_dim = emb_array.shape[1]
normalize_L2(emb_array)

# Create FAISS index
os.makedirs(faiss_dir, exist_ok=True)
index = faiss.IndexFlatIP(embedding_dim)
index.add(emb_array)

# Save index and mapping
faiss.write_index(index, index_path)
with open(mapping_path, "wb") as f:
    pickle.dump(file_paths, f)

print(f"[SUCCESS] Created FAISS index with {index.ntotal} vectors")
print(f"[SUCCESS] Saved to: {index_path}\n")