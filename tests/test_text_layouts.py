from __future__ import annotations

import importlib

import pytest

from hlt_slide.config import CanvasSize, Rect
from hlt_slide.text_layouts import (
    ROLE_GEOMETRY_WEIGHTS,
    TextLayoutSettings,
    active_text_blocks,
    describe_text_layout,
    resolve_text_layout_name,
    select_text_layout,
)


def _blocks(count: int) -> tuple[str, ...]:
    return tuple(f"Text {index}" for index in range(1, count + 1))


def _roles(count: int) -> tuple[str, ...]:
    defaults = ("headline", "subheadline", "body", "caption")
    return defaults[:count]


def _assert_inside(outer: Rect, inner: Rect) -> None:
    assert inner.x >= outer.x
    assert inner.y >= outer.y
    assert inner.right <= outer.right
    assert inner.bottom <= outer.bottom


def _assert_no_overlaps(rects: tuple[Rect, ...]) -> None:
    for left_index, left in enumerate(rects):
        for right in rects[left_index + 1 :]:
            assert not (
                left.x < right.right
                and right.x < left.right
                and left.y < right.bottom
                and right.y < left.bottom
            )


def test_active_text_blocks_omits_empty_slots_and_preserves_source_order() -> None:
    blocks = active_text_blocks(
        (" Headline ", "", "Línea uno\nlínea dos áéíóú", "   "),
        ("headline", "subheadline", "body", "caption"),
    )

    assert [block.source_index for block in blocks] == [0, 2]
    assert [block.role for block in blocks] == ["headline", "body"]
    assert blocks[0].text == " Headline "
    assert blocks[1].text == "Línea uno\nlínea dos áéíóú"


def test_active_text_blocks_rejects_empty_invalid_roles_and_more_than_four_slots() -> None:
    with pytest.raises(ValueError, match="at least one active"):
        active_text_blocks(("", " ", "\n"), ("headline", "body", "caption"))

    with pytest.raises(ValueError, match="Invalid text role"):
        active_text_blocks(("Hello",), ("hero",))

    with pytest.raises(ValueError, match="at most 4"):
        active_text_blocks(("1", "2", "3", "4", "5"), ("body",) * 5)


@pytest.mark.parametrize(
    ("count", "expected"),
    [
        (1, "centered_statement"),
        (2, "split_2"),
        (3, "vertical_stack"),
        (4, "grid_2x2"),
    ],
)
def test_auto_text_resolves_by_active_count(count: int, expected: str) -> None:
    assert resolve_text_layout_name("auto_text", count) == expected
    assert resolve_text_layout_name("auto_text", count) == expected


def test_resolve_text_layout_name_rejects_unsupported_counts_and_names() -> None:
    with pytest.raises(ValueError, match="1 to 4"):
        resolve_text_layout_name("auto_text", 0)
    with pytest.raises(ValueError, match="Unsupported text layout"):
        resolve_text_layout_name("unknown", 1)


@pytest.mark.parametrize(
    ("canvas", "requested", "count"),
    [
        (CanvasSize(1080, 1920), "centered_statement", 1),
        (CanvasSize(1080, 1920), "vertical_stack", 4),
        (CanvasSize(1080, 1350), "vertical_stack", 3),
        (CanvasSize(1080, 1080), "split_2", 2),
        (CanvasSize(1920, 1080), "split_2", 2),
        (CanvasSize(320, 320), "grid_2x2", 4),
        (CanvasSize(320, 480), "editorial_quote", 2),
    ],
)
def test_layout_rectangles_are_positive_inside_content_and_non_overlapping(
    canvas: CanvasSize,
    requested: str,
    count: int,
) -> None:
    source_blocks = active_text_blocks(_blocks(count), _roles(count))
    layout = select_text_layout(canvas, source_blocks, TextLayoutSettings(), requested)
    rects = tuple(block.rect for block in layout.blocks)

    assert layout.content_rect.width > 0
    assert layout.content_rect.height > 0
    assert all(rect.width > 0 and rect.height > 0 for rect in rects)
    assert all(block.inner_rect.width > 0 and block.inner_rect.height > 0 for block in layout.blocks)
    for rect in rects:
        _assert_inside(layout.content_rect, rect)
    _assert_no_overlaps(rects)


def test_vertical_stack_uses_role_weights_without_reordering_source_indexes() -> None:
    source_blocks = active_text_blocks(
        ("Caption", "Headline"),
        ("caption", "headline"),
    )
    layout = select_text_layout(
        CanvasSize(1080, 1920),
        source_blocks,
        TextLayoutSettings(block_gap=20),
        "vertical_stack",
    )

    assert tuple(block.source_index for block in layout.blocks) == (0, 1)
    caption, headline = layout.blocks
    assert headline.rect.height > caption.rect.height
    assert ROLE_GEOMETRY_WEIGHTS["number"] > ROLE_GEOMETRY_WEIGHTS["headline"]
    assert ROLE_GEOMETRY_WEIGHTS["headline"] > ROLE_GEOMETRY_WEIGHTS["caption"]


