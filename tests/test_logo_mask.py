from __future__ import annotations

from PIL import Image

from hlt_slide.config import CanvasSize, Rect
from hlt_slide.logo_utils import compose_logo, prepare_logo
from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack


def _logo_rgb(size: tuple[int, int] = (100, 50), color: tuple[int, int, int] = (255, 0, 0)) -> Image.Image:
    return Image.new("RGB", size, color)


def _logo_rgba() -> Image.Image:
    image = Image.new("RGBA", (100, 50), (255, 0, 0, 0))
    for x in range(25, 75):
        for y in range(10, 40):
            image.putpixel((x, y), (255, 0, 0, 255))
    return image


def test_logo_rgb_without_mask_is_opaque_and_centered() -> None:
    prepared = prepare_logo(
        _logo_rgb(),
        canvas_size=CanvasSize(400, 300),
        footer_rect=Rect(0, 200, 400, 80),
        logo_width_percent=25,
        logo_max_height_percent=30,
    )

    assert prepared is not None
    assert prepared.rect.width == 100
    assert prepared.rect.height == 50
    assert prepared.rect.x == 150
    assert prepared.rect.y == 215
    assert prepared.image.getchannel("A").getextrema() == (255, 255)


def test_logo_rgba_internal_alpha_is_preserved_and_output_rgb() -> None:
    output = render_vertical_stack(
        [SlideItem(Image.new("RGB", (40, 40), (10, 10, 10)))],
        canvas_size=CanvasSize(320, 480),
        logo_image=_logo_rgba(),
        settings=RenderSettings(background_color="#000000", logo_width_percent=40, logo_max_height_percent=20),
    )

    assert output.mode == "RGB"
    assert _has_red_pixel(output)
    assert output.getpixel((10, 455)) == (0, 0, 0)


def test_logo_mask_direct_and_inverted_control_alpha() -> None:
    logo = _logo_rgb()
    white_mask = Image.new("L", (100, 50), 255)
    black_mask = Image.new("L", (100, 50), 0)
    footer = Rect(0, 200, 400, 80)

    direct_white = prepare_logo(logo, canvas_size=CanvasSize(400, 300), footer_rect=footer, logo_mask=white_mask, invert_logo_mask=False)
    inverted_white = prepare_logo(logo, canvas_size=CanvasSize(400, 300), footer_rect=footer, logo_mask=white_mask, invert_logo_mask=True)
    inverted_black = prepare_logo(logo, canvas_size=CanvasSize(400, 300), footer_rect=footer, logo_mask=black_mask, invert_logo_mask=True)

    assert direct_white is not None
    assert inverted_white is not None
    assert inverted_black is not None
    assert direct_white.image.getchannel("A").getextrema() == (255, 255)
    assert inverted_white.image.getchannel("A").getextrema() == (0, 0)
    assert inverted_black.image.getchannel("A").getextrema() == (255, 255)


def test_logo_mask_is_resized_and_multiplied_with_internal_alpha() -> None:
    prepared = prepare_logo(
        _logo_rgba(),
        canvas_size=CanvasSize(400, 300),
        footer_rect=Rect(0, 200, 400, 80),
        logo_mask=Image.new("L", (10, 5), 128),
        invert_logo_mask=False,
    )

    assert prepared is not None
    alpha_extrema = prepared.image.getchannel("A").getextrema()
    assert alpha_extrema[0] == 0
    assert 120 <= alpha_extrema[1] <= 130


def test_logo_opacity_and_safe_percent_limits() -> None:
    transparent = prepare_logo(
        _logo_rgb(),
        canvas_size=CanvasSize(400, 300),
        footer_rect=Rect(0, 200, 400, 80),
        logo_opacity=0,
    )
    half = prepare_logo(
        _logo_rgb(),
        canvas_size=CanvasSize(400, 300),
        footer_rect=Rect(0, 200, 400, 80),
        logo_opacity=0.5,
    )
    scaled = prepare_logo(
        _logo_rgb((400, 100)),
        canvas_size=CanvasSize(400, 300),
        footer_rect=Rect(0, 200, 400, 80),
        logo_width_percent=1000,
        logo_max_height_percent=10,
    )

    assert transparent is not None
    assert half is not None
    assert scaled is not None
    assert transparent.image.getchannel("A").getextrema() == (0, 0)
    assert 120 <= half.image.getchannel("A").getextrema()[1] <= 130
    assert scaled.rect.height <= 30
    assert scaled.rect.width <= 320


def test_logo_bottom_offset_stays_inside_canvas() -> None:
    prepared = prepare_logo(
        _logo_rgb(),
        canvas_size=CanvasSize(400, 300),
        footer_rect=Rect(0, 220, 400, 70),
        logo_bottom_offset=999,
    )

    assert prepared is not None
    assert prepared.rect.bottom <= 300


def test_compose_logo_preserves_background_where_alpha_is_zero() -> None:
    canvas = Image.new("RGB", (400, 300), (0, 0, 0))
    result = compose_logo(
        canvas,
        _logo_rgba(),
        footer_rect=Rect(0, 200, 400, 80),
        canvas_size=CanvasSize(400, 300),
        logo_width_percent=25,
        logo_max_height_percent=30,
    )

    assert result.mode == "RGB"
    assert _has_red_pixel(result)
    assert result.getpixel((200, 205)) == (0, 0, 0)


def test_renderer_auto_reserves_footer_for_logo_and_respects_manual_footer() -> None:
    auto = render_vertical_stack(
        [SlideItem(Image.new("RGB", (40, 40), (40, 40, 40)))],
        canvas_size=CanvasSize(320, 480),
        logo_image=_logo_rgb(),
        settings=RenderSettings(logo_width_percent=30, logo_max_height_percent=12),
    )
    manual = render_vertical_stack(
        [SlideItem(Image.new("RGB", (40, 40), (40, 40, 40)))],
        canvas_size=CanvasSize(320, 480),
        logo_image=_logo_rgb(),
        settings=RenderSettings(reserve_footer=True, footer_height=120, logo_width_percent=30, logo_max_height_percent=12),
    )

    assert _has_red_pixel(auto)
    assert _has_red_pixel(manual)
    assert auto.mode == manual.mode == "RGB"


def test_logo_absent_does_not_change_previous_footer_behavior() -> None:
    output = render_vertical_stack(
        [SlideItem(Image.new("RGB", (40, 40), (40, 200, 50)), label="")],
        canvas_size=CanvasSize(320, 480),
        settings=RenderSettings(reserve_footer=False),
    )

    assert not _has_red_pixel(output)


def _has_red_pixel(image: Image.Image) -> bool:
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue = image.getpixel((x, y))
            if red > 180 and green < 80 and blue < 80:
                return True
    return False
