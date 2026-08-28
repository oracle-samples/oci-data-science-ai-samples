# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from pathlib import Path


TERRAFORM_DIRECTORY = Path(__file__).resolve().parents[1] / "terraform"


def test_terraform_uses_read_only_external_data_source_and_string_result_contract() -> None:
    main_tf = (TERRAFORM_DIRECTORY / "main.tf").read_text(encoding="utf-8")
    wrapper = (TERRAFORM_DIRECTORY / "discover_capacity_reservation_usage_external.py").read_text(
        encoding="utf-8"
    )

    assert 'data "external" "capacity_reservation_usage"' in main_tf
    assert "jsondecode(data.external.capacity_reservation_usage.result.report_json)" in main_tf
    assert '"report_json"' in wrapper
    assert "--terraform-external" in wrapper


def test_terraform_always_uses_the_complete_data_science_scope() -> None:
    variables_tf = (TERRAFORM_DIRECTORY / "variables.tf").read_text(encoding="utf-8")
    main_tf = (TERRAFORM_DIRECTORY / "main.tf").read_text(encoding="utf-8")
    tfvars_example = (TERRAFORM_DIRECTORY / "terraform.tfvars.example").read_text(
        encoding="utf-8"
    )

    assert "resource_types" not in variables_tf
    assert "resource_types" not in main_tf
    assert "resource_types" not in tfvars_example
    assert "allow_non_preview_client" not in variables_tf
    assert "allow_non_preview_client" not in main_tf
    assert "allow_non_preview_client" not in tfvars_example
