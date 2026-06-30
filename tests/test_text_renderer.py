from __future__ import annotations

import importlib
import warnings

import pytest
from PIL import Image, ImageDraw

from hlt_slide.config import CanvasSize
from hlt_slide.text_renderer import (
    BASE_ROLE_STYLES,
    TEXT_COMPOSER_WARNING_PREFIX,
    TextRenderSettings,
    measure_text_composition,
    render_text_composition,
    scaled_role_style,
)


def _logo() -> Image.Image:
    image = Image.new("RGBA", (160, 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 152, 72), radius=18, fill=(233, 33, 36, 255))
    draw.rectangle((58, 20, 102, 60), fill=(255, 255, 255, 255))
    return image


def _background() -> Image.Image:
    image = Image.new("RGB", (200, 100), (20, 80, 140))
    draw = ImageDraw.Draw(image)
    draw.rectangle((100, 0, 199, 99), fill=(180, 60, 20))
    return image


def test_role_style_table_is_complete_immutable_and_scaled() -> None:
    assert set(BASE_ROLE_STYLES) == {
        "number",
        "headline",
        "quote",
        "subheadline",
        "body",
        "label",
        "caption",
    }
    assert BASE_ROLE_STYLES["number"].preferred_font_size == 184
    assert BASE_ROLE_STYLES["headline"].minimum_font_size == 34
    assert BASE_ROLE_STYLES["quote"].max_lines == 7
    assert BASE_ROLE_STYLES["caption"].line_spacing == 5
    with pytest.raises(TypeError):
        BASE_ROLE_STYLES["headline"] = BASE_ROLE_STYLES["body"]  # type: ignore[index]

    scaled = scaled_role_style("headline", CanvasSize(2160, 3840), font_scale=0.5)
    assert scaled.preferred_font_size == 112
    assert scaled.minimum_font_size == 34
    assert scaled.line_spacing == 8


def test_font_scale_validation() -> None:
    with pytest.raises(ValueError, match="font_scale"):
        TextRenderSettings(font_scale=0.1)
    with pytest.raises(ValueError, match="font_scale"):
        TextRenderSettings(font_scale=4.5)


@pytest.mark.parametrize("role", ["headline", "subheadline", "body", "quote", "number", "label", "caption"])
def test_measure_fits_each_role_and_preserves_original_text(role: str) -> None:
    plan = measure_text_composition(
        ("Árbol\nmanual line",),
        roles=(role,),
        canvas_size=CanvasSize(1080, 1920),
        settings=TextRenderSettings(layout="centered_statement", uppercase=True),
    )

    block = plan.fitted_blocks[0]
    assert block.role == role
    assert block.original_text == "Árbol\nmanual line"
    assert "ÁRBOL" in block.rendered_text
    assert block.line_count >= 1
    assert block.font_size >= BASE_ROLE_STYLES[role].minimum_font_size
    assert block.rect == plan.geometry.blocks[0].rect
    assert block.inner_rect == plan.geometry.blocks[0].inner_rect


def test_long_text_truncates_and_warns_with_original_source_index() -> None:
    text = " ".join(["extraordinariamente"] * 80)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        plan = measure_text_composition(
            ("", text),
            roles=("headline", "caption"),
            canvas_size=CanvasSize(360, 640),
            settings=TextRenderSettings(layout="centered_statement", warn_on_truncation=True),
        )

    assert plan.fitted_blocks[0].source_index == 1
    assert plan.fitted_blocks[0].was_truncated is True
    assert any(f"{TEXT_COMPOSER_WARNING_PREFIX} text_2 was truncated." in str(item.message) for item in caught)


def test_alignment_auto_rules_and_global_overrides() -> None:
    centered = measure_text_composition(("A",), canvas_size=CanvasSize(1080, 1920))
    stack = measure_text_composition(("A", "B", "C"), canvas_size=CanvasSize(1080, 1920))
    quote = measure_text_composition(
        ("Quote", "Author"),
        roles=("quote", "caption"),
        canvas_size=CanvasSize(1080, 1920),
        settings=TextRenderSettings(layout="editorial_quote"),
    )
    override = measure_text_composition(
        ("A", "B"),
        canvas_size=CanvasSize(1080, 1920),
        settings=TextRenderSettings(layout="split_2", horizontal_align="right", vertical_align="top"),
    )

    assert centered.fitted_blocks[0].alignment == "center"
    assert centered.fitted_blocks[0].vertical_alignment == "center"
    assert {block.alignment for block in stack.fitted_blocks} == {"left"}
    assert quote.fitted_blocks[0].alignment == "left"
    assert quote.fitted_blocks[1].alignment == "right"
    assert quote.fitted_blocks[1].vertical_alignment == "bottom"
    assert {block.alignment for block in override.fitted_blocks} == {"right"}
    assert {block.vertical_alignment for block in override.fitted_blocks} == {"top"}


