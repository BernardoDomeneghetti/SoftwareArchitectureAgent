from mcp.server.mcpserver import MCPServer
from contextlib import asynccontextmanager
from .context_lifespan import LifespanContext
from environment_setting import POSTGRES_CONNECTION_STRING
import asyncpg

@asynccontextmanager
async def lifespan(server: MCPServer):
    pool = await asyncpg.create_pool(POSTGRES_CONNECTION_STRING)
    try:
        yield LifespanContext(pool=pool)
    finally:
        await pool.close()

mcp = MCPServer(lifespan=lifespan, name="LogsQueryServer")