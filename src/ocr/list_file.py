import os
import mimetypes

files = []

def get_file_type(filepath):
    mime_type, _ = mimetypes.guess_type(filepath)
    if mime_type:
        return mime_type.split('/')[0]  
    return "unknown"

def list_files(folder):
    contenu = os.listdir(folder)
    for c in contenu:
        full_path = os.path.join(folder, c)
        if os.path.isfile(full_path):
            files.append({
                "path": full_path,
                "type": get_file_type(full_path)
            })
        elif os.path.isdir(full_path):
            list_files(full_path)  # recursion pour les sous-dossiers

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
folder = os.path.join(project_root, "data", "raw")

# Vérifier si le dossier existe
if os.path.exists(folder):
    list_files(folder)
    print(f"[INFO] {len(files)} fichier(s) trouvé(s) dans {folder}\n")
    for f in files:
        print(f)
else:
    print(f"[ERREUR] Le dossier {folder} n'existe pas !")