def test_editorial_quote_alignment_uses_active_position_not_original_slot() -> None:
    quote = measure_text_composition(
        ("", "Quote", "Author"),
        roles=("headline", "quote", "caption"),
        canvas_size=CanvasSize(1080, 1920),
        settings=TextRenderSettings(layout="editorial_quote"),
    )

    assert quote.fitted_blocks[0].source_index == 1
    assert quote.fitted_blocks[0].alignment == "left"
    assert quote.fitted_blocks[0].vertical_alignment == "center"
    assert quote.fitted_blocks[1].source_index == 2
    assert quote.fitted_blocks[1].alignment == "right"
    assert quote.fitted_blocks[1].vertical_alignment == "bottom"


def test_accent_targets_use_original_slots_and_do_not_reassign_empty_slot() -> None:
    first = measure_text_composition(
        ("A", "", "C"),
        roles=("headline", "body", "caption"),
        canvas_size=CanvasSize(1080, 1920),
        settings=TextRenderSettings(accent_target="first_active"),
    )
    text_3 = measure_text_composition(
        ("A", "", "C"),
        roles=("headline", "body", "caption"),
        canvas_size=CanvasSize(1080, 1920),
        settings=TextRenderSettings(accent_target="text_3"),
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        empty = measure_text_composition(
            ("A", "", "C"),
            roles=("headline", "body", "caption"),
            canvas_size=CanvasSize(1080, 1920),
            settings=TextRenderSettings(accent_target="text_2"),
        )

    assert first.fitted_blocks[0].color[:3] == (233, 33, 36)
    assert first.fitted_blocks[1].color[:3] != (233, 33, 36)
    assert text_3.fitted_blocks[1].source_index == 2
    assert text_3.fitted_blocks[1].color[:3] == (233, 33, 36)
    assert all(block.color[:3] != (233, 33, 36) for block in empty.fitted_blocks)
    assert any("accent_target='text_2' selected an empty text slot" in str(item.message) for item in caught)


def test_render_outputs_rgb_exact_size_background_overlay_logo_and_debug() -> None:
    image = render_text_composition(
        ("FONDO", "LOGO"),
        roles=("headline", "caption"),
        canvas_size=CanvasSize(320, 480),
        background_image=_background(),
        logo_image=_logo(),
        settings=TextRenderSettings(
            layout="split_2",
            background_mode="image_with_overlay",
            background_color="#000000",
            overlay_opacity=0.35,
            logo_width_percent=24.0,
            reserve_logo_space=True,
            debug_layout=True,
        ),
    )

    assert image.mode == "RGB"
    assert image.size == (320, 480)
    assert _count_red_pixels(image) > 0
    assert _count_bright_pixels(image) > 0


def test_render_is_deterministic_and_slide_composer_contract_unchanged() -> None:
    kwargs = {
        "texts": ("UNO", "DOS", "TRES", "CUATRO"),
        "roles": ("number", "headline", "label", "caption"),
        "canvas_size": CanvasSize(320, 480),
        "settings": TextRenderSettings(layout="auto_text", accent_target="text_1"),
    }
    first = render_text_composition(**kwargs)
    second = render_text_composition(**kwargs)
    node_module = importlib.import_module("nodes")

    assert first.tobytes() == second.tobytes()
    assert node_module.NODE_CLASS_MAPPINGS == {"HLTSlideComposer": node_module.HLTSlideComposer}
    assert node_module.NODE_DISPLAY_NAME_MAPPINGS == {
        "HLTSlideComposer": "HLT · Slide Composer"
    }
    assert not hasattr(node_module, "HLTTextComposer")


def test_logo_reserve_changes_geometry_and_mask_is_accepted() -> None:
    mask = Image.new("L", (160, 80), 255)
    without_reserve = measure_text_composition(
        ("A", "B"),
        canvas_size=CanvasSize(320, 480),
        logo_image=_logo(),
        logo_mask=mask,
        settings=TextRenderSettings(layout="split_2", reserve_logo_space=False),
    )
    with_reserve = measure_text_composition(
        ("A", "B"),
        canvas_size=CanvasSize(320, 480),
        logo_image=_logo(),
        logo_mask=mask,
        settings=TextRenderSettings(layout="split_2", reserve_logo_space=True),
    )

    assert without_reserve.logo_rect is not None
    assert with_reserve.logo_rect is not None
    assert with_reserve.geometry.content_rect.bottom < without_reserve.geometry.content_rect.bottom
    assert with_reserve.geometry.content_rect.bottom <= with_reserve.logo_rect.y


def _count_red_pixels(image: Image.Image) -> int:
    pixels = image.convert("RGB").load()
    return sum(
        1
        for y in range(image.height)
        for x in range(image.width)
        if pixels[x, y][0] > 160 and pixels[x, y][1] < 100 and pixels[x, y][2] < 100
    )


def _count_bright_pixels(image: Image.Image) -> int:
    pixels = image.convert("RGB").load()
    return sum(
        1
        for y in range(image.height)
        for x in range(image.width)
        if max(pixels[x, y]) > 220
    )
