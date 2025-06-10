import sys

from common.server import mcp
from common.config import MCP_TRANSPORT
from common.connection import RedisConnectionManager


class RedisMCPServer:
    def __init__(self):
        print("Starting the RedisMCPServer", file=sys.stderr)

    def run(self):
        print(f"🔧 Starting Redis MCP Server (transport={MCP_TRANSPORT})")
        mcp.run(transport=MCP_TRANSPORT)

if __name__ == "__main__":
    server = RedisMCPServer()
    server.run()
