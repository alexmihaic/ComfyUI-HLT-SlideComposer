from __future__ import annotations

import pytest

from hlt_slide.config import CanvasSize, Rect, resolve_canvas_size
from hlt_slide.exceptions import InvalidCanvasError


def test_rect_rejects_negative_dimensions() -> None:
    with pytest.raises(InvalidCanvasError):
        Rect(x=0, y=0, width=-1, height=10)

    with pytest.raises(InvalidCanvasError):
        Rect(x=0, y=0, width=10, height=-1)


def test_known_resolution_preset_resolves_exact_size() -> None:
    result = resolve_canvas_size("9:16 Social Â· 1080x1920")

    assert result.size == CanvasSize(width=1080, height=1920)
    assert result.warnings == ()


def test_custom_resolution_validates_dimensions() -> None:
    result = resolve_canvas_size("Custom", custom_width=2048, custom_height=1024)

    assert result.size == CanvasSize(width=2048, height=1024)

    with pytest.raises(InvalidCanvasError):
        resolve_canvas_size("Custom", custom_width=0, custom_height=1024)


def test_background_size_uses_background_dimensions_or_fallback_warning() -> None:
    with_background = resolve_canvas_size(
        "Background size",
        background_size=CanvasSize(width=640, height=480),
    )
    without_background = resolve_canvas_size("Background size")

    assert with_background.size == CanvasSize(width=640, height=480)
    assert with_background.warnings == ()
    assert without_background.size == CanvasSize(width=1080, height=1920)
    assert len(without_background.warnings) == 1
    assert without_background.warnings[0].startswith("[HLT Slide Composer]")


def test_unknown_preset_raises_clear_error() -> None:
    with pytest.raises(InvalidCanvasError, match="Unknown canvas preset"):
        resolve_canvas_size("Poster")
