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
logger.info(f'predict_endpoint: {predict_endpoint}')

# -------------- OpenAI Client Init -----------------
custom_oci_openai = MultiInferOpenAI(
    oci_signer=signer,
    api_key='',
    base_url=predict_endpoint
)

# Chat Completions
response = custom_oci_openai.chat.completions.create(
    model='/opt/ds/model/deployed_model',
    messages=[
        {"role": "system", "content": "You are a helpful assistant working in Oracle Cloud Infrastructure."},
        {"role": "user", "content": "Tell me the most interesting fact about your time working at OCI."}
    ],
    max_tokens=500
)

# Models List
models = custom_oci_openai.models.list()
for model in models:
    logger.info(f'Model: {model.id}')

print('-----------------------------------')
print(f'Completions Response received: {response}')
print('-----------------------------------')


