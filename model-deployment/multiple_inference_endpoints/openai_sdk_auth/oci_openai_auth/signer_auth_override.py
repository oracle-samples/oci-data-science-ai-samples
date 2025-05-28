import oci
from oci.signer import Signer
import httpx
from openai._base_client import BaseClient
from openai import OpenAI
import requests
import logging
import sys
from email.utils import formatdate
import time
import hashlib
import base64
import json


# Configure logging
logger = logging.getLogger(__name__)

# Set to DEBUG to see detailed logs, INFO for standard logs
DEBUG_MODE = True  # Toggle this to True/False to enable/disable debug logs
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
    # Also set console handler to DEBUG to see debug messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

# Create console handler with formatting
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# -------------- Get oci signer -----------------
config = oci.config.from_file(profile_name='default')
token_file = config['security_token_file']
token = None
with open(token_file, 'r') as f:
    token = f.read()
private_key = oci.signer.load_private_key_from_file(config['key_file'])
signer = oci.auth.signers.SecurityTokenSigner(token, private_key)



# Custom auth class
class MyCustomAuth(httpx.Auth):
    def __init__(self, signer):
        self.signer = signer

    def auth_flow(self, request):
        logger.debug("Starting custom auth flow")

        required_headers = {
            **dict(request.headers),
        }

        # Convert httpx.Request to requests.PreparedRequest
        req = requests.Request(
            method=request.method,
            url=str(request.url),
            headers=required_headers,
            data=request.content  # Use content to ensure consistency
        )

        prepared = req.prepare()
        logger.debug(f'Prepared URL: {prepared.url}')
        
        # Log headers at debug level
        for k, v in prepared.headers.items():
            logger.debug(f'OpenAI default header ➡️: {k}: {v}')

        # Sign the request using the signer
        signed_prepared = self.signer(prepared)

        # Update httpx.Request with signed headers and body
        request.headers.clear()  # Clear existing headers
        request.headers.update(signed_prepared.headers)
        
        # Always set Content-Length header
        if signed_prepared.body:
            request.stream = httpx.ByteStream(signed_prepared.body)  # Use ByteStream to set the body
            if 'content-length' not in request.headers:
                request.headers['content-length'] = str(len(signed_prepared.body))
        else:
            # For requests without body (like GET), set Content-Length to 0
            request.headers['content-length'] = '0'
        
        logger.debug(f'Signed prepared URL: {signed_prepared.url}')
        # Log signed headers at debug level
        for k, v in request.headers.items():
            logger.debug(f'Custom OCI signed header ⬅️: {k}: {v}')

        yield request

# Custom openai class
class MultiInferOpenAI(OpenAI):
    def __init__(self, oci_signer, *args, **kwargs):
        kwargs['http_client'] = httpx.Client(verify=False)  # Disable SSL verification for local testing (TODO: remove this for prod)
        super().__init__(*args, **kwargs)
        self.signer = oci_signer
    
    @property
    def custom_auth(self) -> httpx.Auth | None:
        return MyCustomAuth(self.signer)
