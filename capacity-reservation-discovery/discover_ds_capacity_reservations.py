#!/usr/bin/env python3
# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Discover explicit Data Science capacity-reservation associations through the public Python SDK.

This is a read-only tool. It lists visible Compute Capacity Reservations and
visible Data Science resources in one compartment, then joins the configured
``capacityReservationId`` / ``capacityReservationIds`` fields into Console-like
rows. It does not create, modify, or delete OCI resources.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from discovery.adapters import SDKAdapter
from discovery.engine import ALL_RESOURCE_TYPES, DiscoveryError, discover_capacity_reservation_associations
from discovery.preflight import validate_oci_sdk
from discovery.render import canonical_json, render_report, write_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only, same-compartment report of explicitly configured Data Science "
            "capacity-reservation associations. Requires a public OCI SDK that exposes "
            "the required Data Science capacity-reservation API fields."
        )
    )
    parser.add_argument("--compartment-id", help="OCI compartment OCID for both reservations and Data Science resources.")
    parser.add_argument(
        "--profile",
        default="DEFAULT",
        help="OCI config profile for api_key or security_token authentication.",
    )
    parser.add_argument("--config-file", help="Optional OCI config file path.")
    parser.add_argument("--region", help="Optional OCI region override.")
    parser.add_argument(
        "--auth",
        choices=("api_key", "security_token", "instance_principal", "resource_principal"),
        default="api_key",
        help="SDK authentication mode (default: api_key).",
    )
    parser.add_argument("--output", choices=("json", "table", "markdown"), default="json")
    parser.add_argument("--output-file", help="Write the rendered report to this local path instead of stdout.")
    parser.add_argument(
        "--check-prereqs",
        action="store_true",
        help="Validate the installed public OCI SDK and requested API surface without calling OCI.",
    )
    parser.add_argument(
        "--terraform-external",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser


def _query_string(query: dict[str, Any], key: str, default: str = "") -> str:
    value = query.get(key, default)
    if not isinstance(value, str):
        raise DiscoveryError("Terraform external query field '{}' must be a string.".format(key))
    return value


def _external_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    try:
        query = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        raise DiscoveryError("Terraform external input was not valid JSON: {}".format(error)) from error
    if not isinstance(query, dict):
        raise DiscoveryError("Terraform external input must be a JSON object.")

    if "resource_types_json" in query:
        raise DiscoveryError(
            "resource_types_json is no longer supported; discovery always scans every supported "
            "Data Science capacity-reservation resource type."
        )

    arguments = [
        "--compartment-id",
        _query_string(query, "compartment_id"),
        "--profile",
        _query_string(query, "profile", "DEFAULT"),
        "--auth",
        _query_string(query, "auth", "api_key"),
        "--terraform-external",
    ]
    region = _query_string(query, "region")
    config_file = _query_string(query, "config_file")
    if region:
        arguments.extend(["--region", region])
    if config_file:
        arguments.extend(["--config-file", config_file])
    return parser.parse_args(arguments)


def _run(args: argparse.Namespace) -> dict[str, Any] | None:
    version = validate_oci_sdk()
    if args.check_prereqs:
        return {
            "oci_sdk_version": version,
            "resource_types": list(ALL_RESOURCE_TYPES),
            "status": "ready",
        }

    if not args.compartment_id:
        raise DiscoveryError("--compartment-id is required unless --check-prereqs is used.")
    adapter = SDKAdapter(
        config_file=args.config_file,
        profile=args.profile,
        region=args.region,
        auth=args.auth,
    )
    return discover_capacity_reservation_associations(
        adapter,
        args.compartment_id,
        profile=args.profile if args.auth in {"api_key", "security_token"} else None,
        region=args.region,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    supplied_args = list(sys.argv[1:] if argv is None else argv)
    try:
        args = parser.parse_args(supplied_args)
        if args.terraform_external:
            args = _external_args(parser)
        result = _run(args)
        assert result is not None
        if args.terraform_external:
            # hashicorp/external accepts only string values in its result map.
            print(json.dumps({"report_json": canonical_json(result, pretty=False)}, sort_keys=True))
        else:
            write_output(render_report(result, args.output), args.output_file)
        return 0
    except (DiscoveryError, OSError, ValueError) as error:
        print("Capacity-reservation discovery failed: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
