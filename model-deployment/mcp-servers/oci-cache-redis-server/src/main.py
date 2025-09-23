import sys

from common.connection import RedisConnectionManager
import tools.server_management
import tools.misc 
import tools.redis_query_engine
import tools.hash
#import tools.list
#import tools.string
#import tools.json
#import tools.sorted_set
#import tools.set
#import tools.stream
#import tools.pub_sub
from common.server import mcp
from common.config import MCP_TRANSPORT, MCP_HOST, MCP_PORT


class RedisMCPServer:
    def __init__(self):
        print("Starting the Redis MCP Server", file=sys.stderr)

    def run(self):
        mcp.run(transport=MCP_TRANSPORT)

def main():
    server = RedisMCPServer()
    server.run()

if __name__ == "__main__":
    main()
