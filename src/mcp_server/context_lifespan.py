import asyncpg
from dataclasses import dataclass
@dataclass
class LifespanContext:
    """
    LifespanContext é um dataclass que mantém o contexto para o tempo de vida de uma aplicação.
    """
    pool: asyncpg.Pool
    