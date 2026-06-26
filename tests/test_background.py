from __future__ import annotations

import warnings

from PIL import Image

from hlt_slide.config import CanvasSize
from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack


def _item() -> SlideItem:
    return SlideItem(Image.new("RGB", (40, 40), (240, 240, 240)), label="")


def _striped_background() -> Image.Image:
    image = Image.new("RGB", (90, 30), "black")
    pixels = image.load()
    for x in range(image.width):
        color = (255, 0, 0) if x < 30 else (0, 255, 0) if x < 60 else (0, 0, 255)
        for y in range(image.height):
            pixels[x, y] = color
    return image


def test_solid_background_ignores_background_image() -> None:
    output = render_vertical_stack(
        [_item()],
        canvas_size=CanvasSize(160, 240),
        background_image=Image.new("RGB", (20, 20), (255, 0, 0)),
        settings=RenderSettings(background_mode="solid", background_color="#112233"),
    )

    assert output.mode == "RGB"
    assert output.size == (160, 240)
    assert output.getpixel((5, 5)) == (17, 34, 51)


def test_background_image_cover_contain_and_stretch_return_exact_rgb_size() -> None:
    background = _striped_background()

    cover = render_vertical_stack(
        [_item()],
        canvas_size=CanvasSize(120, 120),
        background_image=background,
        settings=RenderSettings(background_mode="image", background_fit="cover", corner_radius=0),
    )
    contain = render_vertical_stack(
        [_item()],
        canvas_size=CanvasSize(120, 120),
        background_image=background,
        settings=RenderSettings(background_mode="image", background_fit="contain", background_color="#101010", corner_radius=0),
    )
    stretch = render_vertical_stack(
        [_item()],
        canvas_size=CanvasSize(120, 120),
        background_image=background,
        settings=RenderSettings(background_mode="image", background_fit="stretch", corner_radius=0),
    )

    assert cover.size == contain.size == stretch.size == (120, 120)
    assert cover.mode == contain.mode == stretch.mode == "RGB"
    assert cover.getpixel((60, 5))[1] > 180
    assert contain.getpixel((60, 5)) == (16, 16, 16)
    assert stretch.getpixel((20, 5))[0] > 180


def test_background_opacity_is_clamped_and_blended_over_solid_color() -> None:
    background = Image.new("RGB", (20, 20), (255, 255, 255))

    transparent = render_vertical_stack(
        [_item()],
        canvas_size=CanvasSize(120, 120),
        background_image=background,
        settings=RenderSettings(background_mode="image", background_color="#000000", background_opacity=-1),
    )
    half = render_vertical_stack(
        [_item()],
        canvas_size=CanvasSize(120, 120),
        background_image=background,
        settings=RenderSettings(background_mode="image", background_color="#000000", background_opacity=0.5),
    )
    opaque = render_vertical_stack(
        [_item()],
        canvas_size=CanvasSize(120, 120),
        background_image=background,
        settings=RenderSettings(background_mode="image", background_color="#000000", background_opacity=2),
    )

    assert transparent.getpixel((5, 5)) == (0, 0, 0)
    assert 120 <= half.getpixel((5, 5))[0] <= 136
    assert opaque.getpixel((5, 5)) == (255, 255, 255)


def test_background_overlay_is_applied_after_image() -> None:
    background = Image.new("RGB", (20, 20), (200, 200, 200))

    no_overlay = render_vertical_stack(
        [_item()],
        canvas_size=CanvasSize(120, 120),
        background_image=background,
        settings=RenderSettings(background_mode="image_with_overlay", background_color="#000000", overlay_opacity=0),
    )
    half_overlay = render_vertical_stack(
        [_item()],
        canvas_size=CanvasSize(120, 120),
        background_image=background,
        settings=RenderSettings(background_mode="image_with_overlay", background_color="#000000", overlay_opacity=0.5),
    )
    full_overlay = render_vertical_stack(
        [_item()],
        canvas_size=CanvasSize(120, 120),
        background_image=background,
        settings=RenderSettings(background_mode="image_with_overlay", background_color="#000000", overlay_opacity=1),
    )

    assert no_overlay.getpixel((5, 5)) == (200, 200, 200)
    assert 95 <= half_overlay.getpixel((5, 5))[0] <= 105
    assert full_overlay.getpixel((5, 5)) == (0, 0, 0)


def test_image_background_mode_without_image_warns_and_uses_solid_color() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        output = render_vertical_stack(
            [_item()],
            canvas_size=CanvasSize(120, 120),
            settings=RenderSettings(background_mode="image", background_color="#123456"),
        )

    assert output.getpixel((5, 5)) == (18, 52, 86)
    assert any("No se proporcionó una imagen de fondo" in str(item.message) for item in caught)


def test_background_size_preset_uses_background_or_fallback() -> None:
    background = Image.new("RGB", (77, 55), (10, 20, 30))
    with_background = render_vertical_stack(
        [_item()],
        canvas_size=None,
        background_image=background,
        settings=RenderSettings(canvas_preset="Background size", background_mode="image"),
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fallback = render_vertical_stack(
            [_item()],
            canvas_size=None,
            settings=RenderSettings(canvas_preset="Background size", background_mode="solid"),
        )

    assert with_background.size == (77, 55)
    assert fallback.size == (1080, 1920)
    assert any("Background size preset selected" in str(item.message) for item in caught)
