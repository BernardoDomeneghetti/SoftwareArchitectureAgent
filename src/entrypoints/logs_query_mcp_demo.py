from mcp_server.mcp_server_provider import mcp
import mcp_server.logs_mcp # noqa: F401

def main():
    mcp.run()

if __name__ == "__main__":
    main()