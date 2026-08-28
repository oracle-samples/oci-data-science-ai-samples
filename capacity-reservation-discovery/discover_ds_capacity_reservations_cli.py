#!/usr/bin/env python3
# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Discover explicit Data Science capacity-reservation associations through the public OCI CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from discovery.adapters import CLIAdapter
from discovery.engine import ALL_RESOURCE_TYPES, DiscoveryError, discover_capacity_reservation_associations
from discovery.preflight import validate_oci_cli
from discovery.render import render_report, write_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only, same-compartment report of explicitly configured Data Science "
            "capacity-reservation associations using a public OCI CLI that exposes the "
            "required Data Science capacity-reservation API fields."
        )
    )
    parser.add_argument("--compartment-id", help="OCI compartment OCID for reservations and Data Science resources.")
    parser.add_argument("--oci-cli", default="oci", help="OCI CLI executable (default: oci).")
    parser.add_argument("--profile", default="DEFAULT", help="OCI CLI profile.")
    parser.add_argument("--config-file", help="Optional OCI CLI config file path.")
    parser.add_argument("--region", help="Optional OCI region override.")
    parser.add_argument(
        "--auth",
        help="Optional OCI CLI --auth value, such as security_token or instance_principal.",
    )
    parser.add_argument("--output", choices=("json", "table", "markdown"), default="json")
    parser.add_argument("--output-file", help="Write the rendered report to this local path instead of stdout.")
    parser.add_argument("--check-prereqs", action="store_true", help="Validate the public OCI CLI without calling OCI.")
    return parser


def _run(args: argparse.Namespace) -> dict[str, Any]:
    version = validate_oci_cli(args.oci_cli)
    if args.check_prereqs:
        return {
            "oci_cli_version": version,
            "resource_types": list(ALL_RESOURCE_TYPES),
            "status": "ready",
        }
    if not args.compartment_id:
        raise DiscoveryError("--compartment-id is required unless --check-prereqs is used.")

    adapter = CLIAdapter(
        oci_cli=args.oci_cli,
        config_file=args.config_file,
        profile=args.profile,
        region=args.region,
        auth=args.auth,
    )
    return discover_capacity_reservation_associations(
        adapter,
        args.compartment_id,
        profile=args.profile,
        region=args.region,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = _run(args)
        write_output(render_report(report, args.output), args.output_file)
        return 0
    except (DiscoveryError, OSError, ValueError) as error:
        print("Capacity-reservation discovery failed: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
