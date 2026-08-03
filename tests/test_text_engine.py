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


def test_fit_text_can_preserve_long_words_for_text_composer() -> None:
    fitted = fit_text(
        "GENERAR CONTEXTO CRITERIO",
        font_path=None,
        preferred_size=42,
        minimum_size=10,
        max_width=130,
        max_height=200,
        max_lines=5,
        line_spacing=2,
        break_long_words=False,
    )

    assert "GENER" not in fitted.lines
    assert "AR" not in fitted.lines
    assert "CONT" not in fitted.lines
    assert "EXTO" not in fitted.lines
    assert "CRITE" not in fitted.lines
    assert "RIO" not in fitted.lines


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


def test_draw_text_in_rect_compensates_bbox_offsets_inside_rect() -> None:
    image = Image.new("RGBA", (180, 90), (0, 0, 0, 0))
    rect = Rect(x=40, y=24, width=90, height=34)
    result = draw_text_in_rect(
        image,
        rect,
        "Ágyp",
        font_path=None,
        preferred_size=34,
        minimum_size=34,
        max_lines=1,
        line_spacing=0,
        color=(233, 33, 36, 255),
        vertical_align="center",
        clip=True,
    )

    bounds = _ink_bounds(result)

    assert bounds is not None
    left, top, right, bottom = bounds
    assert left >= rect.x
    assert right <= rect.right - 1
    assert top >= rect.y
    assert bottom <= rect.bottom - 1


def test_draw_text_in_rect_vertical_alignment_and_clipping_modes() -> None:
    rect = Rect(x=10, y=10, width=120, height=50)
    tops: dict[str, int] = {}
    for align in ("top", "center", "bottom"):
        image = Image.new("RGBA", (140, 80), (0, 0, 0, 0))
        result = draw_text_in_rect(
            image,
            rect,
            "ASC\npgy",
            font_path=None,
            preferred_size=24,
            minimum_size=24,
            max_lines=2,
            line_spacing=0,
            color=(233, 33, 36, 255),
            vertical_align=align,
            clip=True,
        )
        bounds = _ink_bounds(result)
        assert bounds is not None
        tops[align] = bounds[1]
        assert bounds[1] >= rect.y
        assert bounds[3] <= rect.bottom - 1

    assert tops["top"] <= tops["center"] <= tops["bottom"]

    clipped = draw_text_in_rect(
        Image.new("RGBA", (140, 80), (0, 0, 0, 0)),
        Rect(x=10, y=10, width=120, height=10),
        "gyp",
        font_path=None,
        preferred_size=34,
        minimum_size=34,
        max_lines=1,
        line_spacing=0,
        color=(233, 33, 36, 255),
        vertical_align="top",
        clip=True,
    )
    unclipped = draw_text_in_rect(
        Image.new("RGBA", (140, 80), (0, 0, 0, 0)),
        Rect(x=10, y=10, width=120, height=10),
        "gyp",
        font_path=None,
        preferred_size=34,
        minimum_size=34,
        max_lines=1,
        line_spacing=0,
        color=(233, 33, 36, 255),
        vertical_align="top",
        clip=False,
    )

    clipped_bounds = _ink_bounds(clipped)
    unclipped_bounds = _ink_bounds(unclipped)
    assert clipped_bounds is not None
    assert unclipped_bounds is not None
    assert clipped_bounds[3] <= 19
    assert unclipped_bounds[3] > 19


def _ink_bounds(image: Image.Image) -> tuple[int, int, int, int] | None:
    pixels = []
    rgba = image.convert("RGBA")
    for y in range(rgba.height):
        for x in range(rgba.width):
            red, green, blue, alpha = rgba.getpixel((x, y))
            if alpha > 0 and red > 180 and green < 90 and blue < 90:
                pixels.append((x, y))
    if not pixels:
        return None
    return (
        min(x for x, _ in pixels),
        min(y for _, y in pixels),
        max(x for x, _ in pixels),
        max(y for _, y in pixels),
    )
