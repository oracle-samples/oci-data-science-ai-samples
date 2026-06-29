#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Update an OCI Data Science model deployment on a Compute Target."""

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
    ManagedComputeClusterModelDeploymentResourceConfiguration,
    ManagedComputeClusterWorkloadAutoScalingPolicy,
    ManagedComputeClusterWorkloadFixedSizeScalingPolicy,
    ManagedComputeClusterWorkloadScalePolicy,
    ManagedComputeClusterWorkloadThresholdBasedPolicyDetails,
    ResourceLimitConfiguration,
    ResourceRequestConfiguration,
    TargetCustomExpressionQueryScalingConfiguration,
    TargetCustomMetricExpressionRule,
    TargetPredefinedExpressionThresholdScalingConfiguration,
    TargetPredefinedMetricExpressionRule,
    UpdateManagedComputeClusterModelDeployInfrastructureConfigDetails,
    UpdateModelDeploymentDetails,
    UpdateOcirModelDeploymentEnvironmentConfigurationDetails,
    UpdateSingleModelConfigurationDetails,
    UpdateSingleModelDeploymentFlexConfigurationDetails,
)
from oci.exceptions import ServiceError

LOGGER = logging.getLogger("update_model_deployment_on_compute_target")


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


def optional_value(value: Optional[str], field_name: str) -> Optional[str]:
    if not value:
        return None
    if is_placeholder(value):
        raise ValueError(
            f"Replace the placeholder value for '{field_name}' in the config JSON before running the update sample."
        )
    return value


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


def validate_resource_configuration(model_deployment_config: Dict[str, Any]) -> None:
    request = model_deployment_config.get("resource_request")
    limits = model_deployment_config.get("resource_limit")
    if not request or not limits:
        return

    if limits["ocpus"] < request["ocpus"]:
        raise ValueError(
            "model_deployment_update.resource_limit.ocpus must be greater than or equal to resource_request.ocpus."
        )
    if limits["memory_in_gbs"] < request["memory_in_gbs"]:
        raise ValueError(
            "model_deployment_update.resource_limit.memory_in_gbs must be greater than or equal to resource_request.memory_in_gbs."
        )


def validate_sample_config(sample_config: Dict[str, Any]) -> None:
    update_config = sample_config["model_deployment_update"]
    require_value(
        update_config.get("model_deployment_id"),
        "model_deployment_update.model_deployment_id",
    )

    if "compute_target_id" in update_config:
        raise ValueError(
            "This sample intentionally omits model_deployment_update.compute_target_id. "
            "Active model deployments on Compute Targets do not support computeTargetId updates."
        )

    validate_resource_configuration(update_config)
    validate_scaling_config(update_config, "model_deployment_update.scaling")


def validate_scaling_config(model_deployment_config: Dict[str, Any], field_name: str) -> None:
    scaling_config = model_deployment_config.get("scaling")
    if not scaling_config:
        return

    scaling_type = scaling_config.get("type", "").upper()
    if scaling_type == "FIXED_SIZE":
        if "autoscaling" in scaling_config:
            raise ValueError(
                f"'{field_name}.autoscaling' must not be set when type is FIXED_SIZE."
            )
        if scaling_config.get("instance_count") is None:
            raise ValueError(
                f"'{field_name}.instance_count' must be provided when type is FIXED_SIZE."
            )
        return

    if scaling_type != "AUTOSCALING":
        raise ValueError(f"'{field_name}.type' must be FIXED_SIZE or AUTOSCALING.")

    if "instance_count" in scaling_config:
        raise ValueError(
            f"'{field_name}.instance_count' must not be set when type is AUTOSCALING."
        )

    autoscaling_config = scaling_config.get("autoscaling")
    if not autoscaling_config:
        raise ValueError(
            f"'{field_name}.autoscaling' must be provided when type is AUTOSCALING."
        )

    for required_field in (
        "minimum_instance_count",
        "maximum_instance_count",
        "initial_instance_count",
        "rules",
        "scale_out_policy",
        "scale_in_policy",
    ):
        if autoscaling_config.get(required_field) in (None, []):
            raise ValueError(
                f"'{field_name}.autoscaling.{required_field}' must be provided when type is AUTOSCALING."
            )

    minimum_instance_count = autoscaling_config["minimum_instance_count"]
    maximum_instance_count = autoscaling_config["maximum_instance_count"]
    initial_instance_count = autoscaling_config["initial_instance_count"]
    if not minimum_instance_count <= initial_instance_count <= maximum_instance_count:
        raise ValueError(
            f"'{field_name}.autoscaling' must satisfy minimum_instance_count <= initial_instance_count <= maximum_instance_count."
        )

    for index, rule in enumerate(autoscaling_config["rules"]):
        rule_field_name = f"{field_name}.autoscaling.rules[{index}]"
        rule_type = rule.get("type", "").upper()
        if rule_type in ("TARGET_PREDEFINED_EXPRESSION", "PREDEFINED"):
            if rule.get("metric_type") is None or rule.get("threshold") is None:
                raise ValueError(
                    f"'{rule_field_name}' must include metric_type and threshold for predefined autoscaling rules."
                )
            continue
        if rule_type in ("TARGET_CUSTOM_EXPRESSION", "CUSTOM"):
            if rule.get("query") is None or rule.get("threshold") is None:
                raise ValueError(
                    f"'{rule_field_name}' must include query and threshold for custom autoscaling rules."
                )
            if is_placeholder(rule["query"]):
                raise ValueError(
                    f"Replace the placeholder value for '{rule_field_name}.query' before running the update sample."
                )
            if rule.get("metric_namespace") and is_placeholder(rule["metric_namespace"]):
                raise ValueError(
                    f"Replace the placeholder value for '{rule_field_name}.metric_namespace' before running the update sample."
                )
            continue
        raise ValueError(
            f"'{rule_field_name}.type' must be TARGET_PREDEFINED_EXPRESSION or TARGET_CUSTOM_EXPRESSION."
        )


