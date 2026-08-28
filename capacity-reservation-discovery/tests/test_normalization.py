# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from discovery.normalization import (
    find_capacity_reservation_ids,
    find_first_by_keys,
    format_path,
    get_path,
    get_value,
)


def test_field_helpers_accept_camel_and_snake_case() -> None:
    payload = {
        "modelDeploymentConfigurationDetails": {
            "instance_configuration": {"capacity_reservation_ids": ["cr-one", "cr-two"]}
        }
    }

    assert get_value(payload, ["model_deployment_configuration_details"]) == payload[
        "modelDeploymentConfigurationDetails"
    ]
    assert get_path(payload, ["model_deployment_configuration_details", "instanceConfiguration"]) == {
        "capacity_reservation_ids": ["cr-one", "cr-two"]
    }


def test_field_helper_honors_requested_preference_not_payload_order() -> None:
    payload = {"id": "ocid1.example", "displayName": "Human readable name"}

    assert get_value(payload, ["displayName", "id"]) == "Human readable name"


def test_capacity_reservation_extraction_keeps_every_configured_id_and_path() -> None:
    payload = {
        "one": {"capacityReservationId": "cr-one"},
        "two": {"capacity_reservation_ids": ["cr-two", "", "cr-three"]},
    }

    found = find_capacity_reservation_ids(payload)

    assert [(item.value, format_path(item.path)) for item in found] == [
        ("cr-one", "one.capacityReservationId"),
        ("cr-two", "two.capacity_reservation_ids[0]"),
        ("cr-three", "two.capacity_reservation_ids[2]"),
    ]


def test_shape_and_count_extraction_is_recursive_and_ignores_boolean_counts() -> None:
    payload = {
        "nested": {
            "instanceShapeName": "VM.GPU.A10.1",
            "instanceCount": True,
            "replica_count": 2,
        }
    }

    shape = find_first_by_keys(payload, ["shapeName", "instanceShapeName"], str)
    count = find_first_by_keys(payload, ["instanceCount", "replicaCount"], int)

    assert shape is not None and shape.value == "VM.GPU.A10.1"
    assert count is not None and count.value == 2
