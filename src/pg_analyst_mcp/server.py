from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pg-analyst")


@mcp.tool()
def ping() -> str:
    """Health check. Returns 'pong'. Use it to confirm the server is reachable."""
    return "pong"


if __name__ == "__main__":
    mcp.run()
