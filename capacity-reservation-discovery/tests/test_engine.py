# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from discovery.engine import ALL_RESOURCE_TYPES, discover_capacity_reservation_associations


class FakeAdapter:
    source_name = "fixture"

    def __init__(self, *, supports_compute_target: bool = True) -> None:
        self.supports_compute_target = supports_compute_target
        self.capacity_reservations = {
            "cr-alpha": {
                "id": "cr-alpha",
                "displayName": "Alpha GPU",
                "lifecycleState": "ACTIVE",
                "compartmentId": "compartment-a",
                "availabilityDomain": "AD-1",
                "instanceReservationConfigs": [
                    {"instanceShape": "VM.GPU.A10.1", "reservedCount": 4, "usedCount": 1}
                ],
            },
            "cr-beta": {
                "id": "cr-beta",
                "displayName": "Beta GPU",
                "lifecycleState": "ACTIVE",
                "compartmentId": "compartment-a",
                "availabilityDomain": "AD-1",
                "instanceReservationConfigs": [
                    {"instanceShape": "VM.GPU.A10.1", "reservedCount": 2, "usedCount": 0}
                ],
            },
        }
        self.resources: dict[str, dict[str, Mapping[str, Any]]] = {
            "notebook_session": {
                "notebook-1": {
                    "id": "notebook-1",
                    "displayName": "Notebook one",
                    "lifecycleState": "ACTIVE",
                    "compartmentId": "compartment-a",
                    "notebookSessionConfigurationDetails": {
                        "shape": "VM.GPU.A10.1",
                        "capacityReservationId": "cr-alpha",
                    },
                }
            },
            "model_deployment": {
                "model-1": {
                    "id": "model-1",
                    "displayName": "Model one",
                    "lifecycleState": "ACTIVE",
                    "compartmentId": "compartment-a",
                    "modelDeploymentConfigurationDetails": {
                        "infrastructureConfigurationDetails": {
                            "instanceConfiguration": {
                                "instanceShape": "VM.GPU.A10.1",
                                "instanceCount": 2,
                                "capacityReservationIds": ["cr-alpha", "cr-not-visible"],
                            }
                        }
                    },
                }
            },
            "job": {
                "job-1": {
                    "id": "job-1",
                    "displayName": "Job one",
                    "lifecycleState": "ACTIVE",
                    "compartmentId": "compartment-a",
                    "jobInfrastructureConfigurationDetails": {
                        "shapeName": "VM.GPU.A10.1",
                        "capacityReservationId": "cr-beta",
                    },
                }
            },
            "job_run": {
                "run-1": {
                    "id": "run-1",
                    "displayName": "Run one",
                    "lifecycleState": "SUCCEEDED",
                    "compartmentId": "compartment-a",
                    "jobId": "job-1",
                }
            },
            "compute_target": {
                "target-1": {
                    "id": "target-1",
                    "displayName": "Target one",
                    "lifecycleState": "ACTIVE",
                    "compartmentId": "compartment-a",
                    "computeConfigurationDetails": {
                        "instanceConfiguration": {
                            "instanceShape": "VM.GPU.A10.1",
                            "instanceCount": 3,
                            "capacityReservationIds": ["cr-alpha", "cr-beta"],
                        }
                    },
                }
            },
        }

    def supports(self, resource_type: str) -> bool:
        return resource_type != "compute_target" or self.supports_compute_target

    def list_capacity_reservations(self, compartment_id: str) -> list[Mapping[str, Any]]:
        assert compartment_id == "compartment-a"
        return [
            {"id": "cr-alpha", "displayName": "Alpha GPU"},
            {"id": "cr-beta", "displayName": "Beta GPU"},
        ]

    def get_capacity_reservation(self, reservation_id: str) -> Mapping[str, Any]:
        return self.capacity_reservations[reservation_id]

    def list_resources(self, resource_type: str, compartment_id: str) -> list[Mapping[str, Any]]:
        assert compartment_id == "compartment-a"
        return [{"id": resource_id} for resource_id in self.resources[resource_type]]

    def get_resource(self, resource_type: str, resource_id: str) -> Mapping[str, Any]:
        return self.resources[resource_type][resource_id]


