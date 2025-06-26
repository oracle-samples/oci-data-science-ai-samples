from mcp.server.fastmcp import FastMCP
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
    dependencies=["redis", "dotenv", "numpy"]
)

mcp._session_manager = StreamableHTTPSessionManager(
        app=mcp._mcp_server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

def handle_health(request):
        return JSONResponse({"status": "success"})

async def handle_streamable_http(
    scope: Scope, receive: Receive, send: Send
) -> None:
    await mcp._session_manager.handle_request(scope, receive, send)

mcp._custom_starlette_routes=[
            Mount("/mcp", app=handle_streamable_http),
            Route('/health', endpoint=handle_health),
        ]