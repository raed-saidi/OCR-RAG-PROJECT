# src/ocr/rag_pipeline.py
import os
import sys
from Retriever import Retriever
from groq import Groq

class RAGPipeline:
    def __init__(self, api_key=None):
        """
        Initialize RAG pipeline with Groq
        
        Args:
            api_key: Groq API key (if None, reads from GROQ_API_KEY env var)
        """
        self.retriever = Retriever()
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Groq API key required. Set GROQ_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        self.client = Groq(api_key=self.api_key)
        # Using Llama 3.3 70B - best balance of speed and quality
        self.model = "llama-3.3-70b-versatile"

    def generate_answer(self, query, k=3, max_context_chars=4000):
        """
        Generate answer using RAG with Groq
        
        Args:
            query: User question
            k: Number of documents to retrieve
            max_context_chars: Maximum context length
        
        Returns:
            dict with success, answer, and documents
        """
        try:
            # Retrieve relevant documents
            paths, distances, texts = self.retriever.search_with_texts(query, k=k)
            
            print(f"[INFO] Retrieved {len(paths)} documents", file=sys.stderr)

            # Build context from retrieved documents
            context = ""
            for i, text in enumerate(texts):
                doc_name = os.path.basename(paths[i])
                # Add document with clear separator
                doc_snippet = text[:1000].strip()
                if len(context) + len(doc_snippet) > max_context_chars:
                    break
                context += f"\n--- Document {i+1}: {doc_name} ---\n{doc_snippet}\n"

            if not context.strip():
                return {
                    "success": False,
                    "error": "No relevant documents found",
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "documents": []
                }

            # Create prompt for Groq
            system_prompt = """You are a helpful AI assistant that answers questions based on provided documents. 
Your task is to:
1. Read the context from the documents carefully
2. Answer the user's question based ONLY on the information in the documents
3. If the documents don't contain enough information, say so clearly
4. Be concise but complete in your answer
5. Cite which document(s) you used when relevant"""

            user_prompt = f"""Context from documents:
{context}

Question: {query}

Please provide a clear and accurate answer based on the context above."""

            # Call Groq API
            print(f"[INFO] Calling Groq API with model {self.model}", file=sys.stderr)
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.3,  # Lower temperature for more focused answers
                max_tokens=500,
                top_p=0.9
            )

            answer = chat_completion.choices[0].message.content.strip()

            # Prepare document metadata
            documents = []
            for i, (p, d, t) in enumerate(zip(paths, distances, texts)):
                try:
                    score = float(d)
                except:
                    score = 0.0
                
                documents.append({
                    "path": os.path.basename(p),
                    "full_path": p,
                    "score": round(score, 4),
                    "text": t[:300] + "..." if len(t) > 300 else t,
                    "rank": i + 1
                })

            print(f"[INFO] Generated answer successfully", file=sys.stderr)

            return {
                "success": True,
                "answer": answer,
                "documents": documents,
                "model": self.model,
                "num_docs_used": len(documents)
            }

        except Exception as e:
            import traceback
            error_msg = str(e)
            trace = traceback.format_exc()
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            print(trace, file=sys.stderr)
            
            return {
                "success": False,
                "error": error_msg,
                "traceback": trace
            }