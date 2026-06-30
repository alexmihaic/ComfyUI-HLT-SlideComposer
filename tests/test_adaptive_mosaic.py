from __future__ import annotations

import pytest

from hlt_slide.adaptive_mosaic import (
    AdaptiveMosaicSettings,
    SourceImageInfo,
    describe_candidate,
    fit_rect_preserving_aspect,
    generate_mosaic_candidates,
    select_adaptive_mosaic,
)
from hlt_slide.config import CanvasSize, Rect


def source(index: int, width: int, height: int, *, has_label: bool = True) -> SourceImageInfo:
    return SourceImageInfo(
        index=index,
        width=width,
        height=height,
        aspect_ratio=width / height,
        has_label=has_label,
    )


def assert_rect_inside(inner: Rect, outer: Rect) -> None:
    assert inner.x >= outer.x
    assert inner.y >= outer.y
    assert inner.right <= outer.right
    assert inner.bottom <= outer.bottom
    assert inner.width > 0
    assert inner.height > 0


def assert_no_intersections(rects: tuple[Rect, ...]) -> None:
    for left_index, left in enumerate(rects):
        for right in rects[left_index + 1 :]:
            overlaps_x = left.x < right.right and right.x < left.right
            overlaps_y = left.y < right.bottom and right.y < left.bottom
            assert not (overlaps_x and overlaps_y)


@pytest.mark.parametrize(
    ("canvas", "sources"),
    [
        (CanvasSize(1080, 1920), (source(0, 1600, 900),)),
        (CanvasSize(1080, 1350), (source(0, 1600, 900), source(1, 900, 1600))),
        (
            CanvasSize(1536, 2048),
            (source(0, 1000, 1000), source(1, 900, 1600), source(2, 1200, 900)),
        ),
        (
            CanvasSize(1080, 1080),
            (
                source(0, 1600, 900),
                source(1, 900, 1600),
                source(2, 1000, 1000),
                source(3, 900, 1200),
            ),
        ),
        (
            CanvasSize(1920, 1080),
            (
                source(0, 2400, 900),
                source(1, 900, 1600),
                source(2, 1000, 1000),
                source(3, 1200, 900),
            ),
        ),
    ],
)
def test_selects_geometry_inside_canvas_for_common_canvases(
    canvas: CanvasSize, sources: tuple[SourceImageInfo, ...]
) -> None:
    layout, candidate = select_adaptive_mosaic(canvas, sources)
    canvas_rect = Rect(0, 0, canvas.width, canvas.height)

    assert len(layout.blocks) == len(sources)
    assert candidate.template_name
    assert candidate.score > 0
    assert candidate.diagnostics["unused_area_percentage"] >= 0

    occupied_rects: list[Rect] = []
    for block, image in zip(layout.blocks, sources):
        assert block.image_rect.width / block.image_rect.height == pytest.approx(
            image.aspect_ratio, rel=0.025
        )
        assert_rect_inside(block.image_rect, canvas_rect)
        occupied_rects.append(block.image_rect)
        if image.has_label:
            assert block.label_rect is not None
            assert_rect_inside(block.label_rect, canvas_rect)
            assert block.label_rect.y >= block.image_rect.bottom
            occupied_rects.append(block.label_rect)
        else:
            assert block.label_rect is None

    if layout.footer_rect is not None:
        assert_rect_inside(layout.footer_rect, canvas_rect)
        occupied_rects.append(layout.footer_rect)
    assert_no_intersections(tuple(occupied_rects))


def test_fit_rect_preserving_aspect_never_exits_available_rect() -> None:
    fitted = fit_rect_preserving_aspect(
        1600,
        900,
        Rect(10, 20, 300, 600),
        alignment=("center", "center"),
    )

    assert fitted == Rect(10, 236, 300, 169)


def test_labels_and_footer_are_reserved_without_intersections() -> None:
    layout, _candidate = select_adaptive_mosaic(
        CanvasSize(1080, 1920),
        (source(0, 1600, 900), source(1, 900, 1600), source(2, 1000, 1000)),
        AdaptiveMosaicSettings(gap=32, footer_height=120),
        label_heights=(56, 72, 64),
    )

    rects = []
    for block in layout.blocks:
        rects.append(block.image_rect)
        assert block.label_rect is not None
        rects.append(block.label_rect)
    assert layout.footer_rect is not None
    rects.append(layout.footer_rect)

    assert_no_intersections(tuple(rects))
    assert all(block.label_rect is not None for block in layout.blocks)


def test_explicit_hero_index_prefers_template_containing_requested_side() -> None:
    sources = (
        source(0, 900, 1600),
        source(1, 2400, 900),
        source(2, 1000, 1000),
        source(3, 900, 1200),
    )

    _layout, candidate = select_adaptive_mosaic(
        CanvasSize(1080, 1920),
        sources,
        AdaptiveMosaicSettings(strategy="editorial", hero_index=1),
    )

    hero_block = candidate.blocks[1].image_rect
    other_areas = [
        block.image_rect.width * block.image_rect.height
        for index, block in enumerate(candidate.blocks)
        if index != 1
    ]
    assert hero_block.width * hero_block.height > max(other_areas)


def test_candidate_description_contains_diagnostics() -> None:
    _layout, candidate = select_adaptive_mosaic(
        CanvasSize(1080, 1920),
        (source(0, 1600, 900), source(1, 900, 1600)),
    )

    description = describe_candidate(candidate)

    assert candidate.template_name in description
    assert "score=" in description
    assert "unused_area_percentage=" in description
    assert "source_aspect_ratio=" in description
    assert "output_aspect_ratio=" in description


def test_rejects_invalid_source_count_with_descriptive_error() -> None:
    with pytest.raises(ValueError, match="1 to 4"):
        select_adaptive_mosaic(CanvasSize(1080, 1920), ())

    with pytest.raises(ValueError, match="1 to 4"):
        select_adaptive_mosaic(
            CanvasSize(1080, 1920),
            tuple(source(index, 1000, 1000) for index in range(5)),
        )


@pytest.mark.parametrize(
    ("sources", "expected_templates"),
    [
        ((source(0, 1000, 1000),), {"single"}),
        (
            (source(0, 1600, 900), source(1, 900, 1600)),
            {"row_2", "column_2", "hero_left", "hero_right", "hero_top", "hero_bottom"},
        ),
        (
            (source(0, 1600, 900), source(1, 900, 1600), source(2, 1000, 1000)),
            {
                "row_3",
                "column_3",
                "hero_left_2_stack",
                "hero_right_2_stack",
                "hero_top_2_row",
                "hero_bottom_2_row",
                "justified_1_2",
                "justified_2_1",
            },
        ),
        (
            (
                source(0, 1600, 900),
                source(1, 900, 1600),
                source(2, 1000, 1000),
                source(3, 900, 1200),
            ),
            {
                "grid_2x2",
                "hero_left_3_stack",
                "hero_right_3_stack",
                "hero_top_3_row",
                "hero_bottom_3_row",
                "justified_1_3",
                "justified_3_1",
                "justified_2_2",
            },
        ),
    ],
)
def test_internal_candidate_template_inventory_is_stable(
    sources: tuple[SourceImageInfo, ...], expected_templates: set[str]
) -> None:
    candidates = generate_mosaic_candidates(CanvasSize(1080, 1920), sources)

    assert {candidate.template_name for candidate in candidates} == expected_templates
