# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Deterministic JSON and Console-like table rendering for association reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DISPLAY_COLUMNS = (
    ("Reservation", "reservation_name"),
    ("Reservation state", "reservation_state"),
    ("Reservation shape configs", "reservation_shape_summary"),
    ("Resource type", "resource_type_display"),
    ("Resource name", "resource_name"),
    ("Resource state", "resource_state"),
    ("Shape", "associated_resource_shape"),
    ("Count", "associated_resource_count"),
)


def canonical_json(value: Any, *, pretty: bool = True) -> str:
    """Serialize report output consistently for diffing SDK, CLI, and Terraform results."""

    kwargs: dict[str, Any] = {"sort_keys": True, "default": str}
    if pretty:
        kwargs["indent"] = 2
    else:
        kwargs["separators"] = (",", ":")
    return json.dumps(value, **kwargs)


def _display_value(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if value is None or value == "":
        if key == "resource_name":
            if row.get("association_status") == "no_configured_association_found":
                return "No Data Science resources"
            if row.get("association_status") == "indeterminate_due_to_read_errors":
                return "Indeterminate (see warnings)"
        return "-"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def render_table(report: dict[str, Any], *, markdown: bool = False) -> str:
    """Render the same primary columns used by the Capacity Reservation Console view."""

    headers = [column[0] for column in DISPLAY_COLUMNS]
    values = [
        [_display_value(row, key) for _, key in DISPLAY_COLUMNS]
        for row in report.get("rows", [])
    ]
    if not values:
        values = [["No visible Capacity Reservations", "-", "-", "-", "-", "-", "-", "-"]]

    if markdown:
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
        ]
        lines.extend("| " + " | ".join(value.replace("|", "\\|") for value in row) + " |" for row in values)
        return "\n".join(lines)

    widths = [
        max(len(headers[index]), *(len(row[index]) for row in values))
        for index in range(len(headers))
    ]
    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    header = "| " + " | ".join(headers[index].ljust(widths[index]) for index in range(len(headers))) + " |"
    lines = [separator, header, separator]
    lines.extend(
        "| " + " | ".join(row[index].ljust(widths[index]) for index in range(len(headers))) + " |"
        for row in values
    )
    lines.append(separator)
    return "\n".join(lines)


def render_report(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return canonical_json(report)
    if output_format == "table":
        return render_table(report)
    if output_format == "markdown":
        return render_table(report, markdown=True)
    raise ValueError("Unsupported output format '{}'".format(output_format))


def write_output(content: str, output_file: str | None) -> None:
    if output_file:
        Path(output_file).write_text(content + ("" if content.endswith("\n") else "\n"), encoding="utf-8")
    else:
        print(content)
