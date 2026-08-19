from datetime import datetime
from typing import Literal
from mcp.server.mcpserver import Context
from .mcp_server_provider import mcp

@mcp.tool()
async def query_logs(
    origin: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    level: Literal["INFO", "WARN", "ERROR", "TIMEOUT"] | None = None,
    message: str | None = None,
    ctx: Context = None,
) -> list[dict]:

    """Busca logs de aplicação dos microserviços para investigar erros, timeouts,
    lentidão ou qualquer comportamento anômalo relatado pelo usuário.

    Use esta tool sempre que precisar de evidência concreta de log antes de
    diagnosticar uma causa (ex: "por que o serviço X está lento", "houve falha
    no checkout ontem", "existe algum timeout recorrente"). Todos os filtros
    abaixo são opcionais — omita os que não forem relevantes para a pergunta;
    omitir um filtro significa "não restringir por esse campo".

    Args:
        origin: Nome exato do microserviço de origem do log (coluna `service`),
            ex: "payment-service". Omita se a pergunta não mencionar um serviço
            específico ou se não for possível identificar o nome exato.
        start_date: Início do período de busca (inclusive). Omita para não
            limitar o início do histórico.
        end_date: Fim do período de busca (inclusive). Omita para não limitar
            até o momento mais recente.
        level: Severidade do log — um entre "INFO", "WARN", "ERROR", "TIMEOUT".
            Omita para retornar logs de todos os níveis (útil para visão geral
            histórica).
        message: Texto livre a ser buscado dentro do conteúdo da mensagem de
            log (busca parcial, case-insensitive). Use para localizar termos
            específicos mencionados no problema relatado.

    Returns:
        Lista de entradas de log que atendem aos filtros informados, mais
        recentes primeiro.
    """
    pool = ctx.request_context.lifespan_context.pool

    conditions: list[str] = []
    params: list[object] = []
    param_index = 1

    if start_date is not None:
        conditions.append(f"created_at >= ${param_index}")
        params.append(start_date)
        param_index += 1

    if end_date is not None:
        conditions.append(f"created_at <= ${param_index}")
        params.append(end_date)
        param_index += 1

    if origin is not None:
        conditions.append(f"service = ${param_index}")
        params.append(origin)
        param_index += 1

    if level is not None:
        conditions.append(f"level = ${param_index}")
        params.append(level)
        param_index += 1

    if message is not None:
        conditions.append(f"message ILIKE ${param_index}")
        params.append(f"%{message}%")
        param_index += 1

    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    query = f"SELECT * FROM service_logs WHERE {where_clause} ORDER BY created_at DESC"

    rows = await pool.fetch(query, *params)

    return [dict(row) for row in rows]

@mcp.resource("resource://logs/table/schema")
def get_logs_table_schema() -> dict:
    """Retorna o esquema da tabela de logs de serviço, incluindo nomes de
    colunas e tipos de dados. Útil para entender a estrutura dos logs e
    construir consultas mais precisas.
    """
    return {
        "columns": [
            {"name": "id", "type": "INTEGER", "description": "Identificador único do log"},
            {"name": "service", "type": "TEXT", "description": "Serviço que gerou o log"},
            {"name": "level", "type": "TEXT", "description": "Nível de severidade do log"},
            {"name": "message", "type": "TEXT", "description": "Mensagem contida no conteúdo do log"},
            {"name": "created_at", "type": "TIMESTAMP", "description": "Data e hora de criação do log"},
            {"name": "origin", "type": "TEXT", "description": "Origem do log (Arquivo ou método que gerou o log)"},
            {"name": "duration_ms", "type": "INTEGER", "description": "Duração do log em milissegundos"},
            {"name": "correlation_id", "type": "UUID", "description": "Identificador de correlação do log"},

        ]
    }
