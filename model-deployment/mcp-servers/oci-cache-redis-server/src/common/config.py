import urllib
from dotenv import load_dotenv
import os

load_dotenv()

MCP_TRANSPORT = os.getenv('MCP_TRANSPORT', 'stdio')
MCP_HOST = os.getenv('MCP_HOST', '0.0.0.0')
MCP_PORT = os.getenv('MCP_PORT', 8080)

REDIS_CFG = {"host": os.getenv('REDIS_HOST', '127.0.0.1'),
             "port": int(os.getenv('REDIS_PORT',6379)),
             "username": os.getenv('REDIS_USERNAME', None),
             "password": os.getenv('REDIS_PWD',''),
             "ssl": os.getenv('REDIS_SSL', False) in ('true', '1', 't'),
             "ssl_ca_path": os.getenv('REDIS_SSL_CA_PATH', None),
             "ssl_keyfile": os.getenv('REDIS_SSL_KEYFILE', None),
             "ssl_certfile": os.getenv('REDIS_SSL_CERTFILE', None),
             "ssl_cert_reqs": os.getenv('REDIS_SSL_CERT_REQS', 'required'),
             "ssl_ca_certs": os.getenv('REDIS_SSL_CA_CERTS', None),
             "cluster_mode": os.getenv('REDIS_CLUSTER_MODE', False) in ('true', '1', 't'),
             "db": int(os.getenv('REDIS_DB', 0))}


def generate_redis_uri():
    cfg = REDIS_CFG
    scheme = "rediss" if cfg.get("ssl") else "redis"
    host = cfg.get("host", "127.0.0.1")
    port = cfg.get("port", 6379)
    db = cfg.get("db", 0)

    username = cfg.get("username")
    password = cfg.get("password")

    # Auth part
    if username:
        auth_part = f"{urllib.parse.quote(username)}:{urllib.parse.quote(password)}@"
    elif password:
        auth_part = f":{urllib.parse.quote(password)}@"
    else:
        auth_part = ""

    # Base URI
    base_uri = f"{scheme}://{auth_part}{host}:{port}/{db}"

    # Additional SSL query parameters if SSL is enabled
    query_params = {}
    if cfg.get("ssl"):
        if cfg.get("ssl_cert_reqs"):
            query_params["ssl_cert_reqs"] = cfg["ssl_cert_reqs"]
        if cfg.get("ssl_ca_certs"):
            query_params["ssl_ca_certs"] = cfg["ssl_ca_certs"]
        if cfg.get("ssl_keyfile"):
            query_params["ssl_keyfile"] = cfg["ssl_keyfile"]
        if cfg.get("ssl_certfile"):
            query_params["ssl_certfile"] = cfg["ssl_certfile"]
        if cfg.get("ssl_ca_path"):
            query_params["ssl_ca_path"] = cfg["ssl_ca_path"]

    if query_params:
        base_uri += "?" + urllib.parse.urlencode(query_params)

    return base_uri