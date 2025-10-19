import faiss
from faiss import normalize_L2
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import sys

class Retriever:
    def __init__(self, index_path="data/faiss/index.faiss", mapping_path="data/faiss/file_mapping.pkl"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        
        self.index_path = os.path.join(project_root, index_path)
        self.mapping_path = os.path.join(project_root, mapping_path)
        
        if not os.path.exists(self.index_path):
            print(f"[ERROR] Index FAISS introuvable : {self.index_path}", file=sys.stderr)
            raise FileNotFoundError(f"Index FAISS introuvable : {self.index_path}")
        if not os.path.exists(self.mapping_path):
            print(f"[ERROR] Mapping introuvable : {self.mapping_path}", file=sys.stderr)
            raise FileNotFoundError(f"Mapping introuvable : {self.mapping_path}")
        
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.read_index(self.index_path)
        
        with open(self.mapping_path, "rb") as f:
            self.file_paths = pickle.load(f)

        print(f"[DEBUG] Loaded {len(self.file_paths)} files from mapping", file=sys.stderr)

    def search(self, query, k=3):
        k = min(k, len(self.file_paths))
        query_vector = self.model.encode([query]).astype("float32")
        normalize_L2(query_vector)
        distances, indices = self.index.search(query_vector, k)
        results = [self.file_paths[i] for i in indices[0]]
        return results, distances[0]
    
    def search_with_texts(self, query, k=3):
        results, distances = self.search(query, k)
        valid_results = []
        valid_distances = []
        texts = []

        for p, d in zip(results, distances):
            if isinstance(p, str) and os.path.isfile(p):
                valid_results.append(p)
                valid_distances.append(d)
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        texts.append(f.read())
                except Exception:
                    texts.append("")

        print(f"[DEBUG] Returning {len(valid_results)} documents", file=sys.stderr)
        return valid_results, np.array(valid_distances, dtype=float), texts
