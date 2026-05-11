# The OCI SDK must be installed for this example to function properly.
# Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm
#
# Multiple Inference Endpoints (MIE): use the streaming predict prefix and the same path
# suffix as non-streaming, for example:
#   POST https://<model-deployment-host>/<model-deployment-ocid>/predictWithResponseStream/v1/chat/completions

import requests
import oci
from oci.signer import Signer
from oci.config import from_file
import sseclient # pip install sseclient-py

config = from_file('~/.oci/config')
auth = Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file'],
    pass_phrase=config['pass_phrase']
)

# For security token based authentication
# token_file = config['security_token_file']
# token = None
# with open(token_file, 'r') as f:
#     token = f.read()
# private_key = oci.signer.load_private_key_from_file(config['key_file'])
# auth = oci.auth.signers.SecurityTokenSigner(token, private_key)

endpoint = "https://<model-deployment-host>/<model-deployment-ocid>/predictWithResponseStream/v1/chat/completions"
# Use your appropriate body here (schema depends on the route / container)
body = {
    "model":"odsc-llm",
    "prompt":"Who invented Internet",
     "max_tokens":5,
     "stream": True
}

headers={'Content-Type':'application/json', 'Accept': 'text/event-stream'}
response = requests.post(endpoint, json=body, auth=auth, stream=True, headers=headers)

print(response.headers)

client = sseclient.SSEClient(response)
for event in client.events():
    print(event.data)

# Alternatively, we can use the below code to print the response.
# for line in response.iter_lines():
#    if line:
#        print(line)