def build_resource_request(
    model_deployment_config: Dict[str, Any]
) -> Optional[ResourceRequestConfiguration]:
    resource_request = model_deployment_config.get("resource_request")
    if not resource_request:
        return None

    return ResourceRequestConfiguration(
        ocpus=resource_request["ocpus"],
        memory_in_gbs=resource_request["memory_in_gbs"],
        gpus=resource_request.get("gpus"),
    )


def build_resource_limit(
    model_deployment_config: Dict[str, Any]
) -> Optional[ResourceLimitConfiguration]:
    resource_limit = model_deployment_config.get("resource_limit")
    if not resource_limit:
        return None

    return ResourceLimitConfiguration(
        ocpus=resource_limit["ocpus"],
        memory_in_gbs=resource_limit["memory_in_gbs"],
    )


def build_resource_configuration(model_deployment_config: Dict[str, Any]):
    resource_request = build_resource_request(model_deployment_config)
    resource_limit = build_resource_limit(model_deployment_config)
    if not resource_request and not resource_limit:
        return None

    return ManagedComputeClusterModelDeploymentResourceConfiguration(
        resource_request_configuration=resource_request,
        resource_limit_configuration=resource_limit,
    )


def build_workload_scaling_policy(
    model_deployment_config: Dict[str, Any],
):
    scaling_config = model_deployment_config.get("scaling")
    if not scaling_config:
        return None

    scaling_type = scaling_config.get("type", "FIXED_SIZE").upper()
    if scaling_type == "FIXED_SIZE":
        return ManagedComputeClusterWorkloadFixedSizeScalingPolicy(
            instance_count=scaling_config.get("instance_count", 1)
        )

    if scaling_type != "AUTOSCALING":
        raise ValueError(
            "model_deployment_update.scaling.type must be FIXED_SIZE or AUTOSCALING."
        )

    autoscaling_config = scaling_config["autoscaling"]
    return ManagedComputeClusterWorkloadAutoScalingPolicy(
        is_enabled=True,
        auto_scaling_policies=[
            ManagedComputeClusterWorkloadThresholdBasedPolicyDetails(
                minimum_instance_count=autoscaling_config["minimum_instance_count"],
                maximum_instance_count=autoscaling_config["maximum_instance_count"],
                initial_instance_count=autoscaling_config["initial_instance_count"],
                rules=build_autoscaling_rules(autoscaling_config),
                scale_out_policy=build_workload_scale_policy(
                    autoscaling_config["scale_out_policy"]
                ),
                scale_in_policy=build_workload_scale_policy(
                    autoscaling_config["scale_in_policy"]
                ),
            )
        ],
    )


