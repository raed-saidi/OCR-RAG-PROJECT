from retriever import Retriever
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# Charger le modèle local
model_id = "openai/gpt-oss-20b"  # ou "togethercomputer/GPT-NeoXT-Chat-Base-20B"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,   # utilise float16 pour économiser de la VRAM
)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Créer un pipeline Transformers pour génération
text_gen = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if device=="cuda" else -1,
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
)

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()

    def generate_answer(self, query, k=3, max_context_chars=3000):
        # Récupérer les top-k documents
        paths, distances, texts = self.retriever.search_with_texts(query, k=k)

        # Construire le contexte
        context = ""
        for t in texts:
            if len(context) + len(t) > max_context_chars:
                break
            context += t + "\n"

        # Créer le prompt
        prompt = f"Réponds à la question suivante en te basant uniquement sur le contexte ci-dessous.\n\nCONTEXTE:\n{context}\n\nQUESTION:\n{query}\n\nRéponse:"

        # Générer la réponse
        output = text_gen(prompt, max_new_tokens=256)
        answer = output[0]["generated_text"]

        return answer, paths, distances

# Test
if __name__ == "__main__":
    pipeline_rag = RAGPipeline()
    query = input("🔎 Enter your question: ")
    answer, paths, distances = pipeline_rag.generate_answer(query)
    print("\nRéponse générée :\n", answer)
    print("\nDocuments utilisés :")
    for p, d in zip(paths, distances):
        print(f"{p} (score={d:.2f})")
