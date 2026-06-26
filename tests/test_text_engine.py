from __future__ import annotations

from PIL import Image

from hlt_slide.config import Rect
from hlt_slide.text_engine import draw_text_in_rect, fit_text


def test_fit_text_handles_empty_text_without_truncation() -> None:
    fitted = fit_text(
        "",
        font_path=None,
        preferred_size=40,
        minimum_size=12,
        max_width=200,
        max_height=80,
        max_lines=2,
        line_spacing=4,
    )

    assert fitted.lines == ()
    assert fitted.width == 0
    assert fitted.height == 0
    assert fitted.was_truncated is False


def test_fit_text_keeps_short_text_on_one_line() -> None:
    fitted = fit_text(
        "Short title",
        font_path=None,
        preferred_size=40,
        minimum_size=12,
        max_width=400,
        max_height=80,
        max_lines=2,
        line_spacing=4,
    )

    assert fitted.lines == ("Short title",)
    assert fitted.font_size == 40
    assert fitted.was_truncated is False


def test_fit_text_wraps_words_and_respects_manual_breaks() -> None:
    wrapped = fit_text(
        "alpha beta gamma delta",
        font_path=None,
        preferred_size=30,
        minimum_size=12,
        max_width=140,
        max_height=120,
        max_lines=3,
        line_spacing=4,
    )
    manual = fit_text(
        "alpha\nbeta gamma",
        font_path=None,
        preferred_size=30,
        minimum_size=12,
        max_width=400,
        max_height=120,
        max_lines=3,
        line_spacing=4,
    )

    assert len(wrapped.lines) >= 2
    assert manual.lines[0] == "alpha"
    assert "beta" in manual.lines[1]


def test_fit_text_reduces_font_before_truncating() -> None:
    fitted = fit_text(
        "A moderately long heading",
        font_path=None,
        preferred_size=60,
        minimum_size=12,
        max_width=180,
        max_height=70,
        max_lines=2,
        line_spacing=4,
    )

    assert fitted.font_size < 60
    assert fitted.font_size >= 12
    assert fitted.was_truncated is False


def test_fit_text_truncates_as_last_resort_with_ellipsis() -> None:
    fitted = fit_text(
        "Supercalifragilisticexpialidocious",
        font_path=None,
        preferred_size=22,
        minimum_size=22,
        max_width=80,
        max_height=30,
        max_lines=1,
        line_spacing=0,
    )

    assert fitted.was_truncated is True
    assert fitted.lines
    assert fitted.lines[-1].endswith("…")
    assert fitted.width <= 80


def test_fit_text_supports_uppercase() -> None:
    fitted = fit_text(
        "mixed Case",
        font_path=None,
        preferred_size=24,
        minimum_size=12,
        max_width=300,
        max_height=60,
        max_lines=1,
        line_spacing=0,
        uppercase=True,
    )

    assert fitted.lines == ("MIXED CASE",)


def test_draw_text_in_rect_centers_text_and_uses_color() -> None:
    image = Image.new("RGB", (240, 120), (0, 0, 0))
    rect = Rect(x=20, y=20, width=200, height=80)
    result = draw_text_in_rect(
        image,
        rect,
        "Centered",
        font_path=None,
        preferred_size=34,
        minimum_size=12,
        max_lines=1,
        line_spacing=0,
        color=(233, 33, 36, 255),
    )

    red_pixels = [
        (x, y)
        for y in range(result.height)
        for x in range(result.width)
        if result.getpixel((x, y))[0] > 180 and result.getpixel((x, y))[1] < 80
    ]

    assert red_pixels
    average_x = sum(x for x, _ in red_pixels) / len(red_pixels)
    average_y = sum(y for _, y in red_pixels) / len(red_pixels)
    assert 90 <= average_x <= 150
    assert 40 <= average_y <= 80
