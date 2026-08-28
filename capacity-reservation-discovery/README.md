# Data Science Capacity Reservation Discovery

This directory contains read-only tools that report explicitly configured Oracle Cloud Infrastructure Data Science capacity-reservation associations in one selected compartment.

The report joins Data Science `capacityReservationId` and `capacityReservationIds` configuration with Compute Capacity Reservations. It reports configured associations, not current consumption. In particular, it never infers an association from Compute used-instance counts or created-instance data.

## Public OCI SDK and CLI prerequisite

Install the latest public OCI Python SDK and OCI CLI from PyPI. This sample intentionally does not pin a generated-client version: it follows the latest public release once that release exposes the required Data Science capacity-reservation fields.

| Client | Public PyPI package |
| --- | --- |
| OCI Python SDK | `oci` |
| OCI CLI | `oci-cli` |

Use Python 3.10 or later. The unit tests additionally require pytest.

    python3 -m venv .venv-byor
    .venv-byor/bin/python -m pip install --upgrade -r requirements.txt

Before accessing OCI, each entry point checks that its installed public client exposes `capacityReservationId` or `capacityReservationIds`. If the check reports that the field is unavailable, upgrade to the latest public package and rerun it after that API surface is present. The tool stops rather than returning a misleading empty report.

## Test

The unit tests do not contact OCI or require the OCI clients:

    python3 -m pip install -r requirements-dev.txt
    make test

## Documentation

This README is the developer documentation for installation, validation, and
use of the discovery tools. The command-line entry points also provide
parameter help through `--help`.

## Scope

Each run stays within one compartment and performs only these read operations:

    compute capacity-reservation list|get
    data-science notebook-session list|get
    data-science model-deployment list|get
    data-science job list|get
    data-science job-run list|get
    data-science compute-target list|get

It scans every supported Data Science resource type: Notebook Sessions, Model Deployments, Jobs, Job Runs, and Compute Targets. The optional Compute Target API surface becomes a warning when unavailable rather than silently narrowing discovery.

The caller must have least-privilege permission to list and get the selected compartment's Compute Capacity Reservations and Data Science resources. The tool does not create, modify, or delete OCI resources.

## Examples

### Run with the public SDK

    .venv-byor/bin/python discover_ds_capacity_reservations.py \
      --compartment-id 'ocid1.compartment.oc1..example' \
      --profile DEFAULT \
      --region '<region>' \
      --output table

For instance or resource principals, use the corresponding authentication mode:

    .venv-byor/bin/python discover_ds_capacity_reservations.py \
      --compartment-id 'ocid1.compartment.oc1..example' \
      --auth instance_principal \
      --output json

Run a no-network prerequisite check with:

    .venv-byor/bin/python discover_ds_capacity_reservations.py --check-prereqs

### Use an OCI security-token profile

For an unexpired OCI session-token profile, provide its config file and profile
name explicitly:

    .venv-byor/bin/python discover_ds_capacity_reservations.py \
      --compartment-id 'ocid1.compartment.oc1..example' \
      --config-file ~/.oci/config \
      --profile '<SESSION_PROFILE>' \
      --auth security_token \
      --region '<region>' \
      --output table

The profile must contain both `security_token_file` and `key_file`. Do not
commit, print, or share those credentials; refresh an expired session outside
this tool.

### Run with the public OCI CLI

    bash discover_ds_capacity_reservations.sh \
      --compartment-id 'ocid1.compartment.oc1..example' \
      --profile DEFAULT \
      --region '<region>' \
      --output markdown

The direct CLI entry point also supports:

    .venv-byor/bin/python discover_ds_capacity_reservations_cli.py --check-prereqs

The CLI accepts the same OCI security-token profile arguments:

    bash discover_ds_capacity_reservations.sh \
      --compartment-id 'ocid1.compartment.oc1..example' \
      --config-file ~/.oci/config \
      --profile '<SESSION_PROFILE>' \
      --auth security_token \
      --region '<region>' \
      --output markdown

## Terraform

The native OCI Terraform provider does not expose the capacity-reservation fields used by this report. The `terraform` directory therefore uses the read-only `hashicorp/external` provider to invoke the same public-SDK discovery script.

    cd terraform
    cp terraform.tfvars.example terraform.tfvars
    terraform init
    terraform plan

The Python executable configured for Terraform must use a public OCI SDK that passes the script's prerequisite check.

Terraform state contains the resulting report, including resource names and OCIDs. Store state in an encrypted, access-controlled backend and never commit state files, credentials, or customer-specific variables.

## Help

For OCI SDK or CLI release support, use the normal OCI support channel. For sample issues, use the parent repository's GitHub issue tracker. Do not include credentials or customer data in a public issue.

## Interpretation and limitations

- A configured row means a visible Data Science resource explicitly names a reservation in its configuration.
- A `no_configured_association_found` row means the read completed without a visible configured reference. It does not prove no workload consumes a reservation.
- An `indeterminate_due_to_read_errors` row means a list or detail read failed; inspect warnings instead of treating the reservation as unused.
- A `reservation_not_visible_in_selected_compartment` row can indicate a cross-compartment reference or authorization boundary.
- Pipelines and Pipeline Runs are excluded because their current backend fields cannot provide valid configured associations.
- The report cannot determine whether a Console call-to-action should be shown or hidden.

## Security

Do not commit OCI credentials, customer configuration, report output, or Terraform state. Use the approved support and security-reporting process for the service.

For responsible security-vulnerability disclosure, see
[the parent repository security policy](../SECURITY.md). Do not report vulnerabilities in public GitHub
issues.

## Contributing

This project welcomes contributions from the community. Before submitting a
pull request, review the [parent repository contribution guide](../CONTRIBUTING.md).

## License

Licensed under the [Universal Permissive License v1.0](../LICENSE.txt) in the
parent repository.
