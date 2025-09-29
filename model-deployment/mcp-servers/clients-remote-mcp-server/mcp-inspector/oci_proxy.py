import hashlib
import base64
from datetime import datetime
from typing import Dict
from urllib.parse import urlparse, parse_qs

import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import oci
import requests

app = FastAPI(title="OCI Authentication Proxy", version="1.0.0")

class OCIAuthProxy:
    def __init__(self, config_profile: str = "DEFAULT"):
        """Initialize OCI configuration and signer"""
        try:
            # Load OCI config
            PROFILE_NAME = config_profile
            SECURITY_TOKEN_FILE_KEY = 'security_token_file'
            KEY_FILE_KEY = 'key_file'
            self.config = oci.config.from_file(profile_name=PROFILE_NAME)
            token_file = self.config[SECURITY_TOKEN_FILE_KEY]
            token = None
            with open(token_file, 'r') as f:
              token = f.read()
            private_key = oci.signer.load_private_key_from_file(self.config[KEY_FILE_KEY])
            self.signer = oci.auth.signers.SecurityTokenSigner(token, private_key, body_headers=["content-type", "x-content-sha256"]) 
        except Exception as e:
            raise Exception(f"Failed to initialize OCI config: {str(e)}")
    
    def _get_content_hash(self, body: bytes) -> str:
        """Generate SHA256 hash of request body"""
        return base64.b64encode(hashlib.sha256(body).digest()).decode('utf-8')
    
    def _prepare_headers(self, method: str, url: str, headers: Dict[str, str], body: bytes) -> Dict[str, str]:
        """Prepare headers for OCI authentication"""
        parsed_url = urlparse(url)
        
        # Required headers for OCI
        auth_headers = {
            'date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'host': parsed_url.netloc,
            '(request-target)': f"{method.lower()} {parsed_url.path}"
        }
        
        # Add query parameters to request-target if present
        if parsed_url.query:
            auth_headers['(request-target)'] += f"?{parsed_url.query}"
        
        # Add content headers for POST/PUT/PATCH requests
        if method.upper() in ['POST', 'PUT', 'PATCH'] and body:
            auth_headers['content-type'] = headers.get('content-type', 'application/json')
            auth_headers['content-length'] = str(len(body))
            auth_headers['x-content-sha256'] = self._get_content_hash(body)
        
        return auth_headers
    
    async def make_authenticated_request(
        self, 
        method: str, 
        target_url: str, 
        headers: Dict[str, str], 
        body: bytes = b''
    ) -> httpx.Response:
        """Make an authenticated request to OCI API"""
        
        request = requests.Request("POST", target_url, auth=self.signer, headers={'Content-Type': 'application/json', 'accept': 'application/json, text/event-stream'})
        prepared = request.prepare()
        del(prepared.headers['content-length'])
        
        # Prepare final headers
        final_headers = prepared.headers
        
        # Make the request
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=target_url,
                headers=final_headers,
                content=body
            )
        return response

# Global proxy instance
proxy = None

async def get_proxy() -> OCIAuthProxy:
    """Dependency to get or create proxy instance"""
    global proxy
    if proxy is None:
        try:
            proxy = OCIAuthProxy()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize OCI proxy: {str(e)}")
    return proxy

@app.on_event("startup")
async def startup_event():
    """Initialize the proxy on startup"""
    await get_proxy()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OCI Authentication Proxy"}

@app.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(
    request: Request, 
    path: str,
    target_host: str,
    proxy_instance: OCIAuthProxy = Depends(get_proxy)
):
    """
    Proxy requests to OCI with authentication
    
    Query Parameters:
    - target_host: The OCI service hostname (e.g., iaas.us-ashburn-1.oraclecloud.com)
    
    Example:
    GET /proxy/20160918/instances?target_host=iaas.us-ashburn-1.oraclecloud.com
    """
    
    if not target_host:
        raise HTTPException(
            status_code=400, 
            detail="target_host query parameter is required"
        )
    
    # Construct target URL
    scheme = "https"  # OCI APIs are always HTTPS
    query_string = str(request.url.query)
    
    # Remove target_host from query parameters for the actual request
    if query_string:
        query_params = parse_qs(query_string)
        if 'target_host' in query_params:
            del query_params['target_host']
        # Reconstruct query string
        query_parts = []
        for key, values in query_params.items():
            for value in values:
                query_parts.append(f"{key}={value}")
        query_string = "&".join(query_parts)
    
    target_url = f"{scheme}://{target_host}/{path}"
    if query_string:
        target_url += f"?{query_string}"
    
    # Get request body
    body = await request.body()
    
    # Get headers (excluding host and other proxy-specific headers)
    headers = dict(request.headers)
    
    try:
        # Make authenticated request
        response = await proxy_instance.make_authenticated_request(
            method=request.method,
            target_url=target_url,
            headers=headers,
            body=body
        )
        print(response)
        
        # Return response
        return JSONResponse(
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Request failed: {str(e)}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with usage instructions"""
    return {
        "message": "OCI Authentication Proxy",
        "usage": {
            "endpoint": "/proxy/{path}",
            "required_param": "target_host",
            "example": "/proxy/20160918/instances?target_host=iaas.us-ashburn-1.oraclecloud.com"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)