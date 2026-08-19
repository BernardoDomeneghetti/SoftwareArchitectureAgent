import environment_setting
from rag import openai_embedding_service_client
import rag.vector_store_mock as vector_store_mock
import rag.rag_search as rag_search

def main():
    print("OPENAI-KEY carregada:", "***" + environment_setting.OPENAI_API_KEY[-4:])
    print("LANGSMITH-KEY carregada:", "***" + environment_setting.LANGSMITH_API_KEY[-4:])

    query_embedding = openai_embedding_service_client.get_embedding("estratégias de resiliência em microserviços")

    stored_embeddings = vector_store_mock.get_embeddings()

    print("Stored embeddings:", {termo: emb for termo, emb in stored_embeddings.items()})

    top_indices = rag_search.search_for_embedding(query_embedding, stored_embeddings, 1)

    print("Top indices:", top_indices)

if __name__ == "__main__":
    main()