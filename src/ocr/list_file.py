import os
import mimetypes

files = []

def get_file_type(filepath):
    mime_type, _ = mimetypes.guess_type(filepath)
    if mime_type:
        return mime_type.split('/')[0]  # 'image', 'application', etc.
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

# Exemple d’utilisation
folder = r"data\raw"
list_files(folder)

for f in files:
    print(f)
