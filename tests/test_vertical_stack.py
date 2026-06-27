from __future__ import annotations

import pytest

from hlt_slide.config import CanvasSize
from hlt_slide.exceptions import LayoutOverflowError
from hlt_slide.layouts import VerticalStackMetrics, calculate_vertical_stack


def _all_rects(layout):
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


def test_vertical_stack_builds_one_to_four_positive_blocks() -> None:
    for count in (1, 2, 3, 4):
        layout = calculate_vertical_stack(
            CanvasSize(1080, 1920),
            image_count=count,
            title_height=0,
            label_heights=tuple(0 for _ in range(count)),
        )

        assert len(layout.blocks) == count
        assert all(block.image_rect.height > 0 for block in layout.blocks)


def test_vertical_stack_omits_empty_title_labels_and_footer() -> None:
    layout = calculate_vertical_stack(
        CanvasSize(1080, 1920),
        image_count=2,
        title_height=0,
        label_heights=(0, 24),
        reserve_footer=False,
    )

    assert layout.title_rect is None
    assert layout.blocks[0].label_rect is None
    assert layout.blocks[1].label_rect is not None
    assert layout.footer_rect is None


def test_vertical_stack_places_rectangles_inside_canvas_without_intersections() -> None:
    canvas = CanvasSize(1152, 2048)
    layout = calculate_vertical_stack(
        canvas,
        image_count=3,
        title_height=70,
        label_heights=(30, 0, 30),
        reserve_footer=True,
        footer_height=90,
    )

    previous_bottom = 0
    for rect in _all_rects(layout):
        assert rect.x >= 0
        assert rect.y >= previous_bottom
        assert rect.right <= canvas.width
        assert rect.bottom <= canvas.height
        assert rect.width > 0
        assert rect.height > 0
        previous_bottom = rect.bottom


def test_vertical_stack_scales_dimensions_for_different_resolutions() -> None:
    base = calculate_vertical_stack(
        CanvasSize(1080, 1920),
        image_count=2,
        title_height=64,
        label_heights=(34, 34),
    )
    larger = calculate_vertical_stack(
        CanvasSize(1536, 2048),
        image_count=2,
        title_height=91,
        label_heights=(48, 48),
    )

    assert base.blocks[0].image_rect.x == 64
    assert larger.blocks[0].image_rect.x == 91
    assert larger.blocks[0].image_rect.width == 1536 - 2 * 91


def test_vertical_stack_distribution_is_deterministic() -> None:
    first = calculate_vertical_stack(
        CanvasSize(1080, 1920),
        image_count=3,
        title_height=64,
        label_heights=(34, 34, 34),
    )
    second = calculate_vertical_stack(
        CanvasSize(1080, 1920),
        image_count=3,
        title_height=64,
        label_heights=(34, 34, 34),
    )

    assert first == second
    heights = [block.image_rect.height for block in first.blocks]
    assert max(heights) - min(heights) <= 1


def test_vertical_stack_overflow_reports_context() -> None:
    with pytest.raises(LayoutOverflowError, match="canvas=120x160"):
        calculate_vertical_stack(
            CanvasSize(120, 160),
            image_count=4,
            title_height=80,
            label_heights=(40, 40, 40, 40),
            reserve_footer=True,
            footer_height=40,
        )


def test_vertical_stack_label_after_gap_controls_next_image_spacing() -> None:
    label_after_gap = 26
    layout = calculate_vertical_stack(
        CanvasSize(1080, 1400),
        image_count=2,
        label_heights=(48, 32),
        metrics=VerticalStackMetrics(block_gap=0, label_after_gap=label_after_gap),
    )

    first, second = layout.blocks
    assert first.label_rect is not None
    assert first.label_rect.bottom + label_after_gap <= second.image_rect.y
