from dotenv import load_dotenv
import os

load_dotenv()

def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variável de ambiente obrigatória ausente: {name}")
    return value

OPENAI_API_KEY = _required("OPENAI_API_KEY")
LANGSMITH_API_KEY = _required("LANGSMITH_API_KEY")
POSTGRES_CONNECTION_STRING = _required("POSTGRES_CONNECTION_STRING")