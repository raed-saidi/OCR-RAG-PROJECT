import os
import pickle
from sentence_transformers import SentenceTransformer

# Obtenir les chemins absolus
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(script_dir)
project_root = os.path.dirname(src_dir)

text_folder = os.path.join(project_root, "data", "text")
output_path = os.path.join(project_root, "data", "embeddings.pkl")

# Vérifier que le dossier existe
if not os.path.exists(text_folder):
    exit(1)

# Charger le modèle
model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = []
file_paths = []


def embedding(file_name):
    full_path = os.path.join(text_folder, file_name)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if not text.strip():
            return
        
        emb = model.encode(text)
        embeddings.append(emb)
        file_paths.append(full_path)
    except Exception as e:
        print(f"[ERREUR] {file_name}: {e}")


def iterating_texts(text_folder):
    files = [f for f in os.listdir(text_folder) if f.endswith('.txt')]
    
    if not files:
        exit(1)
    
    print(f"[INFO] Traitement de {len(files)} fichier(s)...\n")
    for file in files:
        embedding(file)


# Lancer l'itération
iterating_texts(text_folder)

# Sauvegarder les embeddings
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "wb") as f:
    pickle.dump({"embeddings": embeddings, "file_paths": file_paths}, f)

