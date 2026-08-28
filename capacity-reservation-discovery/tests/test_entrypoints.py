# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from __future__ import annotations

import inspect
import io

import pytest

import discover_ds_capacity_reservations as sdk_entrypoint
import discover_ds_capacity_reservations_cli as cli_entrypoint
from discovery.engine import DiscoveryError, discover_capacity_reservation_associations


def test_entrypoints_do_not_expose_a_resource_type_selector() -> None:
    for entrypoint in (sdk_entrypoint, cli_entrypoint):
        parser = entrypoint.build_parser()
        assert all(action.dest != "resource_types" for action in parser._actions)
        with pytest.raises(SystemExit):
            parser.parse_args(["--resource-types", "console"])

    assert "resource_types" not in inspect.signature(discover_capacity_reservation_associations).parameters


def test_entrypoints_do_not_expose_a_nonpublic_client_escape_hatch() -> None:
    for entrypoint in (sdk_entrypoint, cli_entrypoint):
        parser = entrypoint.build_parser()
        assert all(action.dest != "allow_non_preview_client" for action in parser._actions)
        with pytest.raises(SystemExit):
            parser.parse_args(["--allow-non-preview-client"])


def test_terraform_external_rejects_the_removed_selector(monkeypatch: pytest.MonkeyPatch) -> None:
    parser = sdk_entrypoint.build_parser()
    monkeypatch.setattr(
        sdk_entrypoint.sys,
        "stdin",
        io.StringIO('{"compartment_id":"compartment-a","resource_types_json":"[\\"console\\"]"}'),
    )

    with pytest.raises(DiscoveryError, match="no longer supported"):
        sdk_entrypoint._external_args(parser)
