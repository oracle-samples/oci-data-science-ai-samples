# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from __future__ import annotations

import sys
import types

import pytest

from discovery import preflight


def test_validate_oci_sdk_accepts_a_public_client_with_the_required_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeDataScienceClient:
        def list_notebook_sessions(self) -> None: ...
        def get_notebook_session(self) -> None: ...
        def list_model_deployments(self) -> None: ...
        def get_model_deployment(self) -> None: ...
        def list_jobs(self) -> None: ...
        def get_job(self) -> None: ...
        def list_job_runs(self) -> None: ...
        def get_job_run(self) -> None: ...

    fake_data_science = types.ModuleType("oci.data_science")
    fake_data_science.DataScienceClient = FakeDataScienceClient
    fake_oci = types.ModuleType("oci")
    fake_oci.__path__ = []  # type: ignore[attr-defined]
    fake_oci.data_science = fake_data_science
    monkeypatch.setitem(sys.modules, "oci", fake_oci)
    monkeypatch.setitem(sys.modules, "oci.data_science", fake_data_science)
    monkeypatch.setattr(preflight, "installed_sdk_version", lambda: "2.999.0")
    monkeypatch.setattr(preflight, "_sdk_exposes_capacity_reservation_fields", lambda: True)

    assert preflight.validate_oci_sdk() == "2.999.0"


def test_validate_oci_sdk_rejects_a_preview_build(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight, "installed_sdk_version", lambda: "2.999.0+preview.1")

    with pytest.raises(preflight.ClientPrerequisiteError, match="latest public 'oci' package"):
        preflight.validate_oci_sdk()


def test_validate_oci_cli_requires_capacity_reservation_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight, "installed_cli_version", lambda _: "3.999.0")
    monkeypatch.setattr(preflight, "_cli_exposes_capacity_reservation_fields", lambda _: False)

    with pytest.raises(preflight.ClientPrerequisiteError, match="capacityReservationId"):
        preflight.validate_oci_cli("oci")


def test_validate_oci_cli_accepts_a_public_client_with_the_required_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preflight, "installed_cli_version", lambda _: "3.999.0")
    monkeypatch.setattr(preflight, "_cli_exposes_capacity_reservation_fields", lambda _: True)

    assert preflight.validate_oci_cli("oci") == "3.999.0"


def test_cli_template_field_detection_finds_nested_capacity_reservation_ids() -> None:
    assert preflight._has_capacity_reservation_field(
        {"configuration": {"capacityReservationIds": ["reservation-a"]}}
    )
    assert not preflight._has_capacity_reservation_field({"configuration": {"shape": "VM.Standard.E5"}})