def _association_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in report["rows"] if row["row_type"] == "association"]


def test_fixed_full_scan_correlates_explicit_fields_without_using_aggregate_compute_usage() -> None:
    report = discover_capacity_reservation_associations(
        FakeAdapter(), "compartment-a", generated_at="2026-08-12T00:00:00+00:00"
    )

    rows = _association_rows(report)
    assert report["complete"] is True
    assert ALL_RESOURCE_TYPES == (
        "notebook_session",
        "model_deployment",
        "job",
        "job_run",
        "compute_target",
    )
    assert report["scope"]["resource_types"] == list(ALL_RESOURCE_TYPES)
    assert len(rows) == 6
    assert {(row["reservation_id"], row["resource_type"], row["resource_id"]) for row in rows} == {
        ("cr-alpha", "notebook_session", "notebook-1"),
        ("cr-alpha", "model_deployment", "model-1"),
        ("cr-alpha", "compute_target", "target-1"),
        ("cr-beta", "job", "job-1"),
        ("cr-beta", "job_run", "run-1"),
        ("cr-beta", "compute_target", "target-1"),
    }
    beta_run = next(row for row in rows if row["resource_id"] == "run-1")
    assert beta_run["association_field"].startswith("job.jobInfrastructureConfigurationDetails")
    assert report["reservations"][1]["reservation_shape_configs"][0]["used_count"] == 0
    assert report["unresolved_associations"][0]["capacity_reservation_id"] == "cr-not-visible"


def test_optional_unsupported_type_makes_no_association_rows_indeterminate() -> None:
    report = discover_capacity_reservation_associations(
        FakeAdapter(supports_compute_target=False),
        "compartment-a",
        generated_at="2026-08-12T00:00:00+00:00",
    )

    assert report["complete"] is False
    assert any(warning["code"] == "RESOURCE_TYPE_UNSUPPORTED" for warning in report["warnings"])


def test_full_scope_resolves_model_job_and_job_run_through_compute_target() -> None:
    adapter = FakeAdapter()
    adapter.resources["model_deployment"]["model-via-target"] = {
        "id": "model-via-target",
        "displayName": "Model through target",
        "lifecycleState": "ACTIVE",
        "compartmentId": "compartment-a",
        "modelDeploymentConfigurationDetails": {
            "infrastructureConfigurationDetails": {
                "computeTargetId": "target-1",
                "modelDeploymentResourceConfiguration": {"instanceCount": 5},
            }
        },
    }
    adapter.resources["job"]["job-via-target"] = {
        "id": "job-via-target",
        "displayName": "Job through target",
        "lifecycleState": "ACTIVE",
        "compartmentId": "compartment-a",
        "jobInfrastructureConfigurationDetails": {
            "jobInfrastructureType": "MANAGED_COMPUTE_CLUSTER",
            "computeTargetId": "target-1",
            "resourceConfiguration": {"instanceCount": 4},
        },
    }
    adapter.resources["job_run"]["run-via-target"] = {
        "id": "run-via-target",
        "displayName": "Run through target",
        "lifecycleState": "SUCCEEDED",
        "compartmentId": "compartment-a",
        "timeAccepted": "2026-08-12T00:00:00+00:00",
        "jobInfrastructureConfigurationDetails": {
            "jobInfrastructureType": "MANAGED_COMPUTE_CLUSTER",
            "computeTargetId": "target-1",
            "resourceConfiguration": {"instanceCount": 3},
        },
    }

    report = discover_capacity_reservation_associations(
        adapter, "compartment-a", generated_at="2026-08-12T00:00:00+00:00"
    )

    rows = [
        row
        for row in _association_rows(report)
        if row["resource_id"] in {"model-via-target", "job-via-target", "run-via-target"}
    ]
    assert {(row["resource_id"], row["reservation_id"]) for row in rows} == {
        (resource_id, reservation_id)
        for resource_id in ("model-via-target", "job-via-target", "run-via-target")
        for reservation_id in ("cr-alpha", "cr-beta")
    }
    assert {row["association_source"] for row in rows} == {"compute_target"}
    assert {row["compute_target_name"] for row in rows} == {"Target one"}
    assert all("computeTargetId -> computeTarget." in row["association_field"] for row in rows)
    run_row = next(row for row in rows if row["resource_id"] == "run-via-target")
    assert run_row["resource_created"] == "2026-08-12T00:00:00+00:00"


