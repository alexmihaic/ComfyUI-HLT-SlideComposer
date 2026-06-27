from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from hlt_slide.adaptive_mosaic import (
    AdaptiveMosaicSettings,
    MosaicCandidate,
    SourceImageInfo,
    describe_candidate,
    generate_mosaic_candidates,
    select_adaptive_mosaic,
)
from hlt_slide.config import CanvasSize, Rect


OUTPUT_DIR = Path("examples") / "outputs" / "adaptive-mosaic"
PREVIEW_WIDTH = 540
PREVIEW_HEIGHT = 960
BACKGROUND = (18, 18, 18)
FOREGROUND = (235, 235, 235)
ACCENT = (233, 33, 36)
LABEL_FILL = (40, 40, 40)
BLOCK_COLORS = (
    (58, 132, 255),
    (62, 181, 137),
    (244, 171, 68),
    (194, 93, 255),
)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = (
        (
            "one-image.png",
            CanvasSize(1080, 1920),
            (source(0, 1600, 900),),
            AdaptiveMosaicSettings(strategy="balanced", footer_height=120),
        ),
        (
            "two-mixed.png",
            CanvasSize(1080, 1920),
            (source(0, 1600, 900), source(1, 900, 1600)),
            AdaptiveMosaicSettings(strategy="balanced", footer_height=120),
        ),
        (
            "three-mixed-balanced.png",
            CanvasSize(1080, 1920),
            (source(0, 1600, 900), source(1, 900, 1600), source(2, 1000, 1000)),
            AdaptiveMosaicSettings(strategy="balanced", footer_height=120),
        ),
        (
            "three-mixed-editorial.png",
            CanvasSize(1080, 1920),
            (source(0, 1600, 900), source(1, 900, 1600), source(2, 1000, 1000)),
            AdaptiveMosaicSettings(strategy="editorial", footer_height=120),
        ),
        (
            "four-mixed-balanced.png",
            CanvasSize(1080, 1920),
            mixed_four_sources(),
            AdaptiveMosaicSettings(strategy="balanced", footer_height=120),
        ),
        (
            "four-mixed-editorial.png",
            CanvasSize(1080, 1920),
            mixed_four_sources(),
            AdaptiveMosaicSettings(strategy="editorial", footer_height=120),
        ),
        (
            "four-mixed-compact.png",
            CanvasSize(1080, 1920),
            mixed_four_sources(),
            AdaptiveMosaicSettings(strategy="compact", footer_height=120),
        ),
    )

    for filename, canvas, sources, settings in cases:
        _layout, candidate = select_adaptive_mosaic(canvas, sources, settings)
        image = draw_candidate(canvas, sources, candidate, settings)
        image.save(OUTPUT_DIR / filename)

    comparison = draw_candidate_comparison(
        CanvasSize(1080, 1920),
        mixed_four_sources(),
        AdaptiveMosaicSettings(strategy="balanced", footer_height=120),
    )
    comparison.save(OUTPUT_DIR / "candidate-comparison.png")


def source(index: int, width: int, height: int) -> SourceImageInfo:
    return SourceImageInfo(index, width, height, width / height, True)


def mixed_four_sources() -> tuple[SourceImageInfo, ...]:
    return (
        source(0, 2400, 900),
        source(1, 900, 1600),
        source(2, 1000, 1000),
        source(3, 900, 1200),
    )


def draw_candidate(
    canvas: CanvasSize,
    sources: tuple[SourceImageInfo, ...],
    candidate: MosaicCandidate,
    settings: AdaptiveMosaicSettings,
) -> Image.Image:
    image = Image.new("RGB", (PREVIEW_WIDTH, PREVIEW_HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    scale = min(PREVIEW_WIDTH / canvas.width, PREVIEW_HEIGHT / canvas.height)
    x_offset = round((PREVIEW_WIDTH - (canvas.width * scale)) / 2)
    y_offset = round((PREVIEW_HEIGHT - (canvas.height * scale)) / 2)

    draw.rectangle(
        (
            x_offset,
            y_offset,
            x_offset + round(canvas.width * scale) - 1,
            y_offset + round(canvas.height * scale) - 1,
        ),
        outline=(90, 90, 90),
        width=2,
    )

    for index, block in enumerate(candidate.blocks):
        color = BLOCK_COLORS[index % len(BLOCK_COLORS)]
        image_box = scale_rect(block.image_rect, scale, x_offset, y_offset)
        draw.rectangle(image_box, fill=color, outline=FOREGROUND, width=2)
        output_ratio = block.image_rect.width / max(1, block.image_rect.height)
        text = f"{sources[index].index} src {sources[index].aspect_ratio:.2f} out {output_ratio:.2f}"
        draw.text((image_box[0] + 8, image_box[1] + 8), text, fill=(0, 0, 0), font=font)
        if block.label_rect is not None:
            label_box = scale_rect(block.label_rect, scale, x_offset, y_offset)
            draw.rectangle(label_box, fill=LABEL_FILL, outline=ACCENT, width=1)
            draw.text((label_box[0] + 8, label_box[1] + 4), f"label {index}", fill=FOREGROUND, font=font)

    if settings.footer_height > 0:
        footer = Rect(0, canvas.height - settings.footer_height, canvas.width, settings.footer_height)
        footer_box = scale_rect(footer, scale, x_offset, y_offset)
        draw.rectangle(footer_box, outline=ACCENT, width=2)
        draw.text((footer_box[0] + 8, footer_box[1] + 8), "footer", fill=ACCENT, font=font)

    draw_overlay_text(draw, candidate, font)
    return image


def draw_candidate_comparison(
    canvas: CanvasSize,
    sources: tuple[SourceImageInfo, ...],
    settings: AdaptiveMosaicSettings,
) -> Image.Image:
    candidates = sorted(
        generate_mosaic_candidates(canvas, sources, settings),
        key=lambda item: item.score,
        reverse=True,
    )[:6]
    tile_width = PREVIEW_WIDTH
    tile_height = PREVIEW_HEIGHT
    sheet = Image.new("RGB", (tile_width * 3, tile_height * 2), BACKGROUND)
    for index, candidate in enumerate(candidates):
        tile = draw_candidate(canvas, sources, candidate, settings)
        sheet.paste(tile, ((index % 3) * tile_width, (index // 3) * tile_height))
    return sheet


def scale_rect(rect: Rect, scale: float, x_offset: int, y_offset: int) -> tuple[int, int, int, int]:
    return (
        x_offset + round(rect.x * scale),
        y_offset + round(rect.y * scale),
        x_offset + round(rect.right * scale),
        y_offset + round(rect.bottom * scale),
    )


def draw_overlay_text(draw: ImageDraw.ImageDraw, candidate: MosaicCandidate, font: ImageFont.ImageFont) -> None:
    unused = candidate.diagnostics.get("unused_area_percentage", 0)
    lines = (
        candidate.template_name,
        f"score {candidate.score:.1f}",
        f"unused {unused:.1f}%",
        describe_candidate(candidate)[:86],
    )
    y = 10
    for line in lines:
        draw.text((10, y), line, fill=FOREGROUND, font=font)
        y += 14


if __name__ == "__main__":
    main()
