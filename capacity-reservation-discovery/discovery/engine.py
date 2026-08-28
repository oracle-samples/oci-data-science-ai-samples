# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Reservation-first correlation engine shared by the SDK and OCI CLI entry points.

This module intentionally correlates explicit Data Science configuration fields with
Compute Capacity Reservation OCIDs.  It never derives an association from Compute
``usedInstanceCount`` or from Compute's launched-instance list: both are aggregate
signals and cannot attribute usage to a Data Science resource.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Iterable, Protocol

from .normalization import (
    find_capacity_reservation_ids,
    find_first_by_keys,
    format_path,
    get_value,
    normalize_key,
    to_plain,
)


class DiscoveryError(RuntimeError):
    """An OCI request or report construction error that makes discovery unreliable."""


class UnsupportedResourceType(DiscoveryError):
    """The installed OCI client does not expose one optional resource type."""


class DiscoveryAdapter(Protocol):
    """Read-only operations required by the correlation engine."""

    source_name: str

    def supports(self, resource_type: str) -> bool:
        ...

    def list_capacity_reservations(self, compartment_id: str) -> list[Mapping[str, Any]]:
        ...

    def get_capacity_reservation(self, reservation_id: str) -> Mapping[str, Any]:
        ...

    def list_resources(self, resource_type: str, compartment_id: str) -> list[Mapping[str, Any]]:
        ...

    def get_resource(self, resource_type: str, resource_id: str) -> Mapping[str, Any]:
        ...


RESOURCE_TYPE_DISPLAY_NAMES = {
    "notebook_session": "Notebook session",
    "model_deployment": "Model deployment",
    "job": "Job",
    "job_run": "Job run",
    "compute_target": "Compute target",
}

# This registry is deliberately fixed. Discovery always scans every Data Science
# resource type that currently persists capacity-reservation configuration; callers
# cannot narrow the scan to a Console, BYOR, or ad-hoc subset.
ALL_RESOURCE_TYPES = (
    "notebook_session",
    "model_deployment",
    "job",
    "job_run",
    "compute_target",
)

SHAPE_KEYS = ("instanceShapeName", "instanceShape", "shapeName", "shape")
COUNT_KEYS = ("instanceCount", "replicaCount", "reservedCount")
COMPUTE_TARGET_ID_KEYS = ("computeTargetId",)
JOB_INFRASTRUCTURE_TYPE_KEYS = ("jobInfrastructureType", "infrastructureType")


def _field(value: Any, *keys: str, default: Any = None) -> Any:
    return get_value(value, keys, default)


def _string_field(value: Any, *keys: str, default: str | None = None) -> str | None:
    candidate = _field(value, *keys, default=default)
    return candidate if isinstance(candidate, str) and candidate else default


def _number_field(value: Any, *keys: str) -> int | None:
    candidate = _field(value, *keys)
    return candidate if isinstance(candidate, int) and not isinstance(candidate, bool) else None


def _config(value: Mapping[str, Any], resource_type: str) -> tuple[Any, str]:
    """Return the smallest configuration subtree with capacity-reservation fields."""

    candidate_paths: dict[str, tuple[str, ...]] = {
        "notebook_session": (
            "notebookSessionConfigurationDetails",
            "notebookSessionConfigDetails",
        ),
        "model_deployment": ("modelDeploymentConfigurationDetails",),
        "job": ("jobInfrastructureConfigurationDetails",),
        "job_run": (
            "jobInfrastructureConfigurationOverrideDetails",
            "jobInfrastructureConfigurationDetails",
        ),
        "compute_target": (
            "computeConfigurationDetails",
            "instanceConfiguration",
        ),
    }
    for key in candidate_paths[resource_type]:
        candidate = _field(value, key)
        if isinstance(candidate, Mapping):
            return candidate, key
    # Generated API models can move a field between configuration layers.
    # Fall back to the full payload to report an explicit field rather than silently
    # return no association.
    return value, ""


def _extract_shape(config: Any) -> str | None:
    found = find_first_by_keys(config, SHAPE_KEYS, str)
    return found.value if found else None


