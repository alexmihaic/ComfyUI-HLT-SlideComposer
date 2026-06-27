from __future__ import annotations

from PIL import Image

from hlt_slide.adaptive_mosaic import AdaptiveMosaicSettings
from hlt_slide.config import CanvasSize
from hlt_slide.renderer import (
    RenderSettings,
    SlideItem,
    measure_adaptive_mosaic_layout,
)


def image(size: tuple[int, int]) -> Image.Image:
    return Image.new("RGB", size, (120, 120, 120))


def rects_intersect(left, right) -> bool:
    return left.x < right.right and right.x < left.right and left.y < right.bottom and right.y < left.bottom


def test_candidate_specific_label_measurement_handles_distinct_heights_without_intersections() -> None:
    items = (
        SlideItem(image((640, 360)), "ONE LINE"),
        SlideItem(image((360, 640)), "TWO LINE LABEL THAT SHOULD WRAP"),
        SlideItem(image((400, 400)), "A VERY LONG LABEL THAT MUST BE CLIPPED OR FITTED WITHOUT OVERLAP"),
        SlideItem(image((360, 480)), ""),
    )

    layout, candidate = measure_adaptive_mosaic_layout(
        items,
        title="TITLE",
        canvas_size=CanvasSize(420, 720),
        settings=RenderSettings(
            label_font_size=28,
            minimum_font_size=16,
            max_label_lines=2,
            label_padding_top=9,
            label_padding_bottom=11,
            label_after_gap=18,
            label_min_height=34,
        ),
        adaptive_settings=AdaptiveMosaicSettings(strategy="balanced"),
    )

    occupied = []
    for index, block in enumerate(layout.blocks):
        occupied.append(block.image_rect)
        if index == 3:
            assert block.label_rect is None
            continue
        assert block.label_rect is not None
        assert block.label_rect.height >= 34
        assert block.label_rect.y >= block.image_rect.bottom
        occupied.append(block.label_rect)

    for left_index, left in enumerate(occupied):
        for right in occupied[left_index + 1 :]:
            assert not rects_intersect(left, right)
    assert candidate.penalties["label_overflow"] == 0


def test_adaptive_layout_respects_title_gap_footer_and_content_rect() -> None:
    layout, _candidate = measure_adaptive_mosaic_layout(
        (
            SlideItem(image((640, 360)), "A"),
            SlideItem(image((360, 640)), "B"),
        ),
        title="TITLE",
        canvas_size=CanvasSize(360, 640),
        settings=RenderSettings(
            outer_margin=30,
            top_margin=40,
            bottom_margin=35,
            title_gap=24,
            reserve_footer=True,
            footer_height=80,
            corner_radius=0,
        ),
    )

    assert layout.title_rect is not None
    assert layout.footer_rect is not None
    scale = 360 / 1080
    outer_margin = round(30 * scale)
    bottom_margin = round(35 * scale)
    title_gap = round(24 * scale)
    assert layout.title_rect.y == round(40 * scale)
    content_top = layout.title_rect.bottom + title_gap
    content_bottom = layout.footer_rect.y - bottom_margin
    for block in layout.blocks:
        assert block.image_rect.x >= outer_margin
        assert block.image_rect.y >= content_top
        assert block.image_rect.right <= 360 - outer_margin
        assert block.image_rect.bottom <= content_bottom
        if block.label_rect is not None:
            assert block.label_rect.y >= content_top
            assert block.label_rect.bottom <= content_bottom


def test_hero_index_assigns_dominant_area_and_rejects_out_of_range_index() -> None:
    items = (
        SlideItem(image((400, 400)), "A"),
        SlideItem(image((640, 360)), "B"),
        SlideItem(image((360, 480)), "C"),
        SlideItem(image((360, 640)), "D"),
    )

    for hero_index in (0, 1, 3):
        layout, _candidate = measure_adaptive_mosaic_layout(
            items,
            canvas_size=CanvasSize(420, 720),
            adaptive_settings=AdaptiveMosaicSettings(strategy="editorial", hero_index=hero_index),
        )
        areas = [block.image_rect.width * block.image_rect.height for block in layout.blocks]
        assert areas[hero_index] == max(areas)

    try:
        measure_adaptive_mosaic_layout(
            items,
            canvas_size=CanvasSize(420, 720),
            adaptive_settings=AdaptiveMosaicSettings(hero_index=4),
        )
    except ValueError as error:
        assert "hero_index" in str(error)
    else:
        raise AssertionError("Out-of-range hero_index did not fail.")
