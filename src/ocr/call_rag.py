import sys
import json
import os
from dotenv import load_dotenv

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
load_dotenv(os.path.join(project_root, '.env'))

sys.path.insert(0, script_dir)
from rag_pipeline import RAGPipeline

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: python call_rag.py <question> [k]"}))
        sys.exit(1)

    query = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    print(f"[INFO] Question: {query}", file=sys.stderr)
    print(f"[INFO] Retrieving top {k} documents", file=sys.stderr)

    if not os.environ.get("GROQ_API_KEY"):
        print(json.dumps({
            "success": False,
            "error": "GROQ_API_KEY not set. Get your key at https://console.groq.com"
        }))
        sys.exit(1)

    try:
        pipeline = RAGPipeline()
        result = pipeline.generate_answer(query, k=k)

        if not result.get("success"):
            raise Exception(result.get("error", "Unknown error"))

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except FileNotFoundError as e:
        error_msg = str(e)
        if "index.faiss" in error_msg or "file_mapping" in error_msg:
            error_msg = "FAISS index not found. Run: embeddings.py → faiss_index.py"
        print(json.dumps({"success": False, "error": error_msg, "type": "FileNotFoundError"}))
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