def _extract_count(config: Any) -> int | None:
    found = find_first_by_keys(config, COUNT_KEYS, int)
    return found.value if found else None


def _resource_info(resource: Mapping[str, Any], resource_type: str) -> dict[str, Any]:
    return {
        "resource_id": _string_field(resource, "id"),
        "resource_name": _string_field(resource, "displayName", "name", "id"),
        "resource_type": resource_type,
        "resource_type_display": RESOURCE_TYPE_DISPLAY_NAMES[resource_type],
        "resource_state": _string_field(resource, "lifecycleState"),
        "resource_compartment_id": _string_field(resource, "compartmentId"),
        "resource_created": _field(resource, "timeCreated", "timeAccepted"),
    }


def _resource_associations(
    resource: Mapping[str, Any],
    resource_type: str,
    config: Any | None = None,
    config_prefix: str | None = None,
    *,
    found_capacity_reservation_ids: Iterable[Any] | None = None,
    display_config: Any | None = None,
    association_source: str = "direct",
    association_metadata: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build report associations for reservation IDs found in one configuration.

    ``config`` identifies where the reservation OCID was configured.  An indirect
    Compute Target association can use a different ``display_config`` so the row
    retains the workload's own shape/count rather than incorrectly showing the
    target's cluster capacity as the workload's requested size.
    """

    config_value, inferred_prefix = _config(resource, resource_type) if config is None else (config, config_prefix or "")
    info = _resource_info(resource, resource_type)
    shape_count_config = config_value if display_config is None else display_config
    shape = _extract_shape(shape_count_config)
    count = _extract_count(shape_count_config)
    associations: list[dict[str, Any]] = []
    found_values = (
        find_capacity_reservation_ids(config_value)
        if found_capacity_reservation_ids is None
        else found_capacity_reservation_ids
    )
    for found in found_values:
        field = format_path(found.path)
        if inferred_prefix:
            field = "{}.{}".format(inferred_prefix, field) if field else inferred_prefix
        associations.append(
            {
                **info,
                "associated_resource_shape": shape,
                "associated_resource_count": count,
                "capacity_reservation_id": found.value,
                "association_field": field,
                "association_source": association_source,
                **(dict(association_metadata) if association_metadata else {}),
            }
        )
    return associations


def _capacity_reservation_scalar_ids(config: Any) -> list[Any]:
    """Return scalar ``capacityReservationId`` values, excluding plural fields.

    The documented direct BYOR path for a single-node Job/Job Run is the scalar
    field.  A plural field belongs to the unsupported multi-node path and must not
    be reported as a supported direct association.
    """

    scalar_key = normalize_key("capacityReservationId")
    return [
        found
        for found in find_capacity_reservation_ids(config)
        if found.path
        and isinstance(found.path[-1], str)
        and normalize_key(found.path[-1]) == scalar_key
    ]


def _is_multi_node_job_configuration(config: Any) -> bool:
    infrastructure_type = find_first_by_keys(config, JOB_INFRASTRUCTURE_TYPE_KEYS, str)
    return bool(infrastructure_type and infrastructure_type.value.upper() == "MULTI_NODE")


def _compute_target_reference(config: Any) -> Any | None:
    found = find_first_by_keys(config, COMPUTE_TARGET_ID_KEYS, str)
    if found is None or not found.value.strip():
        return None
    return found


def _prefixed_path(prefix: str | None, path: Any) -> str:
    formatted = format_path(path)
    if prefix:
        return "{}.{}".format(prefix, formatted) if formatted else prefix
    return formatted


def _reservation_info(reservation: Mapping[str, Any]) -> dict[str, Any]:
    configs = _field(reservation, "instanceReservationConfigs", default=[])
    configs = configs if isinstance(configs, list) else []
    shape_configs: list[dict[str, Any]] = []
    shape_summaries: list[str] = []
    for config in configs:
        if not isinstance(config, Mapping):
            continue
        shape = _extract_shape(config) or "-"
        reserved_count = _number_field(config, "reservedCount")
        used_count = _number_field(config, "usedCount")
        available_count = (
            reserved_count - used_count
            if reserved_count is not None and used_count is not None
            else None
        )
        shape_configs.append(
            {
                "shape": shape,
                "reserved_count": reserved_count,
                "used_count": used_count,
                "available_count": available_count,
                "fault_domain": _string_field(config, "faultDomain"),
            }
        )
        if reserved_count is None:
            shape_summaries.append(shape)
        elif used_count is None:
            shape_summaries.append("{}: {}".format(shape, reserved_count))
        else:
            shape_summaries.append("{}: {}/{}".format(shape, used_count, reserved_count))

    reservation_id = _string_field(reservation, "id")
    if not reservation_id:
        raise DiscoveryError("Compute returned a capacity reservation without an OCID.")
    return {
        "reservation_id": reservation_id,
        "reservation_name": _string_field(reservation, "displayName", "id"),
        "reservation_state": _string_field(reservation, "lifecycleState"),
        "reservation_compartment_id": _string_field(reservation, "compartmentId"),
        "availability_domain": _string_field(reservation, "availabilityDomain"),
        "is_default_reservation": _field(reservation, "isDefaultReservation"),
        "reservation_created": _field(reservation, "timeCreated"),
        "reservation_shape_configs": shape_configs,
        "reservation_shape_summary": ", ".join(shape_summaries) if shape_summaries else "-",
    }


def _warning(
    warnings: list[dict[str, Any]],
    code: str,
    message: str,
    **context: Any,
) -> None:
    warnings.append({"code": code, "message": message, **context})


def _get_detail(
    adapter: DiscoveryAdapter,
    resource_type: str,
    resource: Mapping[str, Any],
    warnings: list[dict[str, Any]],
    detail_cache: dict[str, dict[str, Mapping[str, Any]]] | None = None,
) -> Mapping[str, Any] | None:
    resource_id = _string_field(resource, "id")
    if not resource_id:
        _warning(
            warnings,
            "RESOURCE_WITHOUT_OCID",
            "A listed Data Science resource had no OCID and could not be correlated.",
            resource_type=resource_type,
        )
        return None
    if detail_cache is not None:
        cached = detail_cache.get(resource_type, {}).get(resource_id)
        if cached is not None:
            return cached
    try:
        detail = to_plain(adapter.get_resource(resource_type, resource_id))
        if not isinstance(detail, Mapping):
            raise DiscoveryError("OCI returned a non-object Data Science resource detail.")
        if detail_cache is not None:
            detail_cache.setdefault(resource_type, {})[resource_id] = detail
        return detail
    except UnsupportedResourceType:
        raise
    except Exception as error:  # OCI client exceptions are deliberately normalized for the report.
        _warning(
            warnings,
            "RESOURCE_DETAIL_UNAVAILABLE",
            "Could not read a listed Data Science resource; its association is indeterminate.",
            resource_type=resource_type,
            resource_id=resource_id,
            error=str(error),
        )
        return None


def _list_and_get(
    adapter: DiscoveryAdapter,
    resource_type: str,
    compartment_id: str,
    warnings: list[dict[str, Any]],
    detail_cache: dict[str, dict[str, Mapping[str, Any]]] | None = None,
) -> list[Mapping[str, Any]]:
    try:
        summaries = adapter.list_resources(resource_type, compartment_id)
    except UnsupportedResourceType:
        raise
    except Exception as error:
        _warning(
            warnings,
            "RESOURCE_LIST_UNAVAILABLE",
            "Could not list a requested Data Science resource type; results are incomplete.",
            resource_type=resource_type,
            error=str(error),
        )
        return []

    details: list[Mapping[str, Any]] = []
    for summary in summaries:
        detail = _get_detail(adapter, resource_type, to_plain(summary), warnings, detail_cache)
        if detail is not None:
            details.append(detail)
    return details


def _compute_target_associations(
    adapter: DiscoveryAdapter,
    resource: Mapping[str, Any],
    resource_type: str,
    resource_config: Any,
    resource_config_prefix: str,
    compute_target_reference: Any,
    compartment_id: str,
    warnings: list[dict[str, Any]],
    detail_cache: dict[str, dict[str, Mapping[str, Any]]],
    *,
    configuration_source: str,
) -> tuple[list[dict[str, Any]], bool]:
    """Resolve an indirect workload -> Compute Target -> reservation association.

    Managed Compute Cluster Jobs, Job Runs, and Model Deployments name a Compute
    Target, while the reservation OCID is configured on that target.  The emitted
    workload row is explicitly marked indirect so it cannot be mistaken for a
    direct ``capacityReservationId`` on the workload itself.
    """

    target_id = compute_target_reference.value.strip()
    resource_id = _string_field(resource, "id")
    if not adapter.supports("compute_target"):
        _warning(
            warnings,
            "COMPUTE_TARGET_LOOKUP_UNSUPPORTED",
            "Could not resolve a Compute Target-backed Data Science workload because this OCI client lacks Compute Target reads.",
            resource_type=resource_type,
            resource_id=resource_id,
            compute_target_id=target_id,
        )
        return [], True

    target = detail_cache.get("compute_target", {}).get(target_id)
    if target is None:
        try:
            target_detail = to_plain(adapter.get_resource("compute_target", target_id))
            if not isinstance(target_detail, Mapping):
                raise DiscoveryError("OCI returned a non-object Compute Target detail.")
            target = target_detail
            detail_cache.setdefault("compute_target", {})[target_id] = target
        except Exception as error:
            _warning(
                warnings,
                "COMPUTE_TARGET_UNAVAILABLE",
                "Could not resolve a Compute Target referenced by a Data Science workload; its reservation association is indeterminate.",
                resource_type=resource_type,
                resource_id=resource_id,
                compute_target_id=target_id,
                error=str(error),
            )
            return [], True

    target_config, target_prefix = _config(target, "compute_target")
    target_compartment_id = _string_field(target, "compartmentId")
    target_associations = _resource_associations(
        resource,
        resource_type,
        config=target_config,
        config_prefix="computeTarget.{}".format(target_prefix) if target_prefix else "computeTarget",
        display_config=resource_config,
        association_source="compute_target",
        association_metadata={
            "configuration_source": configuration_source,
            "compute_target_id": target_id,
            "compute_target_name": _string_field(target, "displayName", "name", "id"),
            "compute_target_compartment_id": target_compartment_id,
        },
    )
    target_reference_path = _prefixed_path(resource_config_prefix, compute_target_reference.path)
    for association in target_associations:
        association["association_field"] = "{} -> {}".format(
            target_reference_path, association["association_field"]
        )

    if target_compartment_id and target_compartment_id != compartment_id:
        _warning(
            warnings,
            "COMPUTE_TARGET_OUTSIDE_SELECTED_COMPARTMENT",
            "A Data Science workload references a Compute Target outside the selected compartment; its reservation association is retained as unresolved rather than joined across scope.",
            resource_type=resource_type,
            resource_id=resource_id,
            compute_target_id=target_id,
            compute_target_compartment_id=target_compartment_id,
        )
        for association in target_associations:
            association["association_visibility"] = "compute_target_outside_selected_compartment"
        return target_associations, True

    return target_associations, False


def _configuration_associations(
    adapter: DiscoveryAdapter,
    resource: Mapping[str, Any],
    resource_type: str,
    config: Any,
    config_prefix: str,
    compartment_id: str,
    warnings: list[dict[str, Any]],
    detail_cache: dict[str, dict[str, Mapping[str, Any]]],
    *,
    configuration_source: str,
    single_node_job_only: bool = False,
) -> tuple[list[dict[str, Any]], bool, bool]:
    """Discover direct and Compute Target-backed reservations for one config.

    Returns ``(associations, has_effective_configuration, incomplete)``.  The
    middle value is separate from association count because an inaccessible or
    out-of-scope Compute Target is still the effective configuration and must not
    fall through to an older parent Job configuration.
    """

    configured_ids = find_capacity_reservation_ids(config)
    direct_ids = configured_ids
    incomplete = False

    if single_node_job_only and configured_ids:
        if _is_multi_node_job_configuration(config):
            _warning(
                warnings,
                "UNSUPPORTED_MULTI_NODE_JOB_BYOR_CONFIGURATION",
                "A multi-node Job or Job Run contains a capacity reservation field, but documented BYOR discovery supports direct associations only for single-node Job Runs.",
                resource_type=resource_type,
                resource_id=_string_field(resource, "id"),
            )
            direct_ids = []
            incomplete = True
        else:
            direct_ids = _capacity_reservation_scalar_ids(config)
            if not direct_ids:
                _warning(
                    warnings,
                    "UNSUPPORTED_JOB_BYOR_CONFIGURATION",
                    "A Job or Job Run contains only a plural capacity-reservation field; it is not a documented single-node BYOR association.",
                    resource_type=resource_type,
                    resource_id=_string_field(resource, "id"),
                )
                incomplete = True

    associations = _resource_associations(
        resource,
        resource_type,
        config=config,
        config_prefix=config_prefix,
        found_capacity_reservation_ids=direct_ids,
        association_metadata={"configuration_source": configuration_source},
    )

    target_reference = _compute_target_reference(config)
    if target_reference is not None:
        target_associations, target_incomplete = _compute_target_associations(
            adapter,
            resource,
            resource_type,
            config,
            config_prefix,
            target_reference,
            compartment_id,
            warnings,
            detail_cache,
            configuration_source=configuration_source,
        )
        associations.extend(target_associations)
        incomplete = incomplete or target_incomplete

    return associations, bool(configured_ids) or target_reference is not None, incomplete


def _named_configuration(resource: Mapping[str, Any], key: str) -> tuple[Any, str] | None:
    """Return a named configuration block only when it is a mapping."""

    candidate = _field(resource, key)
    return (candidate, key) if isinstance(candidate, Mapping) else None


def _add_associations(
    bucket: list[dict[str, Any]],
    associations: Iterable[dict[str, Any]],
) -> None:
    existing = {
        (item["capacity_reservation_id"], item["resource_type"], item["resource_id"], item["association_field"])
        for item in bucket
    }
    for association in associations:
        marker = (
            association["capacity_reservation_id"],
            association["resource_type"],
            association["resource_id"],
            association["association_field"],
        )
        if marker not in existing:
            bucket.append(association)
            existing.add(marker)


def discover_capacity_reservation_associations(
    adapter: DiscoveryAdapter,
    compartment_id: str,
    *,
    profile: str | None = None,
    region: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Return a reservation-first, Console-like Data Science association report.

    The report is intentionally limited to resources visible in ``compartment_id``.
    Any configuration that references a reservation outside that visible scope is
    retained in ``unresolved_associations`` instead of being treated as unused.
    """

    if not compartment_id:
        raise DiscoveryError("--compartment-id is required.")
    selected_types = ALL_RESOURCE_TYPES
    warnings: list[dict[str, Any]] = []
    incomplete = False

    try:
        reservation_summaries = adapter.list_capacity_reservations(compartment_id)
    except Exception as error:
        raise DiscoveryError("Could not list Compute Capacity Reservations: {}".format(error)) from error

    reservations: list[dict[str, Any]] = []
    for summary in reservation_summaries:
        summary = to_plain(summary)
        reservation_id = _string_field(summary, "id")
        if not reservation_id:
            _warning(
                warnings,
                "RESERVATION_WITHOUT_OCID",
                "Compute returned a reservation summary without an OCID; it was skipped.",
            )
            incomplete = True
            continue
        try:
            detail = to_plain(adapter.get_capacity_reservation(reservation_id))
        except Exception as error:
            # List summaries lack instanceReservationConfigs. Retain the row but mark
            # it incomplete rather than silently producing a misleading shape summary.
            _warning(
                warnings,
                "RESERVATION_DETAIL_UNAVAILABLE",
                "Could not read a listed capacity reservation's shape configuration.",
                reservation_id=reservation_id,
                error=str(error),
            )
            detail = summary
            incomplete = True
        reservations.append(_reservation_info(detail))

    reservations.sort(key=lambda item: ((item["reservation_name"] or "").lower(), item["reservation_id"]))
    reservations_by_id = {item["reservation_id"]: item for item in reservations}

    associations: list[dict[str, Any]] = []
    job_cache: dict[str, Mapping[str, Any]] = {}
    detail_cache: dict[str, dict[str, Mapping[str, Any]]] = {}

    for resource_type in selected_types:
        if not adapter.supports(resource_type):
            _warning(
                warnings,
                "RESOURCE_TYPE_UNSUPPORTED",
                "The OCI client does not expose a Data Science resource type required for full discovery.",
                resource_type=resource_type,
            )
            incomplete = True
            continue
        try:
            resources = _list_and_get(adapter, resource_type, compartment_id, warnings, detail_cache)
        except UnsupportedResourceType:
            _warning(
                warnings,
                "RESOURCE_TYPE_UNSUPPORTED",
                "The OCI client does not expose a Data Science resource type required for full discovery.",
                resource_type=resource_type,
            )
            incomplete = True
            continue

        # A list failure was converted into a warning by _list_and_get. It must make
        # no-association rows indeterminate rather than falsely asserting no usage.
        if any(
            warning["code"] in {"RESOURCE_LIST_UNAVAILABLE", "RESOURCE_DETAIL_UNAVAILABLE"}
            and warning.get("resource_type") == resource_type
            for warning in warnings
        ):
            incomplete = True

        if resource_type == "job":
            for job in resources:
                job_id = _string_field(job, "id")
                if job_id:
                    job_cache[job_id] = job
                job_config, job_prefix = _config(job, "job")
                job_associations, _, job_incomplete = _configuration_associations(
                    adapter,
                    job,
                    "job",
                    job_config,
                    job_prefix,
                    compartment_id,
                    warnings,
                    detail_cache,
                    configuration_source="job_configuration",
                    single_node_job_only=True,
                )
                _add_associations(associations, job_associations)
                incomplete = incomplete or job_incomplete
            continue

        if resource_type != "job_run":
            for resource in resources:
                resource_config, resource_prefix = _config(resource, resource_type)
                resource_associations, _, resource_incomplete = _configuration_associations(
                    adapter,
                    resource,
                    resource_type,
                    resource_config,
                    resource_prefix,
                    compartment_id,
                    warnings,
                    detail_cache,
                    configuration_source="resource_configuration",
                )
                _add_associations(associations, resource_associations)
                incomplete = incomplete or resource_incomplete
            continue

        for job_run in resources:
            resolved_run_configuration = False
            # The override only wins when it explicitly configures a direct
            # reservation or a Compute Target. An empty override must not mask the
            # run's effective configuration snapshot.
            for configuration_key, configuration_source in (
                ("jobInfrastructureConfigurationOverrideDetails", "job_run_override"),
                ("jobInfrastructureConfigurationDetails", "job_run_effective_configuration"),
            ):
                named_config = _named_configuration(job_run, configuration_key)
                if named_config is None:
                    continue
                run_config, run_prefix = named_config
                run_associations, has_effective_configuration, run_incomplete = _configuration_associations(
                    adapter,
                    job_run,
                    "job_run",
                    run_config,
                    run_prefix,
                    compartment_id,
                    warnings,
                    detail_cache,
                    configuration_source=configuration_source,
                    single_node_job_only=True,
                )
                incomplete = incomplete or run_incomplete
                if has_effective_configuration:
                    _add_associations(associations, run_associations)
                    resolved_run_configuration = True
                    break

            if resolved_run_configuration:
                continue

            # A single-node run without an effective direct/Compute Target
            # configuration can inherit the reservation from the parent Job.
            job_id = _string_field(job_run, "jobId")
            if not job_id:
                continue
            parent_job = job_cache.get(job_id)
            if parent_job is None:
                try:
                    parent_job_detail = to_plain(adapter.get_resource("job", job_id))
                    if not isinstance(parent_job_detail, Mapping):
                        raise DiscoveryError("OCI returned a non-object parent Job detail.")
                    parent_job = parent_job_detail
                    job_cache[job_id] = parent_job
                    detail_cache.setdefault("job", {})[job_id] = parent_job
                except Exception as error:
                    _warning(
                        warnings,
                        "PARENT_JOB_UNAVAILABLE",
                        "Could not resolve a Job Run's parent Job configuration.",
                        resource_type="job_run",
                        resource_id=_string_field(job_run, "id"),
                        job_id=job_id,
                        error=str(error),
                    )
                    incomplete = True
                    continue
            parent_config, parent_prefix = _config(parent_job, "job")
            parent_associations, _, parent_incomplete = _configuration_associations(
                adapter,
                job_run,
                "job_run",
                parent_config,
                "job.{}".format(parent_prefix) if parent_prefix else "job",
                compartment_id,
                warnings,
                detail_cache,
                configuration_source="parent_job_fallback",
                single_node_job_only=True,
            )
            _add_associations(associations, parent_associations)
            incomplete = incomplete or parent_incomplete

    by_reservation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unresolved_associations: list[dict[str, Any]] = []
    for association in associations:
        reservation_id = association["capacity_reservation_id"]
        if association.get("association_visibility") == "compute_target_outside_selected_compartment":
            unresolved_associations.append(
                {
                    **association,
                    "association_status": "compute_target_outside_selected_compartment",
                    "message": (
                        "The workload reaches this reservation through a Compute Target outside the selected "
                        "compartment, so the association was not joined into the same-compartment report."
                    ),
                }
            )
            continue
        if reservation_id in reservations_by_id:
            by_reservation[reservation_id].append(association)
        else:
            unresolved_associations.append(
                {
                    **association,
                    "association_status": "reservation_not_visible_in_selected_compartment",
                    "message": (
                        "The Data Science resource explicitly references this reservation, but the reservation "
                        "was not visible in the selected compartment. It may be cross-compartment or unauthorized."
                    ),
                }
            )

    rows: list[dict[str, Any]] = []
    no_association_status = "indeterminate_due_to_read_errors" if incomplete else "no_configured_association_found"
    for reservation in reservations:
        matching = sorted(
            by_reservation[reservation["reservation_id"]],
            key=lambda item: (
                item["resource_type"],
                (item["resource_name"] or "").lower(),
                item["resource_id"] or "",
                item["association_field"],
            ),
        )
        if matching:
            for association in matching:
                rows.append(
                    {
                        "row_type": "association",
                        "service": "Data Science",
                        "association_status": "configured",
                        **reservation,
                        **association,
                    }
                )
            continue
        rows.append(
            {
                "row_type": "no_association",
                "service": "Data Science",
                "association_status": no_association_status,
                **reservation,
                "resource_id": None,
                "resource_name": None,
                "resource_type": None,
                "resource_type_display": None,
                "resource_state": None,
                "resource_compartment_id": None,
                "resource_created": None,
                "associated_resource_shape": None,
                "associated_resource_count": None,
                "capacity_reservation_id": reservation["reservation_id"],
                "association_field": None,
                "association_source": None,
                "configuration_source": None,
                "compute_target_id": None,
                "compute_target_name": None,
                "compute_target_compartment_id": None,
            }
        )

    unresolved_associations.sort(
        key=lambda item: (
            item["capacity_reservation_id"],
            item["resource_type"],
            item["resource_id"] or "",
            item["association_field"],
        )
    )
    generated_at = generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "schema_version": "1.0",
        "report_type": "configured_data_science_capacity_reservation_associations",
        "generated_at": generated_at,
        "complete": not incomplete,
        "scope": {
            "compartment_id": compartment_id,
            "resource_types": list(selected_types),
            "profile": profile,
            "region": region,
            "source": adapter.source_name,
        },
        "limitations": [
            "Rows are explicit Data Science BYOR configuration associations, not proof of active Compute consumption.",
            "The report never derives an association from usedInstanceCount or the Compute created-instances list.",
            "Only resources and reservations authorized and visible in the selected compartment are queried.",
            "Compute Console registration/CTA eligibility is not exposed by this report.",
        ],
        "reservations": reservations,
        "rows": rows,
        "unresolved_associations": unresolved_associations,
        "warnings": warnings,
    }
