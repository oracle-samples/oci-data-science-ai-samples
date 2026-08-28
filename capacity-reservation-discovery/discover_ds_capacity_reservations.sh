#!/usr/bin/env bash
# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

# Thin POSIX-friendly entry point for the public OCI CLI implementation.
set -euo pipefail

script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${script_directory}/discover_ds_capacity_reservations_cli.py" "$@"
