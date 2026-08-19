from numpy import dot
from numpy.linalg import norm
from . import openai_embedding_service_client
from . import vector_store_mock as vector_store_mock

def cosine_similarity(a, b):
    linalg_a = norm(a)
    linalg_b = norm(b)
    if linalg_a == 0 or linalg_b == 0:
        return 0.0
    return dot(a, b) / (linalg_a * linalg_b)

def search_for_embedding(query_embedding, embeddings, top_k=5):
    similarities = []
    for termo, emb in embeddings.items():
        #print(f"Termo: {termo}, Embedding: {emb}")
        similarity = cosine_similarity(query_embedding, emb)
        print(f"Similaridade entre a consulta e '{termo}': {similarity}")
        similarities.append((termo, similarity))
    top_tuples = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

    return top_tuples

def search(user_query):
    query_embedding = openai_embedding_service_client.get_embedding(user_query)
    stored_embeddings = vector_store_mock.get_embeddings()
    top_indices = search_for_embedding(
        query_embedding, 
        stored_embeddings, 
        top_k=1
    )

    return top_indices