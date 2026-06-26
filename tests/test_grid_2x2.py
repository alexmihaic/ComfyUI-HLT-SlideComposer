from __future__ import annotations

import warnings

import pytest
from PIL import Image

from hlt_slide.config import CanvasSize
from hlt_slide.exceptions import LayoutOverflowError
from hlt_slide.layouts import calculate_grid_2x2
from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack


def _item(color: tuple[int, int, int], label: str = "") -> SlideItem:
    return SlideItem(Image.new("RGB", (80, 60), color), label=label)


def _striped_vertical() -> Image.Image:
    image = Image.new("RGB", (80, 240), "black")
    pixels = image.load()
    for y in range(image.height):
        color = (255, 0, 0) if y < 80 else (0, 255, 0) if y < 160 else (0, 0, 255)
        for x in range(image.width):
            pixels[x, y] = color
    return image


def _rects(layout):
    rects = []
    if layout.title_rect is not None:
        rects.append(layout.title_rect)
    for block in layout.blocks:
        rects.append(block.image_rect)
        if block.label_rect is not None:
            rects.append(block.label_rect)
    if layout.footer_rect is not None:
        rects.append(layout.footer_rect)
    return rects


def _intersects(a, b) -> bool:
    return a.x < b.right and a.right > b.x and a.y < b.bottom and a.bottom > b.y


def test_grid_one_image_uses_single_full_width_cell() -> None:
    layout = calculate_grid_2x2(
        CanvasSize(1080, 1920),
        image_count=1,
        title_height=60,
        label_heights=(32,),
    )

    block = layout.blocks[0]
    assert len(layout.blocks) == 1
    assert block.image_rect.width == 1080 - (2 * 64)
    assert block.label_rect is not None
    assert block.label_rect.width == block.image_rect.width
    assert block.label_rect.y > block.image_rect.bottom


def test_grid_two_images_uses_equal_columns_with_aligned_labels() -> None:
    layout = calculate_grid_2x2(
        CanvasSize(1080, 1920),
        image_count=2,
        label_heights=(24, 48),
    )

    first, second = layout.blocks
    assert first.image_rect.y == second.image_rect.y
    assert first.image_rect.width == second.image_rect.width
    assert first.image_rect.height == second.image_rect.height
    assert first.label_rect is not None
    assert second.label_rect is not None
    assert first.label_rect.y == second.label_rect.y
    assert first.label_rect.height == second.label_rect.height == 48


def test_grid_three_images_uses_full_width_hero_then_two_columns() -> None:
    layout = calculate_grid_2x2(
        CanvasSize(1080, 1920),
        image_count=3,
        label_heights=(30, 30, 30),
    )

    top, left, right = layout.blocks
    assert top.image_rect.width == 1080 - (2 * 64)
    assert left.image_rect.y == right.image_rect.y
    assert left.image_rect.width == right.image_rect.width
    assert left.image_rect.height == right.image_rect.height
    assert left.image_rect.x < right.image_rect.x
    assert left.image_rect.y > top.label_rect.bottom


def test_grid_four_images_uses_regular_two_by_two_geometry() -> None:
    layout = calculate_grid_2x2(
        CanvasSize(1080, 1920),
        image_count=4,
        title_height=64,
        label_heights=(24, 40, 0, 40),
        reserve_footer=True,
        footer_height=96,
    )

    first, second, third, fourth = layout.blocks
    assert first.image_rect.x == third.image_rect.x
    assert second.image_rect.x == fourth.image_rect.x
    assert first.image_rect.y == second.image_rect.y
    assert third.image_rect.y == fourth.image_rect.y
    assert first.image_rect.width == second.image_rect.width == third.image_rect.width == fourth.image_rect.width
    assert first.image_rect.height == second.image_rect.height == third.image_rect.height == fourth.image_rect.height
    assert layout.footer_rect is not None
    assert layout.footer_rect.y > fourth.image_rect.bottom


def test_grid_rectangles_stay_inside_canvas_without_intersections_for_resolutions() -> None:
    for canvas in (
        CanvasSize(1080, 1920),
        CanvasSize(1152, 2048),
        CanvasSize(1080, 1350),
        CanvasSize(1536, 2048),
        CanvasSize(1080, 1080),
        CanvasSize(360, 420),
    ):
        layout = calculate_grid_2x2(
            canvas,
            image_count=4,
            title_height=40,
            label_heights=(22, 38, 0, 38),
            reserve_footer=True,
            footer_height=50,
        )
        rects = _rects(layout)

        for rect in rects:
            assert rect.x >= 0
            assert rect.y >= 0
            assert rect.right <= canvas.width
            assert rect.bottom <= canvas.height
            assert rect.width > 0
            assert rect.height > 0

        for index, rect in enumerate(rects):
            for other in rects[index + 1 :]:
                assert not _intersects(rect, other)


def test_grid_distribution_is_deterministic() -> None:
    first = calculate_grid_2x2(
        CanvasSize(1080, 1350),
        image_count=3,
        title_height=70,
        label_heights=(30, 60, 40),
    )
    second = calculate_grid_2x2(
        CanvasSize(1080, 1350),
        image_count=3,
        title_height=70,
        label_heights=(30, 60, 40),
    )

    assert first == second


