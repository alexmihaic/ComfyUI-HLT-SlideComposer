from __future__ import annotations

import pytest
from PIL import Image

from hlt_slide.config import CanvasSize
from hlt_slide.exceptions import HLTSlideError
from hlt_slide.layouts import select_auto_social_layout
from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack


def _item(color: tuple[int, int, int], label: str = "") -> SlideItem:
    return SlideItem(Image.new("RGB", (80, 60), color), label=label)


def test_auto_social_selector_uses_active_image_count() -> None:
    assert select_auto_social_layout(1) == "vertical_stack"
    assert select_auto_social_layout(2) == "vertical_stack"
    assert select_auto_social_layout(3) == "vertical_stack"
    assert select_auto_social_layout(4) == "grid_2x2"


def test_auto_social_selector_rejects_invalid_counts() -> None:
    with pytest.raises(HLTSlideError, match="requires 1 to 4"):
        select_auto_social_layout(0)

    with pytest.raises(HLTSlideError, match="requires 1 to 4"):
        select_auto_social_layout(5)


def test_auto_social_with_four_images_matches_grid_output() -> None:
    items = (
        _item((255, 0, 0), "A"),
        _item((0, 255, 0), "B"),
        _item((0, 0, 255), "C"),
        _item((255, 255, 0), "D"),
    )
    settings = {
        "background_mode": "image_with_overlay",
        "background_color": "#101010",
        "overlay_opacity": 0.2,
        "corner_radius": 0,
        "image_fit": "cover",
    }
    background = Image.new("RGB", (64, 64), (100, 100, 100))
    logo = Image.new("RGBA", (60, 20), (233, 33, 36, 160))

    auto = render_vertical_stack(
        items,
        title="AUTO",
        canvas_size=CanvasSize(420, 640),
        background_image=background,
        logo_image=logo,
        settings=RenderSettings(layout="auto_social", **settings),
    )
    grid = render_vertical_stack(
        items,
        title="AUTO",
        canvas_size=CanvasSize(420, 640),
        background_image=background,
        logo_image=logo,
        settings=RenderSettings(layout="grid_2x2", **settings),
    )

    assert auto.tobytes() == grid.tobytes()


def test_auto_social_with_three_images_uses_vertical_stack() -> None:
    items = (
        _item((255, 0, 0), "A"),
        _item((0, 255, 0), "B"),
        _item((0, 0, 255), "C"),
    )
    auto = render_vertical_stack(
        items,
        title="AUTO",
        canvas_size=CanvasSize(360, 720),
        settings=RenderSettings(layout="auto_social", corner_radius=0),
    )
    vertical = render_vertical_stack(
        items,
        title="AUTO",
        canvas_size=CanvasSize(360, 720),
        settings=RenderSettings(layout="vertical_stack", corner_radius=0),
    )

    assert auto.size == (360, 720)
    assert auto.mode == "RGB"
    assert auto.tobytes() == vertical.tobytes()


def test_auto_social_handles_interleaved_optional_inputs_by_active_count() -> None:
    items = (
        _item((255, 0, 0), "A"),
        SlideItem(None, "missing"),  # type: ignore[arg-type]
        _item((0, 0, 255), "C"),
        SlideItem(None, "missing"),  # type: ignore[arg-type]
    )
    auto = render_vertical_stack(
        items,
        canvas_size=CanvasSize(360, 720),
        settings=RenderSettings(layout="auto_social", corner_radius=0),
    )
    vertical = render_vertical_stack(
        (_item((255, 0, 0), "A"), _item((0, 0, 255), "C")),
        canvas_size=CanvasSize(360, 720),
        settings=RenderSettings(layout="vertical_stack", corner_radius=0),
    )

    assert auto.tobytes() == vertical.tobytes()


def test_auto_social_debug_renders_layout_diagnostic() -> None:
    output = render_vertical_stack(
        [
            _item((255, 0, 0)),
            _item((0, 255, 0)),
            _item((0, 0, 255)),
            _item((255, 255, 0)),
        ],
        canvas_size=CanvasSize(420, 640),
        settings=RenderSettings(layout="auto_social", debug_layout=True, corner_radius=0),
    )

    assert output.mode == "RGB"
    assert output.size == (420, 640)
    assert _has_debug_pixel(output)


def _has_debug_pixel(image: Image.Image) -> bool:
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue = image.getpixel((x, y))
            if blue > 180 and red < 90:
                return True
    return False
