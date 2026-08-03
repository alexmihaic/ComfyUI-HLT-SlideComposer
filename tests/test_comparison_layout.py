from __future__ import annotations

import pytest

from hlt_slide.config import CanvasSize, Rect
from hlt_slide.exceptions import LayoutOverflowError
from hlt_slide.layouts import GridMetrics, calculate_comparison, calculate_vertical_stack


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


def _intersects(a: Rect, b: Rect) -> bool:
    return a.x < b.right and a.right > b.x and a.y < b.bottom and a.bottom > b.y


def _assert_inside_without_intersections(canvas: CanvasSize, rects: list[Rect]) -> None:
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


def test_comparison_one_image_falls_back_to_vertical_stack_geometry() -> None:
    canvas = CanvasSize(1080, 1920)
    comparison = calculate_comparison(
        canvas,
        image_count=1,
        title_height=64,
        label_heights=(40,),
    )
    vertical = calculate_vertical_stack(
        canvas,
        image_count=1,
        title_height=64,
        label_heights=(40,),
    )

    assert comparison == vertical


def test_comparison_two_images_uses_side_by_side_on_square_or_horizontal_canvas() -> None:
    for canvas in (CanvasSize(1080, 1080), CanvasSize(1600, 900)):
        layout = calculate_comparison(
            canvas,
            image_count=2,
            title_height=40,
            label_heights=(32, 40),
        )

        first, second = layout.blocks
        assert first.image_rect.y == second.image_rect.y
        assert first.image_rect.x < second.image_rect.x
        assert first.image_rect.height == second.image_rect.height
        assert first.label_rect is not None
        assert second.label_rect is not None
        assert first.label_rect.y == second.label_rect.y
        assert first.label_rect.height == second.label_rect.height == 40
        _assert_inside_without_intersections(canvas, _rects(layout))


def test_comparison_two_images_uses_vertical_comparison_on_portrait_canvas() -> None:
    for canvas in (CanvasSize(1080, 1920), CanvasSize(1080, 1350)):
        layout = calculate_comparison(
            canvas,
            image_count=2,
            title_height=40,
            label_heights=(32, 40),
        )

        first, second = layout.blocks
        assert first.image_rect.x == second.image_rect.x
        assert first.image_rect.width == second.image_rect.width
        assert first.image_rect.y < second.image_rect.y
        assert first.label_rect is not None
        assert first.label_rect.bottom < second.image_rect.y
        _assert_inside_without_intersections(canvas, _rects(layout))


def test_comparison_three_images_keeps_first_two_as_primary_pair_with_debug_below() -> None:
    canvas = CanvasSize(1080, 1920)
    layout = calculate_comparison(
        canvas,
        image_count=3,
        title_height=60,
        label_heights=(32, 32, 40),
    )

    first, second, debug = layout.blocks
    assert first.image_rect.y == second.image_rect.y
    assert first.image_rect.x < second.image_rect.x
    assert debug.image_rect.y > first.label_rect.bottom
    assert debug.image_rect.width == first.image_rect.width + second.image_rect.width + 30
    assert debug.label_rect is not None
    _assert_inside_without_intersections(canvas, _rects(layout))


def test_comparison_four_images_uses_editorial_two_by_two_grid() -> None:
    canvas = CanvasSize(1080, 1920)
    layout = calculate_comparison(
        canvas,
        image_count=4,
        title_height=60,
        label_heights=(32, 32, 40, 40),
        reserve_footer=True,
        footer_height=96,
    )

    first, second, third, fourth = layout.blocks
    assert first.image_rect.x == third.image_rect.x
    assert second.image_rect.x == fourth.image_rect.x
    assert first.image_rect.y == second.image_rect.y
    assert third.image_rect.y == fourth.image_rect.y
    assert third.image_rect.y > first.label_rect.bottom
    assert layout.footer_rect is not None
    assert layout.footer_rect.y >= third.label_rect.bottom
    _assert_inside_without_intersections(canvas, _rects(layout))


def test_comparison_respects_custom_metrics_and_reports_overflow() -> None:
    layout = calculate_comparison(
        CanvasSize(800, 600),
        image_count=2,
        label_heights=(24, 24),
        metrics=GridMetrics(outer_margin=40, column_gap=20),
    )

    assert layout.blocks[0].image_rect.x == 30
    assert layout.blocks[1].image_rect.x > layout.blocks[0].image_rect.right

    with pytest.raises(LayoutOverflowError, match="comparison overflow"):
        calculate_comparison(
            CanvasSize(120, 120),
            image_count=4,
            title_height=70,
            label_heights=(40, 40, 40, 40),
            reserve_footer=True,
            footer_height=50,
        )
