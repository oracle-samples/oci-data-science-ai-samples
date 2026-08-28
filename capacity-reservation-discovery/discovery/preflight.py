# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Validate public OCI client capability before running discovery."""

from __future__ import annotations

import importlib.metadata
import inspect
import json
import shlex
import subprocess
from collections.abc import Mapping

from .adapters import SDK_RESOURCE_METHODS
from .engine import ALL_RESOURCE_TYPES, DiscoveryError


class ClientPrerequisiteError(DiscoveryError):
    """An installed public OCI client lacks the required Data Science API surface."""


def installed_sdk_version() -> str | None:
    try:
        return importlib.metadata.version("oci")
    except importlib.metadata.PackageNotFoundError:
        return None


def _sdk_exposes_capacity_reservation_fields() -> bool:
    """Check generated model source rather than guessing from an SDK version alone."""

    try:
        import oci.data_science.models as models
    except ImportError:
        return False

    for _, model in inspect.getmembers(models, inspect.isclass):
        try:
            source = inspect.getsource(model)
        except (OSError, TypeError):
            continue
        if "capacity_reservation_id" in source or "capacity_reservation_ids" in source:
            return True
    return False


def _is_preview_version(version: str) -> bool:
    return "preview" in version.lower()


def validate_oci_sdk() -> str:
    """Require a public SDK that exposes the capacity-reservation model fields.

    The check deliberately tests generated-model capability instead of pinning a version. This
    lets the sample follow the latest public PyPI release once the Data Science API surface is
    generally available, while preventing a client that omits the fields from emitting a
    misleading empty report.
    """

    version = installed_sdk_version()
    if not version:
        raise ClientPrerequisiteError("OCI Python SDK is not installed. Install the latest public 'oci' package.")
    if _is_preview_version(version):
        raise ClientPrerequisiteError(
            "OCI Python SDK {} is a preview build. Install the latest public 'oci' package from PyPI.".format(
                version
            )
        )

    try:
        from oci.data_science import DataScienceClient
    except ImportError as error:
        raise ClientPrerequisiteError("The installed OCI SDK has no Data Science client.") from error

    required = [item for item in ALL_RESOURCE_TYPES if item != "compute_target"]
    missing_methods = [
        item
        for item in required
        if item not in SDK_RESOURCE_METHODS
        or not hasattr(DataScienceClient, SDK_RESOURCE_METHODS[item][0])
        or not hasattr(DataScienceClient, SDK_RESOURCE_METHODS[item][1])
    ]
    if missing_methods:
        raise ClientPrerequisiteError(
            "The installed OCI SDK is missing Data Science operations for: {}.".format(
                ", ".join(missing_methods)
            )
        )

    if not _sdk_exposes_capacity_reservation_fields():
        raise ClientPrerequisiteError(
            "OCI Python SDK {} does not expose the public Data Science capacityReservationId(s) fields "
            "required by this report. Upgrade to the latest public 'oci' package and rerun this check "
            "after that API surface is available.".format(version)
        )
    return version


def installed_cli_version(oci_cli: str) -> str | None:
    command = shlex.split(oci_cli)
    if not command:
        return None
    try:
        completed = subprocess.run(
            command + ["--version"], check=False, capture_output=True, text=True
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else None


def _has_capacity_reservation_field(value: object) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in {"capacityReservationId", "capacityReservationIds"}:
                return True
            if _has_capacity_reservation_field(item):
                return True
    elif isinstance(value, list):
        return any(_has_capacity_reservation_field(item) for item in value)
    return False


def _cli_exposes_capacity_reservation_fields(oci_cli: str) -> bool:
    """Check generated CLI input models without contacting OCI.

    These configuration templates use the same generated Data Science models as list/get
    responses. Checking them prevents the CLI adapter from silently dropping an unknown
    capacity-reservation property.
    """

    command = shlex.split(oci_cli)
    if not command:
        return False
    template_commands = (
        ("data-science", "notebook-session", "create", "--generate-param-json-input", "config-details"),
        (
            "data-science",
            "model-deployment",
            "create",
            "--generate-param-json-input",
            "model-deployment-configuration-details",
        ),
        (
            "data-science",
            "job",
            "create",
            "--generate-param-json-input",
            "infrastructure-configuration-details",
        ),
        (
            "data-science",
            "job-run",
            "create",
            "--generate-param-json-input",
            "job-infrastructure-configuration-override-details",
        ),
    )
    for template_command in template_commands:
        try:
            completed = subprocess.run(
                command + list(template_command), check=False, capture_output=True, text=True
            )
        except OSError:
            return False
        if completed.returncode != 0:
            continue
        try:
            template = json.loads(completed.stdout)
        except json.JSONDecodeError:
            continue
        if _has_capacity_reservation_field(template):
            return True
    return False


def validate_oci_cli(oci_cli: str) -> str:
    """Require a public CLI that exposes capacity-reservation configuration fields."""

    version = installed_cli_version(oci_cli)
    if not version:
        raise ClientPrerequisiteError("Could not run OCI CLI '{} --version'.".format(oci_cli))
    if _is_preview_version(version):
        raise ClientPrerequisiteError(
            "OCI CLI {} is a preview build. Install the latest public 'oci-cli' package from PyPI.".format(
                version
            )
        )
    if not _cli_exposes_capacity_reservation_fields(oci_cli):
        raise ClientPrerequisiteError(
            "OCI CLI {} does not expose the public Data Science capacityReservationId(s) fields required "
            "by this report. Upgrade to the latest public 'oci-cli' package and rerun this check after "
            "that API surface is available.".format(version)
        )
    return version
