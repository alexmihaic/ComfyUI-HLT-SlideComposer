from __future__ import annotations

from PIL import Image

from hlt_slide.config import Rect
from hlt_slide.image_utils import compose_image_in_rect, fit_image_to_box


def _vertical_stripes() -> Image.Image:
    image = Image.new("RGB", (40, 120), "black")
    pixels = image.load()
    for y in range(120):
        color = (255, 0, 0) if y < 40 else (0, 255, 0) if y < 80 else (0, 0, 255)
        for x in range(40):
            pixels[x, y] = color
    return image


def _horizontal_stripes() -> Image.Image:
    image = Image.new("RGB", (120, 40), "black")
    pixels = image.load()
    for x in range(120):
        color = (255, 0, 0) if x < 40 else (0, 255, 0) if x < 80 else (0, 0, 255)
        for y in range(40):
            pixels[x, y] = color
    return image


def _dominant(pixel: tuple[int, int, int]) -> str:
    red, green, blue = pixel
    if red > green and red > blue:
        return "red"
    if green > red and green > blue:
        return "green"
    return "blue"


def test_cover_keeps_requested_vertical_crop_anchor_regions() -> None:
    source = _vertical_stripes()

    top = fit_image_to_box(source, (40, 40), fit="cover", crop_anchor="top")
    center = fit_image_to_box(source, (40, 40), fit="cover", crop_anchor="center")
    bottom = fit_image_to_box(source, (40, 40), fit="cover", crop_anchor="bottom")

    assert top.size == (40, 40)
    assert center.size == (40, 40)
    assert bottom.size == (40, 40)
    assert _dominant(top.getpixel((20, 20))) == "red"
    assert _dominant(center.getpixel((20, 20))) == "green"
    assert _dominant(bottom.getpixel((20, 20))) == "blue"


def test_cover_crops_width_without_distorting_aspect_ratio() -> None:
    output = fit_image_to_box(_horizontal_stripes(), (40, 40), fit="cover")

    assert output.size == (40, 40)
    assert _dominant(output.getpixel((20, 20))) == "green"


def test_contain_preserves_full_image_and_fills_letterbox_color() -> None:
    output = fit_image_to_box(
        _horizontal_stripes(),
        (80, 80),
        fit="contain",
        cell_background_color=(10, 20, 30, 255),
    )

    assert output.size == (80, 80)
    assert output.getpixel((40, 5)) == (10, 20, 30)
    assert _dominant(output.getpixel((12, 40))) == "red"
    assert _dominant(output.getpixel((40, 40))) == "green"
    assert _dominant(output.getpixel((68, 40))) == "blue"


def test_stretch_uses_exact_target_size() -> None:
    output = fit_image_to_box(_horizontal_stripes(), (33, 77), fit="stretch")

    assert output.size == (33, 77)


def test_rounded_corners_and_border_are_applied() -> None:
    output = fit_image_to_box(
        Image.new("RGB", (80, 80), (20, 120, 200)),
        (80, 80),
        fit="cover",
        corner_radius=16,
        border_width=4,
        border_color=(255, 0, 0, 255),
    )

    assert output.size == (80, 80)
    assert output.getpixel((0, 0)) == (0, 0, 0, 0)
    assert output.getpixel((40, 2)) == (255, 0, 0, 255)
    assert output.getpixel((40, 40))[:3] == (20, 120, 200)


def test_compose_image_in_rect_places_image_on_canvas() -> None:
    canvas = Image.new("RGB", (100, 100), (0, 0, 0))
    result = compose_image_in_rect(
        canvas,
        Image.new("RGB", (20, 20), (200, 100, 50)),
        Rect(x=10, y=15, width=30, height=25),
        fit="stretch",
    )

    assert result.size == (100, 100)
    assert result.getpixel((9, 15)) == (0, 0, 0)
    assert result.getpixel((10, 15)) == (200, 100, 50)
    assert result.getpixel((39, 39)) == (200, 100, 50)
