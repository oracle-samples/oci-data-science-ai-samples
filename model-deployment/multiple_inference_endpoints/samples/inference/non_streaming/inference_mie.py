# The OCI SDK must be installed for this example to function properly.
# Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm
#
# Multiple Inference Endpoints (MIE): use the non-streaming predict prefix and your
# registered suffix (for example OpenAI chat completions):
#   POST https://<model-deployment-host>/<model-deployment-ocid>/predict/v1/chat/completions
# Replace <suffix> with the path your deployment exposes (framework or custom).

import requests
import oci
from oci.signer import Signer
from oci.config import from_file

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

endpoint = "https://<model-deployment-host>/<model-deployment-ocid>/predict/v1/chat/completions"
# Use your appropriate body here (schema depends on the route / container)
body = {
    "model":"odsc-llm",
    "prompt":"Who invented Internet",
     "max_tokens":5,
     "stream": False
}

headers={'Content-Type':'application/json', 'Accept': 'application/json'}
response = requests.post(endpoint, json=body, auth=auth, headers=headers)

print(response.headers)
print(response.json())
