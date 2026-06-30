from __future__ import annotations

from PIL import Image

from hlt_slide.config import CanvasSize
from hlt_slide.text_renderer import TextRenderSettings, measure_text_composition, render_text_composition


def test_auto_text_renders_all_effective_layouts() -> None:
    expected = {
        1: "centered_statement",
        2: "split_2",
        3: "vertical_stack",
        4: "grid_2x2",
    }
    for count, effective_layout in expected.items():
        texts = tuple(f"Texto {index}" for index in range(1, count + 1))
        plan = measure_text_composition(texts, canvas_size=CanvasSize(540, 960))
        image = render_text_composition(texts, canvas_size=CanvasSize(540, 960))

        assert plan.geometry.effective_layout == effective_layout
        assert image.mode == "RGB"
        assert image.size == (540, 960)
        assert all(block.inner_rect.width > 0 and block.inner_rect.height > 0 for block in plan.fitted_blocks)


def test_background_modes_produce_distinct_robust_outputs() -> None:
    background = Image.new("RGB", (80, 160), (0, 80, 180))
    solid = render_text_composition(
        ("SOLID",),
        canvas_size=CanvasSize(240, 320),
        settings=TextRenderSettings(background_mode="solid", background_color="#101010"),
    )
    image = render_text_composition(
        ("IMAGE",),
        canvas_size=CanvasSize(240, 320),
        background_image=background,
        settings=TextRenderSettings(background_mode="image", background_fit="stretch"),
    )
    overlay = render_text_composition(
        ("OVERLAY",),
        canvas_size=CanvasSize(240, 320),
        background_image=background,
        settings=TextRenderSettings(
            background_mode="image_with_overlay",
            background_color="#000000",
            background_fit="contain",
            overlay_opacity=0.5,
        ),
    )

    assert solid.getpixel((0, 0)) == (16, 16, 16)
    assert image.getpixel((0, 0)) != solid.getpixel((0, 0))
    assert overlay.getpixel((0, 0)) != image.getpixel((0, 0))


def test_clipping_keeps_visible_text_inside_inner_rect_bounds() -> None:
    plan = measure_text_composition(
        ("PALABRA MUY LARGA " * 20,),
        canvas_size=CanvasSize(300, 300),
        settings=TextRenderSettings(clipping=True, font_scale=2.0, warn_on_truncation=False),
    )
    image = render_text_composition(
        ("PALABRA MUY LARGA " * 20,),
        canvas_size=CanvasSize(300, 300),
        settings=TextRenderSettings(clipping=True, font_scale=2.0, warn_on_truncation=False),
    )
    inner = plan.fitted_blocks[0].inner_rect
    text_pixels = []
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue = image.getpixel((x, y))
            if red > 180 and green > 170 and blue > 150:
                text_pixels.append((x, y))

    assert text_pixels
    assert min(x for x, _y in text_pixels) >= inner.x
    assert max(x for x, _y in text_pixels) <= inner.right - 1
    assert min(y for _x, y in text_pixels) >= inner.y
    assert max(y for _x, y in text_pixels) <= inner.bottom - 1
