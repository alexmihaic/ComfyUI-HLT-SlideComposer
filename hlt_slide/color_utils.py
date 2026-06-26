"""Color parsing utilities."""

from __future__ import annotations

import re
import warnings

from .exceptions import prefixed_message


RGBA = tuple[int, int, int, int]
_HEX_PATTERN = re.compile(r"^[0-9a-fA-F]+$")


def parse_color(value: str | None, fallback: RGBA = (0, 0, 0, 255)) -> RGBA:
    normalized = "" if value is None else value.strip()
    if normalized.startswith("#"):
        normalized = normalized[1:]

    if len(normalized) == 3 and _HEX_PATTERN.match(normalized):
        expanded = "".join(channel * 2 for channel in normalized)
        return _parse_hex_rgba(expanded + "FF")

    if len(normalized) == 6 and _HEX_PATTERN.match(normalized):
        return _parse_hex_rgba(normalized + "FF")

    if len(normalized) == 8 and _HEX_PATTERN.match(normalized):
        return _parse_hex_rgba(normalized)

    warnings.warn(
        prefixed_message(f"Invalid color {value!r}; using fallback."),
        stacklevel=2,
    )
    return fallback


def _parse_hex_rgba(value: str) -> RGBA:
    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
        int(value[6:8], 16),
    )
