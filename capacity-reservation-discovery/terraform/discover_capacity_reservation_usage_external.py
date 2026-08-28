#!/usr/bin/env python3
# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Terraform external-provider bridge for the sibling public-SDK discovery script.

The external provider only accepts string-valued JSON maps. This wrapper preserves
the report as one canonical JSON string and sends diagnostics exclusively to stderr.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    try:
        query = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        print("Terraform external input was not valid JSON: {}".format(error), file=sys.stderr)
        return 2
    if not isinstance(query, dict):
        print("Terraform external input must be a JSON object.", file=sys.stderr)
        return 2

    configured_path = query.pop("discovery_script_path", "")
    if not isinstance(configured_path, str):
        print("discovery_script_path must be a string.", file=sys.stderr)
        return 2
    script_path = (
        Path(configured_path).expanduser()
        if configured_path
        else Path(__file__).resolve().parent.parent / "discover_ds_capacity_reservations.py"
    )
    if not script_path.is_file():
        print("OCI SDK discovery script was not found at {}.".format(script_path), file=sys.stderr)
        return 2

    completed = subprocess.run(
        [sys.executable, str(script_path), "--terraform-external"],
        input=json.dumps(query),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="" if completed.stderr.endswith("\n") else "\n")
    if completed.returncode != 0:
        return completed.returncode

    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        print("OCI SDK discovery script returned invalid external JSON: {}".format(error), file=sys.stderr)
        return 2
    if not isinstance(result, dict) or not isinstance(result.get("report_json"), str):
        print("OCI SDK discovery script returned an invalid external result map.", file=sys.stderr)
        return 2

    print(json.dumps({"report_json": result["report_json"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
