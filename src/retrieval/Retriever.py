import faiss
from faiss import normalize_L2
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np


class Retriever :
    def __init__(self,index_path="data/faiss/index.faiss", mapping_path="data/faiss/file_mapping.pkl"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.read_index("data/faiss/index.faiss")
        with open(mapping_path, "rb") as f:
            self.file_paths = pickle.load(f)

    def search(self, query, k=3):
        k = min(k, len(self.file_paths))
        query_vector = self.model.encode([query]).astype("float32")
        normalize_L2(query_vector)  # Normalisation L2
        distances, indices = self.index.search(query_vector, k)
        results = [self.file_paths[i] for i in indices[0]]
        return results, distances[0]
    
    def search_with_texts(self, query, k=3):
        results, distances = self.search(query, k)
        texts = []
        for path in results:
            with open(path, "r", encoding="utf-8") as f :
                texts.append(f.read())
        return results, distances, texts


if __name__ == "__main__":
    retriever = Retriever()
    query = input("🔎 Enter your question: ")
    results, distances = retriever.search(query)
    for r, d in zip(results, distances):
        print(f"{r} (score={d:.2f})")
