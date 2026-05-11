# Update model deployment MIE settings via the Data Science REST API (UpdateModelDeployment).
# Rolling update applies for active deployments. Body is loaded from update_model_deployment.json.
# Set MODEL_DEPLOYMENT_ID below, edit the JSON as needed, then run:
#   python update_model_deployment_rest.py
#
# Prerequisites: oci package, requests, and a configured ~/.oci/config profile.

from __future__ import annotations

import json
import sys
from pathlib import Path

import oci
import requests

CONFIG_PROFILE = "default"
MODEL_DEPLOYMENT_ID = (
    "ocid1.datasciencemodeldeployment.oc1.iad.amaaaaaav66vvniawqof2ppnqeocdyrkqto2ntkem2cbrm2fqebfx7cqmysq"
)
PAYLOAD_FILE = Path(__file__).resolve().parent / "update_model_deployment.json"


def build_signer(config: dict):
    if config.get("security_token_file"):
        with open(config["security_token_file"], encoding="utf-8") as f:
            token = f.read()
        private_key = oci.signer.load_private_key_from_file(config["key_file"])
        return oci.auth.signers.SecurityTokenSigner(token, private_key)
    return oci.signer.Signer(
        tenancy=config["tenancy"],
        user=config["user"],
        fingerprint=config["fingerprint"],
        private_key_file_location=config["key_file"],
        pass_phrase=config.get("pass_phrase"),
    )


def main() -> None:
    config = oci.config.from_file(profile_name=CONFIG_PROFILE)
    region = config.get("region")
    if not region:
        print("config is missing 'region'", file=sys.stderr)
        sys.exit(1)

    if not PAYLOAD_FILE.is_file():
        print(f"missing payload file: {PAYLOAD_FILE}", file=sys.stderr)
        sys.exit(1)

    body = json.loads(PAYLOAD_FILE.read_text(encoding="utf-8"))
    url = (
        f"https://datascience.{region}.oci.oraclecloud.com/20190101/"
        f"modelDeployments/{MODEL_DEPLOYMENT_ID}"
    )
    signer = build_signer(config)

    response = requests.put(
        url,
        json=body,
        auth=signer,
        headers={"Content-Type": "application/json"},
        timeout=120,
    )
    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    main()
