import os
import sys
from Retriever import Retriever
from groq import Groq

class RAGPipeline:
    def __init__(self, api_key=None):
        self.retriever = Retriever()
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("Groq API key required. Set GROQ_API_KEY environment variable")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"

    def generate_answer(self, query, k=3, max_context_chars=4000):
        try:
            paths, distances, texts = self.retriever.search_with_texts(query, k=k)
            print(f"[INFO] Retrieved {len(paths)} documents", file=sys.stderr)

            # Build context
            context = ""
            for i, text in enumerate(texts):
                doc_name = os.path.basename(paths[i])
                doc_snippet = text[:1000].strip()
                if len(context) + len(doc_snippet) > max_context_chars:
                    break
                context += f"\n--- Document {i+1}: {doc_name} ---\n{doc_snippet}\n"

            if not context.strip():
                return {
                    "success": False,
                    "error": "No relevant documents found",
                    "answer": "No relevant information found.",
                    "documents": []
                }

            # Groq API call
            system_prompt = """You are an AI assistant that answers questions based on provided documents.
1. Answer only from the document context
2. Be concise but complete
3. Cite which document(s) you used
4. If information is insufficient, state it clearly"""

            user_prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nProvide a clear answer based on the context."

            print(f"[INFO] Calling Groq API with {self.model}", file=sys.stderr)
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=500,
                top_p=0.9
            )

            answer = chat_completion.choices[0].message.content.strip()

            # Prepare response
            documents = []
            for i, (p, d, t) in enumerate(zip(paths, distances, texts)):
                documents.append({
                    "path": os.path.basename(p),
                    "full_path": p,
                    "score": round(float(d), 4),
                    "text": t[:300] + "..." if len(t) > 300 else t,
                    "rank": i + 1
                })

            print(f"[INFO] Answer generated successfully", file=sys.stderr)

            return {
                "success": True,
                "answer": answer,
                "documents": documents,
                "model": self.model,
                "num_docs_used": len(documents)
            }

        except Exception as e:
            import traceback
            print(f"[ERROR] {str(e)}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }