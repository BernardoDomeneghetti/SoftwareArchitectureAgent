from mcp.client import Client
from mcp.client.stdio import StdioServerParameters, stdio_client
from .state import State
from rag.rag_search import search
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent

def call_rag_node(state: State) -> dict:
    """
    Busca no RAG o termo mais relevante para a mensagem do usuário.

    Args:
        state (State): estado atual da orquestração.

    Returns:
        dict: atualização parcial do State, com a chave "rag_response".
    """
    rag_answer = search(state['user_message'])[0]
    rag_term = rag_answer[0]

    result = {'rag_response': [rag_term]}
    
    return result

async def call_logs_node (state: State)-> dict:
    params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "entrypoints.logs_query_mcp_demo"],
        cwd=SRC_DIR,
    )
    
    transport = stdio_client(params)

    async with Client(transport) as conn:
        tool_result = await conn.call_tool("query_logs", {})
        return {"related_logs": tool_result.structured_content["result"]}