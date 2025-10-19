import os
import numpy as np
from Retriever import Retriever  # note lowercase
from transformers import pipeline

# Modèle GPT-2
text_gen = pipeline(
    "text-generation",
    model="gpt2",
    device="cpu",
    max_length=512
)


class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.text_gen = text_gen

    def generate_answer(self, query, k=3, max_context_chars=2000):
        try:
            # Récupération des documents
            paths, distances, texts = self.retriever.search_with_texts(query, k=k)

            # Construire le contexte
            context = ""
            for t in texts:
                if len(context) + len(t) > max_context_chars:
                    break
                context += t[:500] + "\n"

            prompt = f"Question: {query}\n\nContext: {context}\n\nAnswer:"

            # Génération GPT-2
            outputs = self.text_gen(
                prompt,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True,
                pad_token_id=50256,
                truncation=True
            )

            answer = outputs[0]["generated_text"]
            if "Answer:" in answer:
                answer = answer.split("Answer:")[-1].strip()
            else:
                answer = answer.replace(prompt, "").strip()

            # Construire documents avec score float
            documents = []
            for p, d in zip(paths, distances):
                try:
                    score = float(d)
                except Exception as e:
                    score = 0.0
                documents.append({
                    "path": os.path.basename(p),
                    "full_path": p,
                    "score": score
                })

            return {
                "success": True,
                "answer": answer,
                "documents": documents
            }

        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