def build_autoscaling_rules(
    autoscaling_config: Dict[str, Any],
):
    rules = []
    for rule in autoscaling_config["rules"]:
        rule_type = rule.get("type", "").upper()
        if rule_type in ("TARGET_PREDEFINED_EXPRESSION", "PREDEFINED"):
            rules.append(
                TargetPredefinedMetricExpressionRule(
                    metric_type=rule["metric_type"],
                    scale_configuration=TargetPredefinedExpressionThresholdScalingConfiguration(
                        threshold=rule["threshold"]
                    ),
                )
            )
            continue

        rules.append(
            TargetCustomMetricExpressionRule(
                scale_configuration=TargetCustomExpressionQueryScalingConfiguration(
                    query=rule["query"],
                    threshold=rule["threshold"],
                    metric_namespace=rule.get("metric_namespace"),
                )
            )
        )
    return rules


def build_workload_scale_policy(scale_policy_config: Dict[str, Any]):
    return ManagedComputeClusterWorkloadScalePolicy(
        pending_duration=scale_policy_config.get("pending_duration", "PT1M"),
        instance_count_adjustment=scale_policy_config.get(
            "instance_count_adjustment", 1
        ),
        cool_down_in_seconds=scale_policy_config.get("cool_down_in_seconds", 300),
    )


def build_infrastructure_configuration(model_deployment_config: Dict[str, Any]):
    resource_configuration = build_resource_configuration(model_deployment_config)
    scaling_policy = build_workload_scaling_policy(model_deployment_config)
    if not resource_configuration and not scaling_policy:
        return None

    return UpdateManagedComputeClusterModelDeployInfrastructureConfigDetails(
        model_deployment_resource_configuration=resource_configuration,
        scaling_policy=scaling_policy,
    )


def build_environment_configuration(model_deployment_config: Dict[str, Any]):
    environment_config = model_deployment_config.get("environment_configuration")
    if not environment_config:
        return None

    return UpdateOcirModelDeploymentEnvironmentConfigurationDetails(
        image=optional_value(
            environment_config.get("container_image"),
            "model_deployment_update.environment_configuration.container_image",
        ),
        image_digest=optional_value(
            environment_config.get("container_image_digest"),
            "model_deployment_update.environment_configuration.container_image_digest",
        ),
        server_port=environment_config.get("server_port"),
        health_check_port=environment_config.get("health_check_port"),
        environment_variables=environment_config.get("environment_variables"),
    )


def build_model_configuration(model_deployment_config: Dict[str, Any]):
    model_id = optional_value(
        model_deployment_config.get("model_id"),
        "model_deployment_update.model_id",
    )
    if not model_id:
        return None

    return UpdateSingleModelConfigurationDetails(model_id=model_id)


def build_update_model_deployment_details(
    sample_config: Dict[str, Any]
) -> UpdateModelDeploymentDetails:
    update_config = sample_config["model_deployment_update"]
    configuration_details = UpdateSingleModelDeploymentFlexConfigurationDetails(
        model_configuration_details=build_model_configuration(update_config),
        infrastructure_configuration_details=build_infrastructure_configuration(
            update_config
        ),
        environment_configuration_details=build_environment_configuration(
            update_config
        ),
    )

    update_details = UpdateModelDeploymentDetails(
        display_name=update_config.get("display_name"),
        description=update_config.get("description"),
        model_deployment_configuration_details=configuration_details,
        freeform_tags=update_config.get("freeform_tags"),
        defined_tags=update_config.get("defined_tags"),
    )

    if not prune_empty_values(oci.util.to_dict(update_details)):
        raise ValueError("No update fields were provided in model_deployment_update.")

    return update_details


def print_payload(sample_config: Dict[str, Any]) -> None:
    update_details = build_update_model_deployment_details(sample_config)
    print("UpdateModelDeploymentDetails:")
    print(json.dumps(prune_empty_values(oci.util.to_dict(update_details)), indent=2))


def update_model_deployment(sample_config: Dict[str, Any]) -> None:
    update_config = sample_config["model_deployment_update"]
    client = create_data_science_client(sample_config)
    composite_client = data_science.DataScienceClientCompositeOperations(client)

    try:
        response = composite_client.update_model_deployment_and_wait_for_state(
            model_deployment_id=update_config["model_deployment_id"],
            update_model_deployment_details=build_update_model_deployment_details(
                sample_config
            ),
            wait_for_states=["SUCCEEDED", "FAILED"],
        )
    except ServiceError:
        LOGGER.exception("Failed to update Model Deployment.")
        raise

    if response.data.status != "SUCCEEDED":
        raise RuntimeError(
            "Model Deployment update did not succeed. "
            f"Work request status: {response.data.status}"
        )

    LOGGER.info("Updated Model Deployment: %s", update_config["model_deployment_id"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update a model deployment on a Managed Compute Cluster Compute Target."
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

    update_model_deployment(sample_config)


if __name__ == "__main__":
    main()
