from __future__ import annotations

from PIL import Image, ImageDraw

import hlt_slide.renderer as renderer_module
from hlt_slide.adaptive_mosaic import AdaptiveMosaicSettings
from hlt_slide.config import CanvasSize
from hlt_slide.renderer import RenderSettings, SlideItem, render_adaptive_mosaic


def synthetic_image(size: tuple[int, int], color: tuple[int, int, int], label: str) -> Image.Image:
    image = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((3, 3, size[0] - 4, size[1] - 4), outline=(255, 255, 255), width=3)
    draw.line((0, 0, size[0] - 1, size[1] - 1), fill=(0, 0, 0), width=3)
    draw.line((0, size[1] - 1, size[0] - 1, 0), fill=(0, 0, 0), width=3)
    draw.text((8, 8), label, fill=(255, 255, 255))
    return image


def logo() -> Image.Image:
    image = Image.new("RGBA", (120, 60), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((10, 10, 110, 50), radius=12, fill=(233, 33, 36, 255))
    return image


def background(size: tuple[int, int]) -> Image.Image:
    image = Image.new("RGB", size, (40, 40, 60))
    draw = ImageDraw.Draw(image)
    for x in range(0, size[0], 24):
        draw.line((x, 0, size[0] - x, size[1]), fill=(90, 90, 120), width=2)
    return image


def mixed_items() -> tuple[SlideItem, ...]:
    return (
        SlideItem(synthetic_image((400, 400), (220, 70, 70), "1:1"), "SQUARE"),
        SlideItem(synthetic_image((640, 360), (70, 180, 80), "16:9"), "LANDSCAPE"),
        SlideItem(synthetic_image((360, 480), (80, 110, 230), "3:4"), "PORTRAIT"),
        SlideItem(synthetic_image((360, 640), (230, 170, 60), "9:16"), "TALL"),
    )


def test_render_adaptive_mosaic_returns_exact_rgb_canvas_for_1_to_4_items() -> None:
    for count in range(1, 5):
        output = render_adaptive_mosaic(
            mixed_items()[:count],
            title="ADAPTIVE",
            canvas_size=CanvasSize(360, 640),
            settings=RenderSettings(corner_radius=0, border_width=0),
        )

        assert output.size == (360, 640)
        assert output.mode == "RGB"


def test_render_adaptive_mosaic_supports_background_overlay_logo_mask_borders_and_corners() -> None:
    mask = Image.new("L", (120, 60), 0)
    ImageDraw.Draw(mask).rectangle((20, 15, 100, 45), fill=255)

    output = render_adaptive_mosaic(
        mixed_items(),
        title="BACKGROUND LOGO",
        canvas_size=CanvasSize(420, 720),
        background_image=background((420, 720)),
        logo_image=logo(),
        logo_mask=mask,
        settings=RenderSettings(
            background_mode="image_with_overlay",
            background_color="#000000",
            overlay_opacity=0.35,
            reserve_footer=True,
            footer_height=90,
            border_width=3,
            corner_radius=14,
            debug_layout=True,
        ),
        adaptive_settings=AdaptiveMosaicSettings(strategy="balanced"),
    )

    assert output.mode == "RGB"
    assert output.size == (420, 720)
    assert _has_pixel_matching(output, lambda pixel: pixel[0] > 180 and pixel[1] < 80)
    assert _has_pixel_matching(output, lambda pixel: pixel[2] > 120)


def test_adaptive_renderer_forces_contain_transparent_even_when_global_fit_is_cover() -> None:
    output = render_adaptive_mosaic(
        [SlideItem(synthetic_image((640, 360), (0, 255, 0), "16:9"), "")],
        canvas_size=CanvasSize(320, 480),
        settings=RenderSettings(
            background_color="#AA0000",
            image_fit="cover",
            contain_fill_mode="cell_color",
            corner_radius=0,
            border_width=0,
        ),
    )

    assert output.getpixel((160, 120)) == (170, 0, 0)
    assert _has_pixel_matching(output, lambda pixel: pixel[1] > 200 and pixel[0] < 20)


def test_adaptive_renderer_accepts_all_internal_strategies() -> None:
    outputs = [
        render_adaptive_mosaic(
            mixed_items(),
            canvas_size=CanvasSize(420, 720),
            settings=RenderSettings(corner_radius=0),
            adaptive_settings=AdaptiveMosaicSettings(strategy=strategy),
        )
        for strategy in ("balanced", "editorial", "compact")
    ]

    assert all(output.mode == "RGB" for output in outputs)
    assert all(output.size == (420, 720) for output in outputs)


def test_adaptive_minimum_image_size_uses_explicit_resolved_canvas(monkeypatch) -> None:
    captured = _capture_mosaic_settings(monkeypatch)

    output = render_adaptive_mosaic(
        mixed_items()[:1],
        canvas_size=CanvasSize(320, 480),
        settings=RenderSettings(corner_radius=0, border_width=0),
    )

    assert output.size == (320, 480)
    assert captured[-1].minimum_image_width == 26
    assert captured[-1].minimum_image_height == 24


def test_adaptive_minimum_image_size_uses_large_preset_not_custom_fields(monkeypatch) -> None:
    captured = _capture_mosaic_settings(monkeypatch)

    output = render_adaptive_mosaic(
        mixed_items()[:1],
        canvas_size=None,
        settings=RenderSettings(
            canvas_preset="9:16 4K · 2160x3840",
            corner_radius=0,
            border_width=0,
        ),
    )

    assert output.size == (2160, 3840)
    assert captured[-1].minimum_image_width == 173
    assert captured[-1].minimum_image_height == 192


def test_adaptive_minimum_image_size_uses_background_size_canvas(monkeypatch) -> None:
    captured = _capture_mosaic_settings(monkeypatch)

    output = render_adaptive_mosaic(
        mixed_items()[:1],
        canvas_size=None,
        background_image=background((777, 555)),
        settings=RenderSettings(
            canvas_preset="Background size",
            background_mode="image",
            corner_radius=0,
            border_width=0,
        ),
    )

    assert output.size == (777, 555)
    assert captured[-1].minimum_image_width == 62
    assert captured[-1].minimum_image_height == 28


def _capture_mosaic_settings(monkeypatch):
    captured = []
    original = renderer_module.select_adaptive_mosaic

    def wrapped_select_adaptive_mosaic(canvas_size, sources, settings, **kwargs):
        captured.append(settings)
        return original(canvas_size, sources, settings, **kwargs)

    monkeypatch.setattr(renderer_module, "select_adaptive_mosaic", wrapped_select_adaptive_mosaic)
    return captured


def _has_pixel_matching(image: Image.Image, predicate) -> bool:
    for y in range(image.height):
        for x in range(image.width):
            if predicate(image.getpixel((x, y))):
                return True
    return False
