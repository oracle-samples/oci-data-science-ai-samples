import os
import ads
from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import requests
import asyncio

ads.set_auth("resource_principal")

TARGET = os.getenv("TARGET", None)
TIMEOUT = "10"


app = FastAPI()

def build_signer():
    """
    Retrives the signer from resource_principal.
    """
    return ads.auth.default_signer()["signer"]

@app.get("/{full_path:path}")
async def proxy_get(full_path: str, request: Request):
    """
    Forwards all request to the upstream while adding OCI request signature.
    """
    target = f"{TARGET.rstrip("/")}/"
    signer = build_signer()

    # Use httpx for async; httpx supports requests-compatible auth via "auth=signer"
    headers = dict(request.headers)
    # Prometheus usually sends Accept: text/plain; keep it, but drop hop-by-hop headers
    for h in ["host", "connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"]:
        headers.pop(h, None)

    try:
        async with httpx.AsyncClient() as client:
            def sync_fetch():
                r = requests.get(target, headers=headers, auth=signer, stream=True, timeout=TIMEOUT)
                r.raise_for_status()
                return r

            r = await asyncio.get_event_loop().run_in_executor(None, sync_fetch)
            content = r.raw.read()  # stream -> bytes
                        
            # Pass through upstream content-type and content-encoding;
            headers={
                "content-type": r.headers.get("content-type", "text/plain; version=0.0.4; charset=utf-8; escaping=underscores"),
                "content-encoding": "gzip",
            }
            
            return Response(content, status_code=r.status_code, media_type=None, headers=headers)
    except Exception:
        raise

@app.get("/healthz")
def healthz():
    return {"ok": True}
