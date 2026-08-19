from mcp.server.mcpserver import MCPServer
from contextlib import asynccontextmanager
from .context_lifespan import LifespanContext
from environment_setting import POSTGRES_CONNECTION_STRING
import asyncpg

@asynccontextmanager
async def lifespan(server: MCPServer):
    print("Starting MCP server...")
    pool = await asyncpg.create_pool(POSTGRES_CONNECTION_STRING)
    print("Database connection pool created.")
    try:
        print("Yielding LifespanContext...")
        yield LifespanContext(pool=pool)
    finally:
        print("Closing database connection pool...")
        await pool.close()
        print("Database connection pool closed.")

mcp = MCPServer(lifespan=lifespan, name="LogsQueryServer")