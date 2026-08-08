from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    linalg_a = norm(a)
    linalg_b = norm(b)
    if linalg_a == 0 or linalg_b == 0:
        return 0.0
    return dot(a, b) / (linalg_a * linalg_b)

def search_for_embedding(query_embedding, embeddings, top_k=5):
    similarities = []
    for termo, emb in embeddings.items():
        print(f"Termo: {termo}, Embedding: {emb}")
        similarity = cosine_similarity(query_embedding, emb)
        print(f"Similaridade entre a consulta e '{termo}': {similarity}")
        similarities.append((termo, similarity))
    top_indices = [termo for termo in sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]]

    return top_indices