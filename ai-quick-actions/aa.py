import requests
import oci

config = oci.config.from_file(
    "~/.oci/config"
)  # replace with the location of your oci config file
token_file = config["security_token_file"]
token = None
with open(token_file, "r") as f:
    token = f.read()
private_key = oci.signer.load_private_key_from_file(config["key_file"])
signer = oci.auth.signers.SecurityTokenSigner(token, private_key)


endpoint = "https://modeldeployment-int.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeploymentint.oc1.iad.xxxxxxxxx/predict"
body = {
    "model": "odsc-llm",
    "prompt": "what are activation functions?",
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
}
headers = {}  # header goes here

res = requests.post(endpoint, json=body, auth=signer, headers={}).json()

print(res)
