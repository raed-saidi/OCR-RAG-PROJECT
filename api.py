from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import subprocess
import os
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv() 
app = FastAPI(title="OCR-RAG API")

# Request body
class QueryRequest(BaseModel):
    query: str

@app.post("/rag")
async def rag_endpoint(request: QueryRequest):
    query = request.query.strip()
    if not query:
        return {"success": False, "error": "Query manquante"}

    # Path to call_rag.py
    project_root = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(project_root, "src", "ocr", "call_rag.py")
    if not os.path.exists(script_path):
        return {"success": False, "error": f"Script Python introuvable: {script_path}"}

    # Python path (venv or global)
    python_path = os.path.join(project_root, ".venv", "Scripts", "python.exe")  # Windows
    if not os.path.exists(python_path):
        python_path = "python"  # fallback global python

    # Run the RAG pipeline
    try:
        result = subprocess.run(
            [python_path, script_path, query],
            capture_output=True,
            text=True,
            cwd=project_root,
            check=True
        )
        data = json.loads(result.stdout)
        return data
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr or str(e)}
    except json.JSONDecodeError:
        return {"success": False, "error": f"Invalid JSON returned:\n{result.stdout}"}
