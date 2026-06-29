#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Create an OCI Data Science Managed Compute Cluster Compute Target."""

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional

import oci
import oci.data_science as data_science
from oci.auth import signers
from oci.data_science.models import (
    CreateComputeTargetDetails,
    ManagedComputeClusterAutoScalingPolicy,
    ManagedComputeClusterComputeConfigurationDetails,
    ManagedComputeClusterCustomExpressionQueryScalingConfiguration,
    ManagedComputeClusterCustomMetricExpressionRule,
    ManagedComputeClusterFixedSizeScalingPolicy,
    ManagedComputeClusterInstanceConfigurationDetails,
    ManagedComputeClusterInstanceShapeDetails,
    ManagedComputeClusterThresholdBasedAutoScalingPolicyDetails,
)
from oci.exceptions import ServiceError

LOGGER = logging.getLogger("create_compute_target")


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
    return isinstance(value, str) and re.search(r"<[^<>]+>", value) is not None


def require_value(value: Optional[str], field_name: str) -> None:
    if not value or is_placeholder(value):
        raise ValueError(
            f"Replace the placeholder value for '{field_name}' in the config JSON before running the sample."
        )


def require_metric_query(value: Optional[str], field_name: str) -> None:
    if not value:
        raise ValueError(f"'{field_name}' must be provided when autoscaling is enabled.")
    if is_placeholder(value):
        raise ValueError(
            f"Replace the placeholder value for '{field_name}' in the config JSON before running the sample."
        )


def validate_sample_config(sample_config: Dict[str, Any]) -> None:
    require_value(sample_config.get("compartment_id"), "compartment_id")

    compute_target_config = sample_config["compute_target"]
    require_value(compute_target_config.get("display_name"), "compute_target.display_name")

    instance_config = compute_target_config["instance_configuration"]
    require_value(instance_config.get("instance_shape"), "compute_target.instance_configuration.instance_shape")

    validate_scaling_config(compute_target_config)


def validate_scaling_config(compute_target_config: Dict[str, Any]) -> None:
    scaling_config = compute_target_config.get("scaling")
    if not scaling_config:
        raise ValueError("'compute_target.scaling' must be provided.")

    scaling_type = scaling_config.get("type", "").upper()
    if scaling_type == "FIXED_SIZE":
        if scaling_config.get("instance_count") is None:
            raise ValueError(
                "'compute_target.scaling.instance_count' must be provided when type is FIXED_SIZE."
            )
        return

    if scaling_type != "AUTOSCALING":
        raise ValueError("'compute_target.scaling.type' must be FIXED_SIZE or AUTOSCALING.")

    for required_field in (
        "minimum_instance_count",
        "maximum_instance_count",
        "initial_instance_count",
        "rules",
    ):
        if scaling_config.get(required_field) in (None, []):
            raise ValueError(
                f"'compute_target.scaling.{required_field}' must be provided when type is AUTOSCALING."
            )

    minimum_instance_count = scaling_config["minimum_instance_count"]
    maximum_instance_count = scaling_config["maximum_instance_count"]
    initial_instance_count = scaling_config["initial_instance_count"]
    if not minimum_instance_count <= initial_instance_count <= maximum_instance_count:
        raise ValueError(
            "'compute_target.scaling' must satisfy minimum_instance_count <= initial_instance_count <= maximum_instance_count."
        )

    for index, rule in enumerate(scaling_config["rules"]):
        rule_field_name = f"compute_target.scaling.rules[{index}]"
        if rule.get("type", "").upper() != "CUSTOM_EXPRESSION":
            raise ValueError(
                f"'{rule_field_name}.type' must be CUSTOM_EXPRESSION for this sample."
            )

        scale_out_config = rule.get("scale_out_configuration")
        scale_in_config = rule.get("scale_in_configuration")
        if not scale_out_config or not scale_in_config:
            raise ValueError(
                f"'{rule_field_name}' must include scale_out_configuration and scale_in_configuration."
            )

        require_metric_query(
            scale_out_config.get("query"),
            f"{rule_field_name}.scale_out_configuration.query",
        )
        require_metric_query(
            scale_in_config.get("query"),
            f"{rule_field_name}.scale_in_configuration.query",
        )


def build_instance_configuration(
    compute_target_config: Dict[str, Any]
) -> ManagedComputeClusterInstanceConfigurationDetails:
    instance_config = compute_target_config["instance_configuration"]
    shape_details = None
    if instance_config.get("ocpus") is not None or instance_config.get("memory_in_gbs") is not None:
        shape_details = ManagedComputeClusterInstanceShapeDetails(
            ocpus=instance_config.get("ocpus"),
            memory_in_gbs=instance_config.get("memory_in_gbs"),
        )

    return ManagedComputeClusterInstanceConfigurationDetails(
        instance_shape=instance_config["instance_shape"],
        boot_volume_size_in_gbs=instance_config.get("boot_volume_size_in_gbs"),
        instance_shape_details=shape_details,
    )


