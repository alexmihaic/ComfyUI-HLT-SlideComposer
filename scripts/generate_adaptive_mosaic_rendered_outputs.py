from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from hlt_slide.adaptive_mosaic import AdaptiveMosaicSettings
from hlt_slide.config import CanvasSize
from hlt_slide.renderer import RenderSettings, SlideItem, render_adaptive_mosaic, render_vertical_stack


OUTPUT_DIR = Path("examples") / "outputs" / "adaptive-mosaic-rendered"
CANVAS = CanvasSize(720, 1280)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    items = mixed_items()
    settings = base_settings()

    outputs: dict[str, Image.Image] = {
        "one-image.png": render_adaptive_mosaic(
            items[:1], title="ONE IMAGE", canvas_size=CANVAS, settings=settings
        ),
        "two-mixed-balanced.png": render_adaptive_mosaic(
            items[:2],
            title="TWO MIXED",
            canvas_size=CANVAS,
            settings=settings,
            adaptive_settings=AdaptiveMosaicSettings(strategy="balanced"),
        ),
        "three-mixed-balanced.png": render_adaptive_mosaic(
            items[:3],
            title="THREE MIXED",
            canvas_size=CANVAS,
            settings=settings,
            adaptive_settings=AdaptiveMosaicSettings(strategy="balanced"),
        ),
        "four-mixed-balanced.png": render_adaptive_mosaic(
            items,
            title="BALANCED",
            canvas_size=CANVAS,
            settings=settings,
            adaptive_settings=AdaptiveMosaicSettings(strategy="balanced"),
        ),
        "four-mixed-editorial.png": render_adaptive_mosaic(
            items,
            title="EDITORIAL",
            canvas_size=CANVAS,
            settings=settings,
            adaptive_settings=AdaptiveMosaicSettings(strategy="editorial"),
        ),
        "four-mixed-compact.png": render_adaptive_mosaic(
            items,
            title="COMPACT",
            canvas_size=CANVAS,
            settings=settings,
            adaptive_settings=AdaptiveMosaicSettings(strategy="compact"),
        ),
        "four-mixed-with-labels.png": render_adaptive_mosaic(
            long_label_items(),
            title="LABEL FITTING",
            canvas_size=CANVAS,
            settings=settings,
            adaptive_settings=AdaptiveMosaicSettings(strategy="balanced"),
        ),
        "four-mixed-background-logo.png": render_adaptive_mosaic(
            items,
            title="BG + LOGO",
            canvas_size=CANVAS,
            background_image=synthetic_background((CANVAS.width, CANVAS.height)),
            logo_image=synthetic_logo(),
            settings=RenderSettings(
                **{
                    **base_settings().__dict__,
                    "background_mode": "image_with_overlay",
                    "background_color": "#050505",
                    "overlay_opacity": 0.45,
                    "reserve_footer": True,
                    "footer_height": 116,
                    "logo_width_percent": 20,
                    "debug_layout": False,
                }
            ),
            adaptive_settings=AdaptiveMosaicSettings(strategy="balanced"),
        ),
        "four-mixed-debug.png": render_adaptive_mosaic(
            items,
            title="DEBUG",
            canvas_size=CANVAS,
            settings=RenderSettings(**{**base_settings().__dict__, "debug_layout": True}),
            adaptive_settings=AdaptiveMosaicSettings(strategy="balanced"),
        ),
    }

    comparison = comparison_existing_layouts(items, settings)
    outputs["comparison-existing-layouts.png"] = comparison

    for filename, image in outputs.items():
        image.save(OUTPUT_DIR / filename)
    contact = contact_sheet(tuple(outputs.values()), tuple(outputs.keys()))
    contact.save(OUTPUT_DIR / "review-contact-sheet.png")


def base_settings() -> RenderSettings:
    return RenderSettings(
        background_color="#111111",
        title_color="#E92124",
        label_color="#E92124",
        border_width=2,
        border_color="#E92124",
        corner_radius=18,
        image_fit="cover",
        contain_fill_mode="cell_color",
        outer_margin=64,
        top_margin=58,
        bottom_margin=50,
        title_gap=28,
        inner_padding=24,
        label_font_size=30,
        minimum_font_size=16,
        max_label_lines=2,
        label_clip=True,
    )


def mixed_items() -> tuple[SlideItem, ...]:
    return (
        SlideItem(synthetic_ratio_image((480, 480), (206, 68, 80), "1:1"), "SQUARE 1:1"),
        SlideItem(synthetic_ratio_image((640, 360), (68, 168, 94), "16:9"), "LANDSCAPE 16:9"),
        SlideItem(synthetic_ratio_image((360, 480), (76, 112, 220), "3:4"), "PORTRAIT 3:4"),
        SlideItem(synthetic_ratio_image((360, 640), (230, 168, 66), "9:16"), "TALL 9:16"),
    )


