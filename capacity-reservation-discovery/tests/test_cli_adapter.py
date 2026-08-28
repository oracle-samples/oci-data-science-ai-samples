# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from __future__ import annotations

from discovery.adapters import CLIAdapter


def test_cli_discovery_disables_per_resource_retries() -> None:
    adapter = CLIAdapter(
        oci_cli="oci",
        config_file="/tmp/oci-config",
        profile="TEST",
        region="us-ashburn-1",
        auth="security_token",
    )

    assert adapter._global_args() == [
        "--output",
        "json",
        "--no-retry",
        "--config-file",
        "/tmp/oci-config",
        "--profile",
        "TEST",
        "--region",
        "us-ashburn-1",
        "--auth",
        "security_token",
    ]
