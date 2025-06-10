from common.connection import RedisConnectionManager
from redis.exceptions import RedisError
from common.server import mcp

@mcp.tool()
async def lpush(name: str, value: str, expire: int = None) -> str:
    """Push a value onto the left of a Redis list and optionally set an expiration time."""
    try:
        r = RedisConnectionManager.get_connection()
        r.lpush(name, value)
        if expire:
            r.expire(name, expire)
        return f"Value '{value}' pushed to the left of list '{name}'."
    except RedisError as e:
        return f"Error pushing value to list '{name}': {str(e)}"

@mcp.tool()
async def rpush(name: str, value: str, expire: int = None) -> str:
    """Push a value onto the right of a Redis list and optionally set an expiration time."""
    try:
        r = RedisConnectionManager.get_connection()
        r.rpush(name, value)
        if expire:
            r.expire(name, expire)
        return f"Value '{value}' pushed to the right of list '{name}'."
    except RedisError as e:
        return f"Error pushing value to list '{name}': {str(e)}"

@mcp.tool()
async def lpop(name: str) -> str:
    """Remove and return the first element from a Redis list."""
    try:
        r = RedisConnectionManager.get_connection()
        value = r.lpop(name)
        return value if value else f"List '{name}' is empty or does not exist."
    except RedisError as e:
        return f"Error popping value from list '{name}': {str(e)}"

@mcp.tool()
async def rpop(name: str) -> str:
    """Remove and return the last element from a Redis list."""
    try:
        r = RedisConnectionManager.get_connection()
        value = r.rpop(name)
        return value if value else f"List '{name}' is empty or does not exist."
    except RedisError as e:
        return f"Error popping value from list '{name}': {str(e)}"

@mcp.tool()
async def lrange(name: str, start: int, stop: int) -> list:
    """Get elements from a Redis list within a specific range."""
    try:
        r = RedisConnectionManager.get_connection()
        values = r.lrange(name, start, stop)
        return [v for v in values] if values else f"List '{name}' is empty or does not exist."
    except RedisError as e:
        return f"Error retrieving values from list '{name}': {str(e)}"

@mcp.tool()
async def llen(name: str) -> int:
    """Get the length of a Redis list."""
    try:
        r = RedisConnectionManager.get_connection()
        return r.llen(name)
    except RedisError as e:
        return f"Error retrieving length of list '{name}': {str(e)}"
