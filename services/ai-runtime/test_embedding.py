import time
from app.services.llm.embeddings import generate_embedding

start = time.time()

print("Testing Gemini embedding...")

embedding = generate_embedding("Axon PDF extraction test")

print("Embedding dimensions:", len(embedding))
print("Time taken:", round(time.time() - start, 2), "seconds")