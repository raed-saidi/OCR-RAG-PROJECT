import os
from sentence_transformers import SentenceTransformer

# Charger le modèle
model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = []
file_paths = []

text_folder = r"data\text"

def embedding(file_name):
    full_path = os.path.join(text_folder, file_name)
    with open(full_path, 'r', encoding='utf-8') as f:
        text = f.read()  # Lire tout le contenu
    emb = model.encode(text)
    embeddings.append(emb)
    file_paths.append(full_path)

def iterating_texts(text_folder):
    files = os.listdir(text_folder)
    for file in files:
        embedding(file)

# Lancer l’itération
iterating_texts(text_folder)
print(f"Embeddings générés pour {len(embeddings)} fichiers")
print(embeddings)