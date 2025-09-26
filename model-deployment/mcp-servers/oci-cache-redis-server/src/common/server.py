from fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import Response
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.types import Receive, Scope, Send
from starlette.routing import Mount, Route

from common.config import MCP_PORT, MCP_HOST

# Initialize FastMCP server
mcp = FastMCP(
    "Redis MCP Server",
    host=MCP_HOST,
    port=MCP_PORT,
    dependencies=["redis", "dotenv", "numpy"],
    stateless_http=True,
    json_response=True
)

def handle_health(request):
        return JSONResponse({"status": "success"})

mcp._additional_http_routes = [
    Route('/health', endpoint=handle_health),
]