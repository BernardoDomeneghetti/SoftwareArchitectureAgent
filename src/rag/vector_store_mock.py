from . import openai_embedding_service_client

TERMOS = ["Circuit Breaker", "Padrão de Retentativa", "Sagas"]

def get_embeddings():
    return {
        termo: openai_embedding_service_client.get_embedding(termo)
        for termo in TERMOS
    }
