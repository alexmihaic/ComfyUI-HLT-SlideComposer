from __future__ import annotations

from pathlib import Path

from hlt_slide.font_utils import find_system_font_path, load_font, resolve_font


def test_resolve_font_falls_back_for_missing_explicit_path() -> None:
    result = resolve_font("Z:/missing/font.ttf", 24)

    assert result.font.getbbox("HLT")[2] > 0
    assert result.size == 24
    assert len(result.warnings) == 1
    assert result.warnings[0].startswith("[HLT Slide Composer]")


def test_find_system_font_path_returns_existing_path_when_available() -> None:
    path = find_system_font_path()

    if path is not None:
        assert path.exists()


def test_load_font_caches_by_path_and_size() -> None:
    system_font = find_system_font_path()
    if system_font is None:
        first = load_font(None, 18)
        second = load_font(None, 18)
    else:
        first = load_font(Path(system_font), 18)
        second = load_font(Path(system_font), 18)

    assert first is second


def test_explicit_valid_font_path_is_used_when_available() -> None:
    system_font = find_system_font_path()
    if system_font is None:
        return

    result = resolve_font(str(system_font), 20)

    assert result.path == system_font
    assert result.size == 20
    assert result.warnings == ()
