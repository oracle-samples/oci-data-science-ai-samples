# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

"""Normalize OCI SDK objects and API payload variants without losing OCIDs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Iterable, Iterator, Optional, Tuple, Union


PathPart = Union[str, int]
Path = Tuple[PathPart, ...]


@dataclass(frozen=True)
class FoundValue:
    """A scalar found in a nested OCI payload."""

    path: Path
    value: Any


def normalize_key(value: Any) -> str:
    """Make snake_case, camelCase, and kebab-case field names comparable."""

    return "".join(character.lower() for character in str(value) if character.isalnum())


def format_path(path: Path) -> str:
    """Render a nested payload path in a human-readable, stable form."""

    output = ""
    for part in path:
        if isinstance(part, int):
            output += "[{}]".format(part)
        elif output:
            output += ".{}".format(part)
        else:
            output = part
    return output


def to_plain(value: Any) -> Any:
    """Convert OCI SDK models, dates, and mappings to JSON-compatible values."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_plain(item) for item in value]

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return to_plain(to_dict())

    swagger_types = getattr(value, "swagger_types", None)
    if isinstance(swagger_types, Mapping):
        return {
            str(key): to_plain(getattr(value, key, None))
            for key in swagger_types
            if hasattr(value, key)
        }

    return str(value)


def _mapping(value: Any) -> Mapping[str, Any]:
    plain = to_plain(value)
    return plain if isinstance(plain, Mapping) else {}


def get_value(value: Any, keys: Iterable[str], default: Any = None) -> Any:
    """Return the first requested matching child, independent of field naming style.

    Callers deliberately pass preference order (for example, ``displayName``, then
    ``name``, then ``id``).  Iterating the payload first would make the returned
    value depend on OCI model serialization order instead.
    """

    mapping = _mapping(value)
    normalized_children: dict[str, Any] = {}
    for key, candidate in mapping.items():
        normalized_children.setdefault(normalize_key(key), candidate)
    for key in keys:
        candidate = normalized_children.get(normalize_key(key), default)
        if candidate is not default:
            return candidate
    return default


def get_path(value: Any, path: Iterable[str], default: Any = None) -> Any:
    """Follow a field path while accepting camelCase/snake_case API variants."""

    current: Any = value
    for key in path:
        marker = object()
        current = get_value(current, [key], marker)
        if current is marker:
            return default
    return current


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _walk(value: Any, path: Path = (), visited: Optional[set[int]] = None) -> Iterator[tuple[Path, Any]]:
    """Walk mappings and sequences once, avoiding cycles in malformed test data."""

    if visited is None:
        visited = set()

    if isinstance(value, Mapping):
        object_id = id(value)
        if object_id in visited:
            return
        visited.add(object_id)
        for key, child in value.items():
            child_path = path + (str(key),)
            yield child_path, child
            yield from _walk(child, child_path, visited)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        object_id = id(value)
        if object_id in visited:
            return
        visited.add(object_id)
        for index, child in enumerate(value):
            child_path = path + (index,)
            yield child_path, child
            yield from _walk(child, child_path, visited)


def find_first_by_keys(value: Any, keys: Iterable[str], value_type: type) -> Optional[FoundValue]:
    """Find the first scalar whose field name and type match the requested aliases."""

    wanted = {normalize_key(key) for key in keys}
    for path, candidate in _walk(to_plain(value)):
        if not path or not isinstance(path[-1], str) or normalize_key(path[-1]) not in wanted:
            continue
        if value_type is int:
            if isinstance(candidate, bool) or not isinstance(candidate, int):
                continue
        elif not isinstance(candidate, value_type):
            continue
        return FoundValue(path=path, value=candidate)
    return None


def find_capacity_reservation_ids(value: Any) -> list[FoundValue]:
    """Find every configured capacity-reservation OCID, preserving first-seen order.

    Model Deployments and Compute Targets can reference more than one reservation;
    reporting only the first one would hide a valid Console-style association.
    """

    scalar_key = normalize_key("capacityReservationId")
    plural_key = normalize_key("capacityReservationIds")
    found: list[FoundValue] = []
    seen: set[tuple[str, str]] = set()

    for path, candidate in _walk(to_plain(value)):
        if not path or not isinstance(path[-1], str):
            continue
        key = normalize_key(path[-1])
        candidates: list[tuple[Path, Any]] = []
        if key == scalar_key and is_nonempty_string(candidate):
            candidates.append((path, candidate.strip()))
        elif key == plural_key and isinstance(candidate, Sequence) and not isinstance(
            candidate, (str, bytes, bytearray)
        ):
            for index, item in enumerate(candidate):
                if is_nonempty_string(item):
                    candidates.append((path + (index,), item.strip()))

        for candidate_path, reservation_id in candidates:
            marker = (reservation_id, format_path(candidate_path))
            if marker not in seen:
                seen.add(marker)
                found.append(FoundValue(path=candidate_path, value=reservation_id))
    return found
