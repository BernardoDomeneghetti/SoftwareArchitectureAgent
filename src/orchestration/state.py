from typing import NotRequired, TypedDict

class State(TypedDict):
    """
    Represents the state of the orchestration process, including user messages, RAG responses, related logs, and inference results. 
    """
    user_message: str
    rag_response: NotRequired[list[str]|None]
    related_logs: NotRequired[list[dict]|None]
    inference_result: str