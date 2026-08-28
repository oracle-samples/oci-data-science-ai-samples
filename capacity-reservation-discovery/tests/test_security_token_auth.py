# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from __future__ import annotations

import sys
import types

import discover_ds_capacity_reservations as sdk_entrypoint
from discovery.adapters import SDKAdapter
from discovery.engine import discover_capacity_reservation_associations


def test_sdk_entrypoint_accepts_security_token_and_preserves_profile(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeAdapter:
        def __init__(self, **kwargs: object) -> None:
            captured["adapter_kwargs"] = kwargs

    def fake_discovery(*args: object, **kwargs: object) -> dict[str, object]:
        captured["discovery_args"] = args
        captured["discovery_kwargs"] = kwargs
        return {"status": "ok"}

    monkeypatch.setattr(sdk_entrypoint, "SDKAdapter", FakeAdapter)
    monkeypatch.setattr(sdk_entrypoint, "validate_oci_sdk", lambda: "public")
    monkeypatch.setattr(sdk_entrypoint, "discover_capacity_reservation_associations", fake_discovery)

    args = sdk_entrypoint.build_parser().parse_args(
        [
            "--compartment-id",
            "compartment-a",
            "--config-file",
            "/tmp/config",
            "--profile",
            "session-profile",
            "--auth",
            "security_token",
        ]
    )
    assert sdk_entrypoint._run(args) == {"status": "ok"}
    assert captured["adapter_kwargs"] == {
        "config_file": "/tmp/config",
        "profile": "session-profile",
        "region": None,
        "auth": "security_token",
    }
    assert captured["discovery_kwargs"] == {"profile": "session-profile", "region": None}


def test_sdk_adapter_uses_security_token_signer(monkeypatch, tmp_path) -> None:
    token_file = tmp_path / "session-token"
    token_file.write_text("token-value", encoding="utf-8")
    key_file = tmp_path / "session-key.pem"
    key_file.write_text("private-key", encoding="utf-8")
    captured: dict[str, object] = {}

    class FakeSecurityTokenSigner:
        def __init__(self, token: str, private_key: object) -> None:
            self.token = token
            self.private_key = private_key

    class FakeComputeClient:
        def __init__(self, config: dict[str, object], signer: object) -> None:
            captured["compute"] = (config, signer)

    class FakeDataScienceClient:
        def __init__(self, config: dict[str, object], signer: object) -> None:
            captured["data_science"] = (config, signer)

    def from_file(**kwargs: object) -> dict[str, object]:
        captured["config_kwargs"] = kwargs
        return {
            "region": "configured-region",
            "security_token_file": str(token_file),
            "key_file": str(key_file),
        }

    def load_private_key_from_file(path: str, pass_phrase: object) -> object:
        captured["key_args"] = (path, pass_phrase)
        return "loaded-private-key"

    fake_oci = types.SimpleNamespace(
        config=types.SimpleNamespace(from_file=from_file),
        signer=types.SimpleNamespace(load_private_key_from_file=load_private_key_from_file),
        auth=types.SimpleNamespace(signers=types.SimpleNamespace(SecurityTokenSigner=FakeSecurityTokenSigner)),
        core=types.SimpleNamespace(ComputeClient=FakeComputeClient),
        data_science=types.SimpleNamespace(DataScienceClient=FakeDataScienceClient),
    )
    monkeypatch.setitem(sys.modules, "oci", fake_oci)

    SDKAdapter(
        config_file="/tmp/config",
        profile="session-profile",
        region="us-ashburn-1",
        auth="security_token",
    )

    assert captured["config_kwargs"] == {
        "profile_name": "session-profile",
        "file_location": "/tmp/config",
    }
    config, signer = captured["compute"]
    assert config["region"] == "us-ashburn-1"
    assert isinstance(signer, FakeSecurityTokenSigner)
    assert signer.token == "token-value"
    assert signer.private_key == "loaded-private-key"
    assert captured["data_science"] == (config, signer)
    assert captured["key_args"] == (str(key_file), None)


def test_security_token_profile_requires_token_and_key(monkeypatch) -> None:
    fake_oci = types.SimpleNamespace(
        config=types.SimpleNamespace(from_file=lambda **_: {"region": "us-ashburn-1"}),
    )
    monkeypatch.setitem(sys.modules, "oci", fake_oci)

    try:
        SDKAdapter(auth="security_token")
    except Exception as error:
        assert "security_token_file and key_file" in str(error)
    else:
        raise AssertionError("security-token profile without credentials should fail")
