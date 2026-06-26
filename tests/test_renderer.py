from __future__ import annotations

import warnings

from PIL import Image, ImageDraw

from hlt_slide.config import CanvasSize
from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack


def _solid(color: tuple[int, int, int], size: tuple[int, int] = (120, 80)) -> Image.Image:
    return Image.new("RGB", size, color)


def _striped_vertical() -> Image.Image:
    image = Image.new("RGB", (80, 240), "black")
    pixels = image.load()
    for y in range(240):
        color = (255, 0, 0) if y < 80 else (0, 255, 0) if y < 160 else (0, 0, 255)
        for x in range(80):
            pixels[x, y] = color
    return image


def _two_tone_background(size: tuple[int, int] = (320, 480)) -> Image.Image:
    image = Image.new("RGB", size, (255, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((size[0] // 2, 0, size[0], size[1]), fill=(0, 0, 255))
    return image


def _red_pixels(image: Image.Image) -> list[tuple[int, int]]:
    return [
        (x, y)
        for y in range(image.height)
        for x in range(image.width)
        if image.getpixel((x, y))[0] > 180 and image.getpixel((x, y))[1] < 90
    ]


def test_renderer_returns_exact_rgb_canvas_with_default_background() -> None:
    output = render_vertical_stack(
        [SlideItem(_solid((20, 120, 200)))],
        title="",
        canvas_size=CanvasSize(320, 480),
    )

    assert output.size == (320, 480)
    assert output.mode == "RGB"
    assert output.getpixel((5, 5)) == (0, 0, 0)


def test_renderer_preserves_item_order_without_empty_label_gaps() -> None:
    output = render_vertical_stack(
        [
            SlideItem(_solid((255, 0, 0)), label=""),
            SlideItem(_solid((0, 255, 0)), label="B"),
            SlideItem(_solid((0, 0, 255)), label=""),
        ],
        canvas_size=CanvasSize(360, 720),
        settings=RenderSettings(image_fit="stretch", corner_radius=0),
    )

    assert output.getpixel((180, 120)) == (255, 0, 0)
    assert output.getpixel((180, 350))[1] > 180
    assert output.getpixel((180, 600))[2] > 180


def test_renderer_draws_default_hlt_red_title_and_label() -> None:
    output = render_vertical_stack(
        [SlideItem(_solid((20, 120, 200)), label="REF")],
        title="TITLE",
        canvas_size=CanvasSize(420, 640),
    )

    assert _red_pixels(output)


def test_renderer_supports_contain_and_border() -> None:
    output = render_vertical_stack(
        [SlideItem(_solid((40, 180, 80), (240, 80)), label="")],
        canvas_size=CanvasSize(320, 480),
        settings=RenderSettings(
            image_fit="contain",
            contain_fill_mode="cell_color",
            cell_background_color="#111111",
            border_width=4,
            border_color="#E92124",
            corner_radius=0,
        ),
    )

    assert output.getpixel((160, 110)) == (17, 17, 17)
    assert _has_pixel_matching(output, lambda pixel: pixel[0] > 200 and pixel[1] < 80)


def test_renderer_contain_transparent_keeps_solid_background_visible() -> None:
    output = render_vertical_stack(
        [SlideItem(_solid((40, 180, 80), (240, 80)), label="")],
        canvas_size=CanvasSize(320, 480),
        settings=RenderSettings(
            background_color="#AA0000",
            image_fit="contain",
            contain_fill_mode="transparent",
            cell_background_color="#111111",
            border_width=0,
            corner_radius=0,
        ),
    )

    assert output.mode == "RGB"
    assert output.getpixel((160, 110)) == (170, 0, 0)


def test_renderer_contain_cell_color_uses_cell_background_color() -> None:
    output = render_vertical_stack(
        [SlideItem(_solid((40, 180, 80), (240, 80)), label="")],
        canvas_size=CanvasSize(320, 480),
        settings=RenderSettings(
            background_color="#AA0000",
            image_fit="contain",
            contain_fill_mode="cell_color",
            cell_background_color="#111111",
            border_width=0,
            corner_radius=0,
        ),
    )

    assert output.getpixel((160, 110)) == (17, 17, 17)


def test_renderer_contain_transparent_keeps_image_background_and_overlay_visible() -> None:
    background = _two_tone_background((320, 480))
    output = render_vertical_stack(
        [SlideItem(_solid((40, 180, 80), (240, 80)), label="")],
        canvas_size=CanvasSize(320, 480),
        background_image=background,
        settings=RenderSettings(
            background_mode="image_with_overlay",
            background_color="#000000",
            overlay_opacity=0.5,
            image_fit="contain",
            contain_fill_mode="transparent",
            cell_background_color="#111111",
            border_width=0,
            corner_radius=0,
        ),
    )

    assert output.getpixel((160, 110)) == (0, 0, 127)


def test_renderer_contain_transparent_supports_corner_radius_border_logo_and_grid() -> None:
    logo = Image.new("RGBA", (60, 30), (255, 0, 0, 160))
    output = render_vertical_stack(
        [
            SlideItem(_solid((255, 0, 0), (120, 40))),
            SlideItem(_solid((0, 255, 0), (120, 40))),
            SlideItem(_solid((0, 0, 255), (120, 40))),
            SlideItem(_solid((255, 255, 0), (120, 40))),
        ],
        canvas_size=CanvasSize(420, 640),
        background_image=_two_tone_background((420, 640)),
        logo_image=logo,
        settings=RenderSettings(
            layout="grid_2x2",
            background_mode="image",
            image_fit="contain",
            contain_fill_mode="transparent",
            cell_background_color="#111111",
            corner_radius=12,
            border_width=3,
            border_color="#E92124",
        ),
    )

    assert output.mode == "RGB"
    assert _has_pixel_matching(output, lambda pixel: pixel[0] > 200 and pixel[1] < 80)
    assert _has_pixel_matching(output, lambda pixel: pixel[2] > 120 and pixel[0] < 80)


def test_renderer_cover_crop_anchor_changes_visible_region() -> None:
    top = render_vertical_stack(
        [SlideItem(_striped_vertical(), label="")],
        canvas_size=CanvasSize(320, 320),
        settings=RenderSettings(image_fit="cover", crop_anchor="top", corner_radius=0),
    )
    bottom = render_vertical_stack(
        [SlideItem(_striped_vertical(), label="")],
        canvas_size=CanvasSize(320, 320),
        settings=RenderSettings(image_fit="cover", crop_anchor="bottom", corner_radius=0),
    )

    assert top.getpixel((160, 160))[0] > 180
    assert bottom.getpixel((160, 160))[2] > 180


def test_renderer_debug_layout_can_be_enabled_or_disabled() -> None:
    normal = render_vertical_stack(
        [SlideItem(_solid((40, 180, 80)), label="A")],
        title="T",
        canvas_size=CanvasSize(320, 480),
        settings=RenderSettings(debug_layout=False),
    )
    debug = render_vertical_stack(
        [SlideItem(_solid((40, 180, 80)), label="A")],
        title="T",
        canvas_size=CanvasSize(320, 480),
        settings=RenderSettings(debug_layout=True),
    )

    assert normal.tobytes() != debug.tobytes()
    assert _has_pixel_matching(debug, lambda pixel: pixel[2] > 180 and pixel[0] < 80)


def test_renderer_reserves_footer_without_drawing_logo() -> None:
    output = render_vertical_stack(
        [SlideItem(_solid((200, 100, 50)), label="")],
        canvas_size=CanvasSize(320, 480),
        settings=RenderSettings(reserve_footer=True, footer_height=80),
    )

    assert output.getpixel((160, 455)) == (0, 0, 0)


def test_renderer_warns_when_label_is_truncated() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        render_vertical_stack(
            [SlideItem(_solid((80, 80, 200)), label="Supercalifragilisticexpialidocious")],
            canvas_size=CanvasSize(260, 320),
            settings=RenderSettings(label_font_size=22, minimum_font_size=22, max_label_lines=1),
        )

    assert any("[HLT Slide Composer] La etiqueta 1 ha sido truncada." in str(item.message) for item in caught)


def test_renderer_combines_background_overlay_logo_title_and_three_images() -> None:
    background = Image.new("RGB", (80, 120), (120, 120, 120))
    logo = Image.new("RGBA", (100, 50), (255, 0, 0, 0))
    for x in range(20, 80):
        for y in range(10, 40):
            logo.putpixel((x, y), (255, 0, 0, 255))

    output = render_vertical_stack(
        [
            SlideItem(_solid((255, 0, 0)), "REF0"),
            SlideItem(_solid((0, 255, 0)), "REF1"),
            SlideItem(_solid((0, 0, 255)), "RESULT"),
        ],
        title="COMPLETA",
        canvas_size=CanvasSize(420, 720),
        background_image=background,
        logo_image=logo,
        settings=RenderSettings(
            background_mode="image_with_overlay",
            background_color="#000000",
            overlay_opacity=0.5,
            logo_width_percent=24,
            logo_max_height_percent=8,
            corner_radius=0,
        ),
    )

    assert output.mode == "RGB"
    assert output.size == (420, 720)
    assert output.getpixel((5, 5))[0] < 80
    assert _has_pixel_matching(output, lambda pixel: pixel[0] > 180 and pixel[1] < 80)
    assert _has_pixel_matching(output, lambda pixel: pixel[1] > 180 and pixel[0] < 80)
    assert _has_pixel_matching(output, lambda pixel: pixel[2] > 180 and pixel[0] < 80)


def _has_pixel_matching(image: Image.Image, predicate) -> bool:
    for y in range(image.height):
        for x in range(image.width):
            if predicate(image.getpixel((x, y))):
                return True
    return False
