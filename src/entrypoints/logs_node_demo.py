import asyncio

from orchestration.nodes import call_logs_node
from orchestration.state import State


async def main():
    state: State = {
        "user_message": "Existe algum erro recorrente no payment-service?",
        "inference_result": "",
    }
    result = await call_logs_node(state)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