def test_grid_overflow_reports_context() -> None:
    with pytest.raises(LayoutOverflowError, match="grid_2x2 overflow"):
        calculate_grid_2x2(
            CanvasSize(120, 120),
            image_count=4,
            title_height=70,
            label_heights=(40, 40, 40, 40),
            reserve_footer=True,
            footer_height=50,
        )


def test_grid_renderer_supports_background_logo_fit_and_order() -> None:
    background = Image.new("RGB", (120, 120), (60, 80, 120))
    logo = Image.new("RGBA", (80, 30), (233, 33, 36, 180))
    output = render_vertical_stack(
        [
            _item((255, 0, 0), "A"),
            _item((0, 255, 0), "B"),
            _item((0, 0, 255), "C"),
            _item((255, 255, 0), "D"),
        ],
        title="GRID",
        canvas_size=CanvasSize(420, 640),
        background_image=background,
        logo_image=logo,
        settings=RenderSettings(
            layout="grid_2x2",
            background_mode="image_with_overlay",
            background_color="#000000",
            overlay_opacity=0.25,
            image_fit="contain",
            crop_anchor="top",
            corner_radius=0,
            logo_width_percent=24,
        ),
    )

    assert output.mode == "RGB"
    assert output.size == (420, 640)
    assert _has_pixel(output, lambda p: p[0] > 180 and p[1] < 90)
    assert _has_pixel(output, lambda p: p[1] > 180 and p[0] < 90)
    assert _has_pixel(output, lambda p: p[2] > 180 and p[0] < 90)


def test_grid_renderer_contain_transparent_keeps_background_visible_in_bands() -> None:
    background = Image.new("RGB", (420, 640), (20, 40, 200))
    output = render_vertical_stack(
        [
            SlideItem(Image.new("RGB", (180, 40), (255, 0, 0))),
            SlideItem(Image.new("RGB", (180, 40), (0, 255, 0))),
            SlideItem(Image.new("RGB", (180, 40), (0, 0, 255))),
            SlideItem(Image.new("RGB", (180, 40), (255, 255, 0))),
        ],
        canvas_size=CanvasSize(420, 640),
        background_image=background,
        settings=RenderSettings(
            layout="grid_2x2",
            background_mode="image",
            image_fit="contain",
            contain_fill_mode="transparent",
            cell_background_color="#111111",
            corner_radius=0,
        ),
    )
    layout = calculate_grid_2x2(CanvasSize(420, 640), image_count=4)
    sample = (
        layout.blocks[0].image_rect.x + (layout.blocks[0].image_rect.width // 2),
        layout.blocks[0].image_rect.y + 4,
    )

    assert output.getpixel(sample) == (20, 40, 200)


def test_grid_renderer_supports_cover_crop_anchors() -> None:
    source = _striped_vertical()
    layout = calculate_grid_2x2(CanvasSize(320, 320), image_count=1)
    sample = (
        layout.blocks[0].image_rect.x + (layout.blocks[0].image_rect.width // 2),
        layout.blocks[0].image_rect.y + (layout.blocks[0].image_rect.height // 2),
    )
    top = render_vertical_stack(
        [SlideItem(source)],
        canvas_size=CanvasSize(320, 320),
        settings=RenderSettings(layout="grid_2x2", image_fit="cover", crop_anchor="top", corner_radius=0),
    )
    center = render_vertical_stack(
        [SlideItem(source)],
        canvas_size=CanvasSize(320, 320),
        settings=RenderSettings(layout="grid_2x2", image_fit="cover", crop_anchor="center", corner_radius=0),
    )
    bottom = render_vertical_stack(
        [SlideItem(source)],
        canvas_size=CanvasSize(320, 320),
        settings=RenderSettings(layout="grid_2x2", image_fit="cover", crop_anchor="bottom", corner_radius=0),
    )

    assert top.getpixel(sample)[0] > 180
    assert center.getpixel(sample)[1] > 180
    assert bottom.getpixel(sample)[2] > 180


def test_grid_renderer_supports_stretch_and_truncated_label_warning() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        output = render_vertical_stack(
            [SlideItem(Image.new("RGB", (20, 120), (90, 180, 40)), "Supercalifragilisticexpialidocious")],
            canvas_size=CanvasSize(260, 300),
            settings=RenderSettings(
                layout="grid_2x2",
                image_fit="stretch",
                label_font_size=22,
                minimum_font_size=22,
                max_label_lines=1,
                corner_radius=0,
            ),
        )

    assert output.mode == "RGB"
    assert _has_pixel(output, lambda p: p[1] > 150 and p[0] < 120)
    assert any("La etiqueta 1 ha sido truncada" in str(item.message) for item in caught)


def test_grid_renderer_debug_changes_output() -> None:
    items = [_item((255, 0, 0)), _item((0, 255, 0)), _item((0, 0, 255))]
    normal = render_vertical_stack(
        items,
        canvas_size=CanvasSize(360, 520),
        settings=RenderSettings(layout="grid_2x2", corner_radius=0, debug_layout=False),
    )
    debug = render_vertical_stack(
        items,
        canvas_size=CanvasSize(360, 520),
        settings=RenderSettings(layout="grid_2x2", corner_radius=0, debug_layout=True),
    )

    assert normal.tobytes() != debug.tobytes()
    assert _has_pixel(debug, lambda p: p[2] > 180 and p[0] < 90)


def _has_pixel(image: Image.Image, predicate) -> bool:
    for y in range(image.height):
        for x in range(image.width):
            if predicate(image.getpixel((x, y))):
                return True
    return False
