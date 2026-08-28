# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Read-only OCI SDK and OCI CLI adapters for Capacity Reservation discovery."""

from __future__ import annotations

import json
import shlex
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .engine import DiscoveryError, UnsupportedResourceType
from .normalization import to_plain


SDK_RESOURCE_METHODS = {
    "notebook_session": ("list_notebook_sessions", "get_notebook_session", "notebook_session_id"),
    "model_deployment": ("list_model_deployments", "get_model_deployment", "model_deployment_id"),
    "job": ("list_jobs", "get_job", "job_id"),
    "job_run": ("list_job_runs", "get_job_run", "job_run_id"),
    "compute_target": ("list_compute_targets", "get_compute_target", "compute_target_id"),
}

CLI_RESOURCE_COMMANDS = {
    "notebook_session": ("notebook-session", "notebook-session-id"),
    "model_deployment": ("model-deployment", "model-deployment-id"),
    "job": ("job", "job-id"),
    "job_run": ("job-run", "job-run-id"),
    "compute_target": ("compute-target", "compute-target-id"),
}


class SDKAdapter:
    """Use the public OCI Python SDK while keeping all operations read-only."""

    source_name = "oci_python_sdk"

    def __init__(
        self,
        *,
        config_file: str | None = None,
        profile: str = "DEFAULT",
        region: str | None = None,
        auth: str = "api_key",
    ) -> None:
        try:
            import oci
        except ImportError as error:
            raise DiscoveryError("The OCI Python SDK is not installed.") from error

        self._oci = oci
        self._region = region
        self._auth = auth
        self._config_file = config_file
        self._profile = profile
        self.compute_client, self.data_science_client = self._create_clients()

    def _create_clients(self) -> tuple[Any, Any]:
        oci = self._oci
        if self._auth in {"api_key", "security_token"}:
            config = self._profile_config()
            if self._auth == "api_key":
                return oci.core.ComputeClient(config), oci.data_science.DataScienceClient(config)

            signer = self._security_token_signer(config)
            return (
                oci.core.ComputeClient(config, signer=signer),
                oci.data_science.DataScienceClient(config, signer=signer),
            )

        if self._auth == "instance_principal":
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        elif self._auth == "resource_principal":
            signer = oci.auth.signers.get_resource_principals_signer()
        else:
            raise DiscoveryError("Unsupported SDK auth mode '{}'.".format(self._auth))

        config = {"region": self._region} if self._region else {}
        compute = oci.core.ComputeClient(config, signer=signer)
        data_science = oci.data_science.DataScienceClient(config, signer=signer)
        if self._region:
            compute.base_client.set_region(self._region)
            data_science.base_client.set_region(self._region)
        return compute, data_science

    def _profile_config(self) -> dict[str, Any]:
        config_kwargs: dict[str, Any] = {"profile_name": self._profile}
        if self._config_file:
            config_kwargs["file_location"] = self._config_file
        config = self._oci.config.from_file(**config_kwargs)
        if self._region:
            config["region"] = self._region
        return config

    def _security_token_signer(self, config: Mapping[str, Any]) -> Any:
        missing = [key for key in ("security_token_file", "key_file") if not config.get(key)]
        if missing:
            raise DiscoveryError(
                "The security-token profile must include security_token_file and key_file."
            )

        try:
            token = Path(str(config["security_token_file"])).expanduser().read_text(encoding="utf-8").strip()
            if not token:
                raise ValueError("empty security token")
            private_key = self._oci.signer.load_private_key_from_file(
                str(Path(str(config["key_file"])).expanduser()),
                config.get("pass_phrase"),
            )
            return self._oci.auth.signers.SecurityTokenSigner(token, private_key)
        except (AttributeError, OSError, TypeError, ValueError) as error:
            raise DiscoveryError(
                "Could not load security-token credentials from the selected OCI profile."
            ) from error

    def supports(self, resource_type: str) -> bool:
        methods = SDK_RESOURCE_METHODS.get(resource_type)
        return bool(
            methods
            and hasattr(self.data_science_client, methods[0])
            and hasattr(self.data_science_client, methods[1])
        )

    def _list_all(self, method: Any, *args: Any) -> list[Mapping[str, Any]]:
        response = self._oci.pagination.list_call_get_all_results(method, *args)
        data = to_plain(response.data)
        if not isinstance(data, list):
            raise DiscoveryError("OCI returned a non-list payload for a list operation.")
        return data

    def list_capacity_reservations(self, compartment_id: str) -> list[Mapping[str, Any]]:
        return self._list_all(self.compute_client.list_compute_capacity_reservations, compartment_id)

    def get_capacity_reservation(self, reservation_id: str) -> Mapping[str, Any]:
        return to_plain(self.compute_client.get_compute_capacity_reservation(reservation_id).data)

    def list_resources(self, resource_type: str, compartment_id: str) -> list[Mapping[str, Any]]:
        methods = SDK_RESOURCE_METHODS.get(resource_type)
        if not methods or not self.supports(resource_type):
            raise UnsupportedResourceType(resource_type)
        return self._list_all(getattr(self.data_science_client, methods[0]), compartment_id)

    def get_resource(self, resource_type: str, resource_id: str) -> Mapping[str, Any]:
        methods = SDK_RESOURCE_METHODS.get(resource_type)
        if not methods or not self.supports(resource_type):
            raise UnsupportedResourceType(resource_type)
        response = getattr(self.data_science_client, methods[1])(**{methods[2]: resource_id})
        return to_plain(response.data)


