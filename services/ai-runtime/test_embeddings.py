
import math

from app.services.llm.embeddings import generate_embedding


sentences = [
    "Machine learning is a subset of artificial intelligence.",
    "AI includes machine learning as one of its important fields.",
    "I enjoy playing football on weekends."
]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))

    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))

    return dot_product / (magnitude_a * magnitude_b)


# Generate embeddings
vectors = [generate_embedding(sentence) for sentence in sentences]

# Compare sentence pairs
print("Sentence 1 vs Sentence 2:", cosine_similarity(vectors[0], vectors[1]))
print("Sentence 1 vs Sentence 3:", cosine_similarity(vectors[0], vectors[2]))
