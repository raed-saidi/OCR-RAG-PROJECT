import os
import mimetypes

def get_file_type(filepath):
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type.split('/')[0] if mime_type else "unknown"

def list_files_recursive(folder, files_list):
    for item in os.listdir(folder):
        full_path = os.path.join(folder, item)
        if os.path.isfile(full_path):
            files_list.append({
                "path": full_path,
                "type": get_file_type(full_path)
            })
        elif os.path.isdir(full_path):
            list_files_recursive(full_path, files_list)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    raw_folder = os.path.join(project_root, "data", "raw")
    
    if not os.path.exists(raw_folder):
        print(f"[ERROR] Folder not found: {raw_folder}")
        exit(1)
    
    files = []
    list_files_recursive(raw_folder, files)
    
    print(f"[INFO] Found {len(files)} file(s) in {raw_folder}\n")
    for f in files:
        print(f"  {f['type']:10} {f['path']}")