def build_fixed_size_policy(instance_count: int):
    return ManagedComputeClusterFixedSizeScalingPolicy(
        instance_count=instance_count
    )

def build_autoscaling_policy(
    compute_target_config: Dict[str, Any],
):
    scaling_config = compute_target_config["scaling"]
    rules = []
    for rule in scaling_config["rules"]:
        scale_out_config = rule["scale_out_configuration"]
        scale_in_config = rule["scale_in_configuration"]
        rules.append(
            ManagedComputeClusterCustomMetricExpressionRule(
                scale_out_configuration=ManagedComputeClusterCustomExpressionQueryScalingConfiguration(
                    query=scale_out_config["query"],
                    pending_duration=scale_out_config.get("pending_duration", "PT5M"),
                    instance_count_adjustment=scale_out_config.get(
                        "instance_count_adjustment", 1
                    ),
                ),
                scale_in_configuration=ManagedComputeClusterCustomExpressionQueryScalingConfiguration(
                    query=scale_in_config["query"],
                    pending_duration=scale_in_config.get("pending_duration", "PT10M"),
                    instance_count_adjustment=scale_in_config.get(
                        "instance_count_adjustment", 1
                    ),
                ),
            )
        )

    return ManagedComputeClusterAutoScalingPolicy(
        is_enabled=True,
        cool_down_in_seconds=scaling_config.get("cool_down_in_seconds", 300),
        auto_scaling_policies=[
            ManagedComputeClusterThresholdBasedAutoScalingPolicyDetails(
                minimum_instance_count=scaling_config["minimum_instance_count"],
                maximum_instance_count=scaling_config["maximum_instance_count"],
                initial_instance_count=scaling_config["initial_instance_count"],
                rules=rules,
            )
        ],
    )


def build_requested_scaling_policy(
    compute_target_config: Dict[str, Any],
):
    scaling_config = compute_target_config["scaling"]
    scaling_type = scaling_config.get("type", "FIXED_SIZE").upper()
    if scaling_type == "FIXED_SIZE":
        return build_fixed_size_policy(scaling_config.get("instance_count", 1))
    return build_autoscaling_policy(compute_target_config)


def build_create_compute_target_details(
    sample_config: Dict[str, Any],
) -> CreateComputeTargetDetails:
    compute_target_config = sample_config["compute_target"]
    return CreateComputeTargetDetails(
        compartment_id=sample_config["compartment_id"],
        display_name=compute_target_config.get("display_name"),
        description=compute_target_config.get("description"),
        compute_configuration_details=ManagedComputeClusterComputeConfigurationDetails(
            instance_configuration=build_instance_configuration(compute_target_config),
            scaling_policy=build_requested_scaling_policy(compute_target_config),
        ),
        freeform_tags=sample_config.get("freeform_tags", {}),
        defined_tags=sample_config.get("defined_tags", {}),
    )


def get_work_request_resource_identifier(work_request) -> Optional[str]:
    for resource in getattr(work_request, "resources", []) or []:
        identifier = getattr(resource, "identifier", None)
        if identifier:
            return identifier
    return None


def print_payload(sample_config: Dict[str, Any]) -> None:
    create_details = build_create_compute_target_details(sample_config)
    print("CreateComputeTargetDetails:")
    print(json.dumps(oci.util.to_dict(create_details), indent=2))


def create_compute_target(sample_config: Dict[str, Any]) -> str:
    client = create_data_science_client(sample_config)
    composite_client = data_science.DataScienceClientCompositeOperations(client)

    try:
        response = composite_client.create_compute_target_and_wait_for_state(
            create_compute_target_details=build_create_compute_target_details(sample_config),
            wait_for_states=["SUCCEEDED", "FAILED"],
        )
    except ServiceError:
        LOGGER.exception("Failed to create Compute Target.")
        raise

    if response.data.status != "SUCCEEDED":
        raise RuntimeError(
            "Compute Target creation did not succeed. "
            f"Work request status: {response.data.status}"
        )

    compute_target_id = get_work_request_resource_identifier(response.data)
    if not compute_target_id:
        raise RuntimeError("Compute Target was created, but no resource OCID was returned.")

    LOGGER.info("Created Compute Target: %s", compute_target_id)
    return compute_target_id


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a Managed Compute Cluster Compute Target."
    )
    parser.add_argument(
        "--config-json",
        default="config.json",
        help="Path to a config JSON file. Defaults to ./config.json.",
    )
    parser.add_argument(
        "--print-payload",
        action="store_true",
        help="Print SDK request payloads without calling OCI.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    sample_config = load_sample_config(args.config_json)
    validate_sample_config(sample_config)

    if args.print_payload:
        print_payload(sample_config)
        return

    compute_target_id = create_compute_target(sample_config)
    print(compute_target_id)


if __name__ == "__main__":
    main()
