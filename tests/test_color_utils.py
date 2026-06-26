from __future__ import annotations

import warnings

from hlt_slide.color_utils import parse_color


def test_parse_color_accepts_short_rgb_with_or_without_hash() -> None:
    assert parse_color("#E12") == (238, 17, 34, 255)
    assert parse_color("e12") == (238, 17, 34, 255)


def test_parse_color_accepts_rgb_and_rgba_hex() -> None:
    assert parse_color("#E92124") == (233, 33, 36, 255)
    assert parse_color("00112280") == (0, 17, 34, 128)


def test_parse_color_normalizes_spaces_and_case() -> None:
    assert parse_color("  #aAbBcC  ") == (170, 187, 204, 255)


def test_parse_color_uses_fallback_and_warns_for_invalid_values() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        parsed = parse_color("not-a-color", fallback=(1, 2, 3, 4))

    assert parsed == (1, 2, 3, 4)
    assert len(caught) == 1
    assert str(caught[0].message).startswith("[HLT Slide Composer]")
