import faiss
from faiss import normalize_L2
import pickle
import numpy as np
import os

# Obtenir les chemins absolus
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(script_dir)
project_root = os.path.dirname(src_dir)

embeddings_path = os.path.join(project_root, "data", "embeddings.pkl")
faiss_dir = os.path.join(project_root, "data", "faiss")
index_path = os.path.join(faiss_dir, "index.faiss")
mapping_path = os.path.join(faiss_dir, "file_mapping.pkl")

# Vérifier que embeddings.pkl existe
if not os.path.exists(embeddings_path):
    exit(1)

# Charger les embeddings
with open(embeddings_path, "rb") as f:
    data = pickle.load(f)

embeddings = data["embeddings"]
file_paths = data["file_paths"]

# Convertir en numpy array float32 
emb_array = np.array(embeddings).astype('float32')
embedding_dim = emb_array.shape[1]

normalize_L2(emb_array)

# Créer le dossier FAISS
os.makedirs(faiss_dir, exist_ok=True)

# Créer l'index FAISS avec produit scalaire (pour cosinus après normalisation)
index = faiss.IndexFlatIP(embedding_dim)  
index.add(emb_array)

# Sauvegarder l'index et le mapping
faiss.write_index(index, index_path)
with open(mapping_path, "wb") as f:
    pickle.dump(file_paths, f)


# Fonction de recherche top-k 
def search(query_emb, k=5):
    k = min(k, len(file_paths))
    normalize_L2(query_emb)  # Normaliser la query aussi
    distances, indices = index.search(query_emb, k)
    results = [(file_paths[i], distances[0][idx]) for idx, i in enumerate(indices[0])]
    return results


