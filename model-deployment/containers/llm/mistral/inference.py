import oci
import json
import requests
import sys
import os
import argparse
import yaml
import string
from loguru import logger


app_config = yaml.load(open("config.yaml"), Loader=yaml.SafeLoader)

profile = app_config["oci"]["profile"]

config = oci.config.from_file(
    "~/.oci/config", profile_name=profile
)  # replace with the location of your oci config file

model = os.environ.get("MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
template_file = app_config["models"][model].get("template")
prompt_template = string.Template(
    open(template_file).read() if template_file else "$prompt"
)

logger.info(f"Setting prompt template to: {prompt_template}")

endpoint = app_config["models"][model]["endpoint"]

SECURITY_TOKEN_GENERIC_HEADERS = ["date", "(request-target)", "host"]
SECURITY_TOKEN_BODY_HEADERS = ["content-length", "content-type", "x-content-sha256"]
SECURITY_TOKEN_REQUIRED = ["security_token_file", "key_file", "region"]


headers = {}  # header goes here


def parse_args():
    parser = argparse.ArgumentParser(description="prompt")
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="LLM prompt.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        required=False,
        default=200,
        help="LLM maximum tokens.",
    )
    return parser.parse_args()


def create_security_token_signer():
    auth = oci.auth.signers.SecurityTokenSigner(
        token=open(os.path.expanduser(f"~/.oci/sessions/{profile}/token")).read(),
        private_key=oci.signer.load_private_key_from_file(
            os.path.expanduser(f"~/.oci/sessions/{profile}/oci_api_key.pem")
        ),
        generic_headers=SECURITY_TOKEN_GENERIC_HEADERS,
        body_headers=SECURITY_TOKEN_BODY_HEADERS,
    )

    return auth


def create_default_signer():
    config = oci.config.from_file(
        "~/.oci/config"
    )  # replace with the location of your oci config file

    auth = oci.signer.Signer(
        tenancy=config["tenancy"],
        user=config["user"],
        fingerprint=config["fingerprint"],
        private_key_file_location=config["key_file"],
        pass_phrase=config["pass_phrase"],
    )

    return auth


def query(prompt, max_tokens=200, **kwargs):
    body = {
        "inputs": prompt_template.substitute({"prompt": prompt}),
        "parameters": {
            "max_new_tokens": max_tokens,
            "return_full_text": False,
            "watermark": True,
            "seed": 42,
            **kwargs,
        },
    }

    if os.environ.get("VLLM"):
        if  os.environ.get("API_SPEC")=="openai":
            temperature = kwargs.get('temperature',0.7)
            top_p = kwargs.get('top_p',0.8)
            body = {
                        "prompt": prompt_template.substitute({"prompt": prompt}),
                        "max_tokens": max_tokens,
                        "model": model,
                        "temperature": temperature,
                        "top_p":top_p 
                    }
        else:
            body["parameters"].pop("watermark", None)
            body["parameters"].pop("seed", None)
            body["parameters"].pop("return_full_text", None)

    # create auth using one of the oci signers
    auth = create_default_signer()
    data = requests.post(endpoint, json=body, auth=auth, headers=headers).json()
    # return model generated response, or any error as a string
    if os.environ.get("VLLM"):
        if os.environ.get("API_SPEC")=="openai":
            response_text_key = "choices"
            response =  data.get(response_text_key, data)[0]
            response = response.get("text", data)
    else:
        response_text_key = 'generated_text'
        response =  data.get(response_text_key, data)
    return str(response)


if __name__ == "__main__":
    args = parse_args()
    print(query(args.prompt, args.max_tokens))
