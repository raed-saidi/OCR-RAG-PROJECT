import faiss
import pickle
import numpy as np
import os

# --- Charger les embeddings ---
with open("data/embeddings.pkl", "rb") as f:
    data = pickle.load(f)

embeddings = data["embeddings"]
file_paths = data["file_paths"]

# --- Convertir en numpy array float32 ---
emb_array = np.array(embeddings).astype('float32')
embedding_dim = emb_array.shape[1]

# --- Créer l'index FAISS ---
index = faiss.IndexFlatL2(embedding_dim)  # L2 = distance euclidienne
index.add(emb_array)
print(f"FAISS index contient {index.ntotal} vecteurs")

# --- Sauvegarder l'index et les chemins ---
os.makedirs("data", exist_ok=True)
faiss.write_index(index, "data/faiss_index.idx")

with open("data/file_paths.pkl", "wb") as f:
    pickle.dump(file_paths, f)

print("Index FAISS et chemins sauvegardés ✅")

# --- Fonction de recherche top-k ---
def search(query_emb, k=5):
    """
    query_emb : embedding numpy float32 (1, dim)
    k : nombre de documents à récupérer
    """
    distances, indices = index.search(query_emb, k)
    results = [(file_paths[i], distances[0][idx]) for idx, i in enumerate(indices[0])]
    return results

# --- Test rapide si on lance directement ---
if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer("all-MiniLM-L6-v2")
    test_query = "Comment installer Tesseract OCR sur Windows?"
    query_emb = model.encode([test_query]).astype('float32')
    
    results = search(query_emb, k=5)
    print("\nTop-5 documents les plus pertinents :")
    for path, dist in results:
        print(f"{path} (distance: {dist:.4f})")