class CLIAdapter:
    """Use the public OCI CLI and normalize each response into the SDK-shaped core."""

    source_name = "oci_cli"

    def __init__(
        self,
        *,
        oci_cli: str = "oci",
        config_file: str | None = None,
        profile: str = "DEFAULT",
        region: str | None = None,
        auth: str | None = None,
    ) -> None:
        self._command = shlex.split(oci_cli)
        if not self._command:
            raise DiscoveryError("--oci-cli must name an OCI CLI executable.")
        self._config_file = config_file
        self._profile = profile
        self._region = region
        self._auth = auth
        self._supported_resources: dict[str, bool] = {
            resource_type: True for resource_type in CLI_RESOURCE_COMMANDS
        }

    @property
    def command(self) -> list[str]:
        return list(self._command)

    def supports(self, resource_type: str) -> bool:
        return self._supported_resources.get(resource_type, False)

    def _global_args(self) -> list[str]:
        # Discovery records inaccessible resources as warnings.  Retrying every
        # individual detail call can otherwise turn an expected partial-read
        # report into an hours-long scan in a large compartment.
        args = ["--output", "json", "--no-retry"]
        if self._config_file:
            args.extend(["--config-file", self._config_file])
        if self._profile:
            args.extend(["--profile", self._profile])
        if self._region:
            args.extend(["--region", self._region])
        if self._auth:
            args.extend(["--auth", self._auth])
        return args

    @staticmethod
    def _looks_unsupported(stderr: str) -> bool:
        normalized = stderr.lower()
        return any(
            phrase in normalized
            for phrase in ("no such command", "invalid choice", "unknown command", "command not found")
        )

    def _run(self, args: list[str], *, resource_type: str | None = None) -> Any:
        completed = subprocess.run(
            self.command + self._global_args() + args,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            if resource_type and self._looks_unsupported(completed.stderr):
                self._supported_resources[resource_type] = False
                raise UnsupportedResourceType(resource_type)
            message = completed.stderr.strip() or completed.stdout.strip() or "OCI CLI exited with no error text."
            raise DiscoveryError("OCI CLI command failed: {}".format(message))
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise DiscoveryError("OCI CLI returned invalid JSON: {}".format(error)) from error
        return payload.get("data", payload) if isinstance(payload, Mapping) else payload

    def list_capacity_reservations(self, compartment_id: str) -> list[Mapping[str, Any]]:
        data = self._run(
            [
                "compute",
                "capacity-reservation",
                "list",
                "--compartment-id",
                compartment_id,
                "--all",
            ]
        )
        if not isinstance(data, list):
            raise DiscoveryError("OCI CLI returned a non-list capacity reservation payload.")
        return data

    def get_capacity_reservation(self, reservation_id: str) -> Mapping[str, Any]:
        data = self._run(
            [
                "compute",
                "capacity-reservation",
                "get",
                "--capacity-reservation-id",
                reservation_id,
            ]
        )
        if not isinstance(data, Mapping):
            raise DiscoveryError("OCI CLI returned a non-object capacity reservation payload.")
        return data

    def list_resources(self, resource_type: str, compartment_id: str) -> list[Mapping[str, Any]]:
        command = CLI_RESOURCE_COMMANDS.get(resource_type)
        if not command or not self.supports(resource_type):
            raise UnsupportedResourceType(resource_type)
        data = self._run(
            ["data-science", command[0], "list", "--compartment-id", compartment_id, "--all"],
            resource_type=resource_type,
        )
        if not isinstance(data, list):
            raise DiscoveryError("OCI CLI returned a non-list {} payload.".format(resource_type))
        return data

    def get_resource(self, resource_type: str, resource_id: str) -> Mapping[str, Any]:
        command = CLI_RESOURCE_COMMANDS.get(resource_type)
        if not command or not self.supports(resource_type):
            raise UnsupportedResourceType(resource_type)
        data = self._run(
            ["data-science", command[0], "get", "--{}".format(command[1]), resource_id],
            resource_type=resource_type,
        )
        if not isinstance(data, Mapping):
            raise DiscoveryError("OCI CLI returned a non-object {} payload.".format(resource_type))
        return data
