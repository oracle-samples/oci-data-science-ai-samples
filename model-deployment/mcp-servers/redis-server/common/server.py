from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import Response

# Initialize FastMCP server
mcp = FastMCP(
    "Redis MCP Server",
    dependencies=["redis", "dotenv", "numpy"]
)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    return JSONResponse({"status": "ok"})

