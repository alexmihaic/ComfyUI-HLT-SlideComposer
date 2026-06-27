from __future__ import annotations

from PIL import Image

from hlt_slide.adaptive_mosaic import AdaptiveMosaicSettings, SourceImageInfo, select_adaptive_mosaic
from hlt_slide.config import CanvasSize, Rect
from hlt_slide.renderer import RenderSettings, SlideItem, measure_adaptive_mosaic_layout


def image(size: tuple[int, int]) -> Image.Image:
    return Image.new("RGB", size, (100, 150, 200))


def source(index: int, width: int, height: int) -> SourceImageInfo:
    return SourceImageInfo(index, width, height, width / height, True)


def ratio_error(output_ratio: float, source_ratio: float, width: int, height: int) -> float:
    one_pixel_ratio_slack = max(1 / max(1, width), 1 / max(1, height)) * 2.5
    return abs(output_ratio - source_ratio) / source_ratio - one_pixel_ratio_slack


def test_content_rect_api_keeps_blocks_inside_explicit_area_and_preserves_title_footer() -> None:
    content = Rect(40, 120, 320, 420)
    title = Rect(40, 40, 320, 50)
    footer = Rect(40, 570, 320, 60)
    sources = (source(0, 640, 360), source(1, 360, 640), source(2, 400, 400))

    layout, _candidate = select_adaptive_mosaic(
        CanvasSize(400, 640),
        sources,
        AdaptiveMosaicSettings(gap=16),
        content_rect=content,
        title_rect=title,
        footer_rect=footer,
    )

    assert layout.title_rect == title
    assert layout.footer_rect == footer
    for block in layout.blocks:
        assert block.image_rect.x >= content.x
        assert block.image_rect.y >= content.y
        assert block.image_rect.right <= content.right
        assert block.image_rect.bottom <= content.bottom
        if block.label_rect is not None:
            assert block.label_rect.x >= content.x
            assert block.label_rect.bottom <= content.bottom


def test_adaptive_geometry_preserves_aspect_ratio_with_pixel_based_tolerance() -> None:
    items = (
        SlideItem(image((400, 400)), "1:1"),
        SlideItem(image((640, 360)), "16:9"),
        SlideItem(image((360, 480)), "3:4"),
        SlideItem(image((360, 640)), "9:16"),
    )
    layout, _candidate = measure_adaptive_mosaic_layout(
        items,
        canvas_size=CanvasSize(540, 960),
        settings=RenderSettings(corner_radius=0),
        adaptive_settings=AdaptiveMosaicSettings(strategy="balanced"),
    )

    for item, block in zip(items, layout.blocks):
        output_ratio = block.image_rect.width / block.image_rect.height
        source_ratio = item.image.width / item.image.height
        assert ratio_error(
            output_ratio,
            source_ratio,
            block.image_rect.width,
            block.image_rect.height,
        ) <= 0


def test_strategy_scoring_contract_for_balanced_editorial_and_compact() -> None:
    items = (
        SlideItem(image((400, 400)), "1:1"),
        SlideItem(image((640, 360)), "16:9"),
        SlideItem(image((360, 480)), "3:4"),
        SlideItem(image((360, 640)), "9:16"),
    )
    results = {
        strategy: measure_adaptive_mosaic_layout(
            items,
            canvas_size=CanvasSize(540, 960),
            adaptive_settings=AdaptiveMosaicSettings(strategy=strategy),
        )[1]
        for strategy in ("balanced", "editorial", "compact")
    }

    balanced_unused = results["balanced"].diagnostics["unused_area_percentage"]
    compact_unused = results["compact"].diagnostics["unused_area_percentage"]
    assert compact_unused <= balanced_unused or results["compact"].template_name == results["balanced"].template_name

    balanced_areas = [block.image_rect.width * block.image_rect.height for block in results["balanced"].blocks]
    editorial_areas = [block.image_rect.width * block.image_rect.height for block in results["editorial"].blocks]
    assert max(editorial_areas) / min(editorial_areas) >= max(balanced_areas) / min(balanced_areas)