def test_split_2_auto_and_forced_axes_are_deterministic() -> None:
    source_blocks = active_text_blocks(("A", "B"), ("headline", "caption"))

    portrait = select_text_layout(
        CanvasSize(1080, 1920),
        source_blocks,
        TextLayoutSettings(split_axis="auto"),
        "split_2",
    )
    landscape = select_text_layout(
        CanvasSize(1920, 1080),
        source_blocks,
        TextLayoutSettings(split_axis="auto"),
        "split_2",
    )
    square = select_text_layout(
        CanvasSize(1080, 1080),
        source_blocks,
        TextLayoutSettings(split_axis="auto"),
        "split_2",
    )
    forced_horizontal = select_text_layout(
        CanvasSize(1080, 1920),
        source_blocks,
        TextLayoutSettings(split_axis="horizontal"),
        "split_2",
    )

    assert portrait.diagnostics.split_axis_resolved == "vertical"
    assert portrait.blocks[0].rect.y < portrait.blocks[1].rect.y
    assert landscape.diagnostics.split_axis_resolved == "horizontal"
    assert landscape.blocks[0].rect.x < landscape.blocks[1].rect.x
    assert square.diagnostics.split_axis_resolved == "vertical"
    assert forced_horizontal.diagnostics.split_axis_resolved == "horizontal"


def test_split_2_rejects_wrong_block_count() -> None:
    source_blocks = active_text_blocks(("A", "B", "C"), ("headline", "body", "caption"))

    with pytest.raises(ValueError, match="exactly 2"):
        select_text_layout(CanvasSize(1080, 1920), source_blocks, TextLayoutSettings(), "split_2")


@pytest.mark.parametrize("count", [2, 3, 4])
def test_grid_2x2_keeps_reading_order_for_supported_counts(count: int) -> None:
    source_blocks = active_text_blocks(_blocks(count), _roles(count))
    layout = select_text_layout(CanvasSize(1080, 1920), source_blocks, TextLayoutSettings(), "grid_2x2")

    assert tuple(block.source_index for block in layout.blocks) == tuple(range(count))
    if count == 2:
        assert layout.blocks[0].grid_cell == (0, 0)
        assert layout.blocks[1].grid_cell == (0, 1)
    if count == 3:
        assert tuple(block.grid_cell for block in layout.blocks) == ((0, 0), (0, 1), (1, 0))


def test_editorial_quote_gives_main_block_dominant_area() -> None:
    one = select_text_layout(
        CanvasSize(1080, 1920),
        active_text_blocks(("Quote",), ("quote",)),
        TextLayoutSettings(),
        "editorial_quote",
    )
    two = select_text_layout(
        CanvasSize(1080, 1920),
        active_text_blocks(("Quote", "Author"), ("quote", "caption")),
        TextLayoutSettings(block_gap=24),
        "editorial_quote",
    )

    assert one.blocks[0].rect == one.content_rect
    assert two.blocks[0].rect.height > two.blocks[1].rect.height * 2


def test_settings_validate_numeric_values_and_split_axis() -> None:
    with pytest.raises(ValueError, match="outer_margin"):
        TextLayoutSettings(outer_margin=-1)
    with pytest.raises(ValueError, match="split_axis"):
        TextLayoutSettings(split_axis="diagonal")


def test_describe_text_layout_is_readable_and_deterministic() -> None:
    source_blocks = active_text_blocks(("A", "B"), ("headline", "caption"))
    layout = select_text_layout(CanvasSize(1080, 1920), source_blocks, TextLayoutSettings(), "auto_text")

    first = describe_text_layout(layout)
    second = describe_text_layout(layout)

    assert first == second
    assert "requested_layout=auto_text" in first
    assert "effective_layout=split_2" in first
    assert "active_count=2" in first
    assert "source_order=(0, 1)" in first
    assert "roles=('headline', 'caption')" in first


def test_slide_composer_contract_is_unchanged_with_text_composer_registered() -> None:
    node_module = importlib.import_module("nodes")

    assert node_module.NODE_CLASS_MAPPINGS["HLTSlideComposer"] is node_module.HLTSlideComposer
    assert node_module.NODE_CLASS_MAPPINGS["HLTTextComposer"] is node_module.HLTTextComposer
    assert node_module.NODE_DISPLAY_NAME_MAPPINGS == {
        "HLTSlideComposer": "HLT · Slide Composer",
        "HLTTextComposer": "HLT · Text Composer",
    }
