# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from discovery.render import canonical_json, render_table


def test_console_like_table_renders_no_association_and_indeterminate_rows() -> None:
    report = {
        "rows": [
            {
                "reservation_name": "Alpha",
                "reservation_state": "ACTIVE",
                "reservation_shape_summary": "VM.GPU.A10.1: 0/1",
                "resource_type_display": None,
                "resource_name": None,
                "resource_state": None,
                "associated_resource_shape": None,
                "associated_resource_count": None,
                "association_status": "no_configured_association_found",
            },
            {
                "reservation_name": "Beta",
                "reservation_state": "ACTIVE",
                "reservation_shape_summary": "VM.GPU.A10.1: 0/1",
                "resource_type_display": None,
                "resource_name": None,
                "resource_state": None,
                "associated_resource_shape": None,
                "associated_resource_count": None,
                "association_status": "indeterminate_due_to_read_errors",
            },
        ]
    }

    rendered = render_table(report)

    assert "No Data Science resources" in rendered
    assert "Indeterminate (see warnings)" in rendered
    assert canonical_json({"b": 1, "a": 2}, pretty=False) == '{"a":2,"b":1}'
