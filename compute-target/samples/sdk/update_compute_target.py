#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Update OCI Data Science Compute Target metadata and tags."""

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import oci
import oci.data_science as data_science
from oci.auth import signers
from oci.data_science.models import UpdateComputeTargetDetails
from oci.exceptions import ServiceError

LOGGER = logging.getLogger("update_compute_target")


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


def prune_empty_values(value):
    if isinstance(value, dict):
        return {
            key: pruned
            for key, item in value.items()
            if (pruned := prune_empty_values(item)) not in (None, {}, [])
        }
    if isinstance(value, list):
        return [pruned for item in value if (pruned := prune_empty_values(item)) is not None]
    return value


def validate_sample_config(sample_config: Dict[str, Any]) -> None:
    update_config = sample_config["compute_target_update"]
    require_value(update_config.get("compute_target_id"), "compute_target_update.compute_target_id")

    if "compute_configuration_details" in update_config:
        raise ValueError(
            "This sample intentionally does not update compute_configuration_details. "
            "Compute Target shape, OCPU, memory, and boot volume updates are not included."
        )


def build_update_compute_target_details(
    sample_config: Dict[str, Any]
) -> UpdateComputeTargetDetails:
    update_config = sample_config["compute_target_update"]
    return UpdateComputeTargetDetails(
        display_name=update_config.get("display_name"),
        description=update_config.get("description"),
        metadata=update_config.get("metadata"),
        freeform_tags=update_config.get("freeform_tags"),
        defined_tags=update_config.get("defined_tags"),
    )


def print_payload(sample_config: Dict[str, Any]) -> None:
    update_details = build_update_compute_target_details(sample_config)
    print("UpdateComputeTargetDetails:")
    print(json.dumps(prune_empty_values(oci.util.to_dict(update_details)), indent=2))


def update_compute_target(sample_config: Dict[str, Any]) -> None:
    update_config = sample_config["compute_target_update"]
    client = create_data_science_client(sample_config)
    composite_client = data_science.DataScienceClientCompositeOperations(client)

    try:
        response = composite_client.update_compute_target_and_wait_for_state(
            compute_target_id=update_config["compute_target_id"],
            update_compute_target_details=build_update_compute_target_details(
                sample_config
            ),
            wait_for_states=["SUCCEEDED", "FAILED"],
        )
    except ServiceError:
        LOGGER.exception("Failed to update Compute Target.")
        raise

    if response.data.status != "SUCCEEDED":
        raise RuntimeError(
            "Compute Target update did not succeed. "
            f"Work request status: {response.data.status}"
        )

    LOGGER.info("Updated Compute Target: %s", update_config["compute_target_id"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update Compute Target metadata and tags."
    )
    parser.add_argument(
        "--config-json",
        default="config.json",
        help="Path to a config JSON file. Defaults to ./config.json.",
    )
    parser.add_argument(
        "--print-payload",
        action="store_true",
        help="Print the SDK request payload without calling OCI.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    sample_config = load_sample_config(args.config_json)
    validate_sample_config(sample_config)

    if args.print_payload:
        print_payload(sample_config)
        return

    update_compute_target(sample_config)


if __name__ == "__main__":
    main()