def long_label_items() -> tuple[SlideItem, ...]:
    base = mixed_items()
    labels = (
        "SQUARE SHORT",
        "LANDSCAPE WITH A TWO LINE LABEL",
        "PORTRAIT LABEL THAT IS INTENTIONALLY LONG TO EXERCISE CLIPPING",
        "TALL IMAGE",
    )
    return tuple(SlideItem(item.image, labels[index]) for index, item in enumerate(base))


def synthetic_ratio_image(
    size: tuple[int, int],
    color: tuple[int, int, int],
    ratio_label: str,
) -> Image.Image:
    image = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    width, height = size
    draw.rectangle((4, 4, width - 5, height - 5), outline=(255, 255, 255), width=5)
    draw.rectangle((18, 18, width - 19, height - 19), outline=(0, 0, 0), width=3)
    draw.line((0, 0, width - 1, height - 1), fill=(255, 255, 255), width=4)
    draw.line((0, height - 1, width - 1, 0), fill=(0, 0, 0), width=4)
    for x, y, label in (
        (10, 10, "TL"),
        (width - 42, 10, "TR"),
        (10, height - 24, "BL"),
        (width - 42, height - 24, "BR"),
    ):
        draw.text((x, y), label, fill=(255, 255, 255), font=font)
    draw.text((width // 2 - 18, height // 2 - 6), ratio_label, fill=(255, 255, 255), font=font)
    return image


def synthetic_background(size: tuple[int, int]) -> Image.Image:
    image = Image.new("RGB", size, (44, 46, 58))
    draw = ImageDraw.Draw(image)
    for x in range(-size[1], size[0], 44):
        draw.line((x, 0, x + size[1], size[1]), fill=(92, 94, 112), width=4)
    for y in range(0, size[1], 96):
        draw.rectangle((0, y, size[0], y + 12), fill=(65, 68, 86))
    return image


def synthetic_logo() -> Image.Image:
    image = Image.new("RGBA", (220, 90), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((12, 18, 208, 72), radius=18, fill=(233, 33, 36, 230))
    draw.text((76, 38), "HLT", fill=(255, 255, 255, 255), font=ImageFont.load_default())
    return image


def comparison_existing_layouts(items: tuple[SlideItem, ...], settings: RenderSettings) -> Image.Image:
    variants = (
        (
            "vertical_stack",
            render_vertical_stack(
                items,
                title="VERTICAL STACK",
                canvas_size=CANVAS,
                settings=RenderSettings(**{**settings.__dict__, "layout": "vertical_stack"}),
            ),
        ),
        (
            "grid_2x2",
            render_vertical_stack(
                items,
                title="GRID 2X2",
                canvas_size=CANVAS,
                settings=RenderSettings(**{**settings.__dict__, "layout": "grid_2x2"}),
            ),
        ),
        (
            "adaptive balanced",
            render_adaptive_mosaic(
                items,
                title="ADAPTIVE BALANCED",
                canvas_size=CANVAS,
                settings=settings,
                adaptive_settings=AdaptiveMosaicSettings(strategy="balanced"),
            ),
        ),
        (
            "adaptive editorial",
            render_adaptive_mosaic(
                items,
                title="ADAPTIVE EDITORIAL",
                canvas_size=CANVAS,
                settings=settings,
                adaptive_settings=AdaptiveMosaicSettings(strategy="editorial"),
            ),
        ),
        (
            "adaptive compact",
            render_adaptive_mosaic(
                items,
                title="ADAPTIVE COMPACT",
                canvas_size=CANVAS,
                settings=settings,
                adaptive_settings=AdaptiveMosaicSettings(strategy="compact"),
            ),
        ),
    )
    return contact_sheet(tuple(image for _name, image in variants), tuple(name for name, _image in variants))


def contact_sheet(images: tuple[Image.Image, ...], labels: tuple[str, ...]) -> Image.Image:
    thumb_size = (240, 426)
    columns = 3
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_size[0], rows * (thumb_size[1] + 28)), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)
    for index, image in enumerate(images):
        thumb = image.resize(thumb_size, Image.Resampling.LANCZOS)
        x = (index % columns) * thumb_size[0]
        y = (index // columns) * (thumb_size[1] + 28)
        sheet.paste(thumb, (x, y + 28))
        draw.text((x + 8, y + 8), labels[index], fill=(235, 235, 235), font=ImageFont.load_default())
    return sheet


if __name__ == "__main__":
    main()
