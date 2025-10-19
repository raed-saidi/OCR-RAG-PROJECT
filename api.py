from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
import subprocess
import os
import json

load_dotenv()

app = FastAPI(
    title="OCR-RAG API with Groq",
    description="Document Q&A using OCR and Groq LLM",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    k: Optional[int] = Field(3, ge=1, le=10)

class Document(BaseModel):
    path: str
    full_path: str
    score: float
    text: str
    rank: int

class QueryResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    documents: Optional[list[Document]] = None
    model: Optional[str] = None
    num_docs_used: Optional[int] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "OCR-RAG API",
        "groq_configured": bool(os.environ.get("GROQ_API_KEY"))
    }

@app.get("/health")
async def health():
    project_root = os.path.dirname(os.path.abspath(__file__))
    return {
        "api": "healthy",
        "groq_key_set": bool(os.environ.get("GROQ_API_KEY")),
        "rag_script": os.path.exists(os.path.join(project_root, "src", "ocr", "call_rag.py")),
        "faiss_index": os.path.exists(os.path.join(project_root, "data", "faiss", "index.faiss"))
    }

@app.post("/rag", response_model=QueryResponse)
async def rag_endpoint(request: QueryRequest):
    if not os.environ.get("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

    project_root = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(project_root, "src", "ocr", "call_rag.py")
    
    if not os.path.exists(script_path):
        raise HTTPException(status_code=500, detail="RAG script not found")

    # Determine Python executable
    python_path = os.path.join(project_root, ".venv", "Scripts", "python.exe")
    if not os.path.exists(python_path):
        python_path = os.path.join(project_root, ".venv", "bin", "python")
        if not os.path.exists(python_path):
            python_path = "python"

    try:
        result = subprocess.run(
            [python_path, script_path, request.query, str(request.k)],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=60,
            check=True
        )
        data = json.loads(result.stdout)
        return QueryResponse(**data)
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Request timed out")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e.stderr or str(e)}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)