def test_job_run_uses_effective_configuration_after_empty_override() -> None:
    adapter = FakeAdapter()
    adapter.resources["job_run"]["run-effective"] = {
        "id": "run-effective",
        "displayName": "Run effective configuration",
        "lifecycleState": "SUCCEEDED",
        "compartmentId": "compartment-a",
        "jobId": "job-1",
        "jobInfrastructureConfigurationOverrideDetails": {},
        "jobInfrastructureConfigurationDetails": {
            "jobInfrastructureType": "STANDALONE",
            "shapeName": "VM.GPU.A10.1",
            "capacityReservationId": "cr-alpha",
        },
    }

    report = discover_capacity_reservation_associations(
        adapter, "compartment-a", generated_at="2026-08-12T00:00:00+00:00"
    )

    row = next(row for row in _association_rows(report) if row["resource_id"] == "run-effective")
    assert row["reservation_id"] == "cr-alpha"
    assert row["configuration_source"] == "job_run_effective_configuration"
    assert row["association_source"] == "direct"


def test_multi_node_job_reservation_field_is_not_reported_as_supported_byor() -> None:
    adapter = FakeAdapter()
    adapter.resources["job"]["job-multi-node"] = {
        "id": "job-multi-node",
        "displayName": "Multi-node job",
        "lifecycleState": "ACTIVE",
        "compartmentId": "compartment-a",
        "jobInfrastructureConfigurationDetails": {
            "jobInfrastructureType": "MULTI_NODE",
            "capacityReservationIds": ["cr-alpha"],
        },
    }

    report = discover_capacity_reservation_associations(
        adapter, "compartment-a", generated_at="2026-08-12T00:00:00+00:00"
    )

    assert not any(row["resource_id"] == "job-multi-node" for row in _association_rows(report))
    assert report["complete"] is False
    assert any(
        warning["code"] == "UNSUPPORTED_MULTI_NODE_JOB_BYOR_CONFIGURATION"
        for warning in report["warnings"]
    )


def test_compute_target_outside_scope_is_retained_as_unresolved() -> None:
    adapter = FakeAdapter()
    adapter.resources["compute_target"]["target-1"]["compartmentId"] = "other-compartment"
    adapter.resources["model_deployment"]["model-via-target"] = {
        "id": "model-via-target",
        "displayName": "Model through target",
        "lifecycleState": "ACTIVE",
        "compartmentId": "compartment-a",
        "modelDeploymentConfigurationDetails": {
            "infrastructureConfigurationDetails": {"computeTargetId": "target-1"}
        },
    }

    report = discover_capacity_reservation_associations(
        adapter, "compartment-a", generated_at="2026-08-12T00:00:00+00:00"
    )

    assert report["complete"] is False
    unresolved = [
        item for item in report["unresolved_associations"] if item["resource_id"] == "model-via-target"
    ]
    assert {item["capacity_reservation_id"] for item in unresolved} == {"cr-alpha", "cr-beta"}
    assert {item["association_status"] for item in unresolved} == {
        "compute_target_outside_selected_compartment"
    }
