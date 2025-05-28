import oci
import logging
from oci_openai_auth.signer_auth_override import MultiInferOpenAI

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_oci_signer():
    # Get oci signer
    config = oci.config.from_file(profile_name='default')
    token_file = config['security_token_file']
    token = None
    with open(token_file, 'r') as f:
        token = f.read()
    private_key = oci.signer.load_private_key_from_file(config['key_file'])
    signer = oci.auth.signers.SecurityTokenSigner(token, private_key)
    return signer

signer = get_oci_signer()


# -------------- Getting paths ready -----------------
ssl = True
mdocid = '<your-model-deployment-ocid>'
predict_endpoint = f'https://localhost:8888/{mdocid}/predict/v1' if ssl else f'http://localhost:8888/{mdocid}/predict/v1'
predict_streaming_endpoint = f'https://localhost:8888/{mdocid}/predictWithResponseStream/v1' if ssl else f'http://localhost:8888/{mdocid}/predictWithResponseStream/v1'
print(f'predict_endpoint: {predict_endpoint}')
print(f'predict_streaming_endpoint: {predict_streaming_endpoint}')

# -------------- OpenAI Client Init -----------------
custom_oci_openai = MultiInferOpenAI(
    oci_signer=signer,
    api_key='',
    base_url=predict_streaming_endpoint
)

# Chat Completions
response = custom_oci_openai.chat.completions.create(
    model='/opt/ds/model/deployed_model',
    messages=[
        {"role": "user", "content": "Write a big essay on the history of Oracle Cloud Infrastructure."}
    ],
    stream=True, # -> False
    max_tokens=1000
)

full_response = ""
for chunk in response:
    delta = chunk.choices[0].delta.content
    if delta:
        full_response += delta
        print(delta, end="", flush=True)

print('-----------------------------------')
print(f'Response received: {response}')
print('-----------------------------------')


