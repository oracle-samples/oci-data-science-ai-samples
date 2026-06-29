#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Delete an OCI Data Science model deployment on a Compute Target."""

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import oci
import oci.data_science as data_science
from oci.auth import signers
from oci.exceptions import ServiceError

LOGGER = logging.getLogger("delete_model_deployment_on_compute_target")


def load_sample_config(config_json: str) -> Dict[str, Any]:
    with open(Path(config_json).expanduser(), encoding="utf-8") as config_file:
        return json.load(config_file)


def create_data_science_client(sample_config: Dict[str, Any]):
    config_file = sample_config.get("config_file", "~/.oci/config")
    profile_name = sample_config.get("profile_name", "DEFAULT")
    config = oci.config.from_file(str(Path(config_file).expanduser()), profile_name)
    auth_type = sample_config.get("auth", "api_key").lower().replace("-", "_")
    if auth_type == "api_key":
        return data_science.DataScienceClient(config=config)

    if auth_type == "security_token":
        token_file = config.get("security_token_file")
        key_file = config.get("key_file")
        if not token_file or not key_file:
            raise ValueError(
                "Security token auth requires 'security_token_file' and 'key_file' in the selected OCI config profile."
            )
        token = Path(token_file).expanduser().read_text(encoding="utf-8").strip()
        private_key = oci.signer.load_private_key_from_file(
            str(Path(key_file).expanduser())
        )
        signer = signers.SecurityTokenSigner(token, private_key)
        return data_science.DataScienceClient(config=config, signer=signer)

    raise ValueError("'auth' must be 'api_key' or 'security_token'.")


def is_placeholder(value: Optional[str]) -> bool:
    return isinstance(value, str) and "<" in value and ">" in value


def require_value(value: Optional[str], field_name: str) -> None:
    if not value or is_placeholder(value):
        raise ValueError(
            f"Replace the placeholder value for '{field_name}' in the config JSON before running the sample."
        )


def validate_sample_config(sample_config: Dict[str, Any]) -> None:
    delete_config = sample_config["model_deployment_delete"]
    require_value(
        delete_config.get("model_deployment_id"),
        "model_deployment_delete.model_deployment_id",
    )


def print_payload(sample_config: Dict[str, Any]) -> None:
    delete_config = sample_config["model_deployment_delete"]
    print(
        json.dumps(
            {"model_deployment_id": delete_config["model_deployment_id"]},
            indent=2,
        )
    )


def delete_model_deployment(sample_config: Dict[str, Any]) -> None:
    delete_config = sample_config["model_deployment_delete"]
    client = create_data_science_client(sample_config)
    composite_client = data_science.DataScienceClientCompositeOperations(client)

    try:
        response = composite_client.delete_model_deployment_and_wait_for_state(
            model_deployment_id=delete_config["model_deployment_id"],
            wait_for_states=["SUCCEEDED", "FAILED"],
        )
    except ServiceError:
        LOGGER.exception("Failed to delete Model Deployment.")
        raise

    if response.data.status != "SUCCEEDED":
        raise RuntimeError(
            "Model Deployment delete did not succeed. "
            f"Work request status: {response.data.status}"
        )

    LOGGER.info("Deleted Model Deployment: %s", delete_config["model_deployment_id"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Delete a model deployment on a Managed Compute Cluster Compute Target."
    )
    parser.add_argument(
        "--config-json",
        default="config.json",
        help="Path to a config JSON file. Defaults to ./config.json.",
    )
    parser.add_argument(
        "--print-payload",
        action="store_true",
        help="Print the target resource OCID without calling OCI.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm that the model deployment should be deleted.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    sample_config = load_sample_config(args.config_json)
    validate_sample_config(sample_config)

    if args.print_payload:
        print_payload(sample_config)
        return

    if not args.yes:
        raise ValueError("Pass --yes to confirm Model Deployment deletion.")

    delete_model_deployment(sample_config)


if __name__ == "__main__":
    main()
