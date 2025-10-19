# src/ocr/call_rag.py
import sys
import json
import os

# Load environment variables from .env file
from dotenv import load_dotenv

# Get project root and load .env
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_pipeline import RAGPipeline

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python call_rag.py <question> [k]"
        }))
        sys.exit(1)

    query = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    print(f"[INFO] Question: {query}", file=sys.stderr)
    print(f"[INFO] Retrieving top {k} documents", file=sys.stderr)

    try:
        # Check for Groq API key
        if not os.environ.get("GROQ_API_KEY"):
            print(json.dumps({
                "success": False,
                "error": "GROQ_API_KEY environment variable not set. "
                        "Get your API key at https://console.groq.com"
            }))
            sys.exit(1)

        # Initialize RAG pipeline
        pipeline_rag = RAGPipeline()
        
        # Generate answer
        result = pipeline_rag.generate_answer(query, k=k)

        if not result.get("success", False):
            raise Exception(result.get("error", "Unknown error"))

        # Output JSON to stdout (API will parse this)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except FileNotFoundError as e:
        error_msg = str(e)
        if "index.faiss" in error_msg or "file_mapping" in error_msg:
            error_msg = ("FAISS index not found. Please run embeddings.py "
                        "and faiss_index.py first to build the index.")
        print(json.dumps({
            "success": False,
            "error": error_msg,
            "type": "FileNotFoundError"
        }))
        sys.exit(1)

    except Exception as e:
        import traceback
        print(json.dumps({
            "success": False,
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()