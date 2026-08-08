import openai_service_client

TERMOS = ["Circuit Breaker", "Padrão de Retentativa", "Sagas"]

def get_embeddings():
    return {
        termo: openai_service_client.get_embedding(termo)
        for termo in TERMOS
    }
