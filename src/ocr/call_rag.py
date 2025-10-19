import sys
import json
import os

# Ajouter le dossier courant au path pour importer rag_pipeline
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_pipeline import RAGPipeline

def main():
    # Vérifier qu'une question est passée
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: python call_rag.py <question>"}))
        sys.exit(1)

    query = sys.argv[1]

    # Logs sur stderr pour debug
    print(f"[INFO] Début de l'exécution du pipeline RAG", file=sys.stderr)
    print(f"[INFO] Question: {query}", file=sys.stderr)

    try:
        pipeline_rag = RAGPipeline()
        result = pipeline_rag.generate_answer(query)  # dict {success, answer, documents}

        if not result.get("success", False):
            raise Exception(result.get("error", "Erreur inconnue"))

        # Formater la réponse uniquement en JSON
        response = {
            "success": True,
            "answer": result.get("answer", ""),
            "documents": result.get("documents", [])
        }

        # Le print final → stdout, que Next.js va parser
        print(json.dumps(response, ensure_ascii=False))

    except Exception as e:
        # Erreur capturée → JSON sur stdout
        response = {
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }
        print(json.dumps(response))
        sys.exit(1)

if __name__ == "__main__":
    main()
