import environment_setting
import openai_service_client
import rag
import vector_store_mock

def main():
    print("OPENAI-KEY carregada:", "***" + environment_setting.OPENAI_API_KEY[-4:])
    print("LANGSMITH-KEY carregada:", "***" + environment_setting.LANGSMITH_API_KEY[-4:])

    query_embedding = openai_service_client.get_embedding("estratégias de resiliência em microserviços")

    stored_embeddings = vector_store_mock.get_embeddings()

    print("Stored embeddings:", {termo: emb for termo, emb in stored_embeddings.items()})

    top_indices = rag.search_for_embedding(query_embedding, stored_embeddings, 1)

    print("Top indices:", top_indices)

if __name__ == "__main__":
    main()