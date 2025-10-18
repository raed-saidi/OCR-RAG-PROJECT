import faiss
import pickle
import numpy as np
import os

# Charger les embeddings
with open("data/embeddings.pkl", "rb") as f:
    data = pickle.load(f)

embeddings = data["embeddings"]
file_paths = data["file_paths"]

# Convertir en numpy array float32 
emb_array = np.array(embeddings).astype('float32')
embedding_dim = emb_array.shape[1]

# Créer le dossier FAISS
os.makedirs("data/faiss", exist_ok=True)

# Créer l'index FAISS
index = faiss.IndexFlatL2(embedding_dim)
index.add(emb_array)
print(f"FAISS index contient {index.ntotal} vecteurs")

# Sauvegarder l'index et le mapping
faiss.write_index(index, "data/faiss/index.faiss")
with open("data/faiss/file_mapping.pkl", "wb") as f:
    pickle.dump(file_paths, f)

print("Index FAISS et mapping sauvegardés ✅")

# Fonction de recherche top-k 
def search(query_emb, k=5):
    distances, indices = index.search(query_emb, k)
    results = [(file_paths[i], distances[0][idx]) for idx, i in enumerate(indices[0])]
    return results

# Test rapide 
if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer("all-MiniLM-L6-v2")
    test_query = "Comment installer Tesseract OCR sur Windows?"
    query_emb = model.encode([test_query]).astype('float32')
    
    results = search(query_emb, k=5)
    print("\nTop-5 documents les plus pertinents :")
    for path, dist in results:
        print(f"{path} (distance: {dist:.4f})")
