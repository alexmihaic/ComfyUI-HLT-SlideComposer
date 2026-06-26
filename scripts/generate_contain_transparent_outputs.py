from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from hlt_slide.config import CanvasSize
from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "examples" / "outputs"


def make_background(size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (round(35 + 90 * ratio), round(30 + 30 * ratio), round(140 + 80 * (1 - ratio)))
        draw.line((0, y, width, y), fill=color)
    for x in range(0, width, 80):
        draw.line((x, 0, x, height), fill=(230, 50, 60), width=2)
    for y in range(0, height, 80):
        draw.line((0, y, width, y), fill=(20, 180, 220), width=2)
    return image


def make_content(size: tuple[int, int], text: str, color: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(image)
    width, height = size
    draw.rectangle((0, 0, width - 1, height - 1), outline=(255, 255, 255), width=8)
    draw.line((0, 0, width, height), fill=(0, 0, 0), width=6)
    draw.line((0, height, width, 0), fill=(0, 0, 0), width=6)
    draw.text((width // 2 - 18, height // 2 - 12), text, fill=(255, 255, 255))
    return image


def make_logo() -> Image.Image:
    logo = Image.new("RGBA", (320, 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    draw.rounded_rectangle((6, 6, 314, 114), radius=30, fill=(255, 255, 255, 210))
    draw.text((86, 48), "HLT", fill=(233, 33, 36, 255))
    return logo


def render_case(
    name: str,
    *,
    layout: str = "vertical_stack",
    background_mode: str = "image",
    contain_fill_mode: str = "transparent",
    overlay_opacity: float = 0.0,
    logo: bool = False,
) -> Image.Image:
    canvas_size = CanvasSize(540, 960)
    items = [
        SlideItem(make_content((480, 160), "1", (210, 35, 60)), "wide image"),
        SlideItem(make_content((160, 420), "2", (35, 150, 210)), "tall image"),
        SlideItem(make_content((360, 240), "3", (70, 175, 80)), "mixed image"),
        SlideItem(make_content((260, 260), "4", (200, 140, 35)), "square image"),
    ]
    if layout != "grid_2x2":
        items = items[:1]
    settings = RenderSettings(
        canvas_preset="Custom",
        background_mode=background_mode,
        background_color="#101820",
        background_fit="cover",
        overlay_opacity=overlay_opacity,
        title_font_size=36,
        label_font_size=22,
        minimum_font_size=12,
        outer_margin=42,
        top_margin=42,
        bottom_margin=36,
        title_gap=22,
        block_gap=20,
        image_label_gap=8,
        inner_padding=18,
        image_fit="contain",
        contain_fill_mode=contain_fill_mode,
        cell_background_color="#111111",
        corner_radius=20,
        border_width=3,
        layout=layout,
        reserve_footer=logo,
        footer_height=72,
    )
    return render_vertical_stack(
        items,
        title=name,
        canvas_size=canvas_size,
        settings=settings,
        background_image=make_background((540, 960)),
        logo_image=make_logo() if logo else None,
    )


def build_contact_sheet(before: Image.Image, after: Image.Image) -> Image.Image:
    width = before.width + after.width + 48
    height = before.height + 96
    sheet = Image.new("RGB", (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 26), "ANTES · CELL COLOR", fill=(255, 255, 255))
    draw.text((before.width + 48, 26), "DESPUES · TRANSPARENT", fill=(255, 255, 255))
    sheet.paste(before, (16, 72))
    sheet.paste(after, (before.width + 32, 72))
    return sheet


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "contain_transparent_solid_background.png": render_case(
            "SOLID BACKGROUND",
            background_mode="solid",
            contain_fill_mode="transparent",
        ),
        "contain_transparent_image_background.png": render_case(
            "IMAGE BACKGROUND",
            background_mode="image",
            contain_fill_mode="transparent",
        ),
        "contain_transparent_overlay_background.png": render_case(
            "OVERLAY BACKGROUND",
            background_mode="image_with_overlay",
            contain_fill_mode="transparent",
            overlay_opacity=0.45,
        ),
        "contain_cell_color.png": render_case(
            "CELL COLOR",
            background_mode="image",
            contain_fill_mode="cell_color",
        ),
        "contain_transparent_grid.png": render_case(
            "GRID TRANSPARENT",
            layout="grid_2x2",
            background_mode="image_with_overlay",
            contain_fill_mode="transparent",
            overlay_opacity=0.30,
            logo=True,
        ),
    }
    before = outputs["contain_cell_color.png"]
    after = outputs["contain_transparent_image_background.png"]
    outputs["contain_transparent_comparison_sheet.png"] = build_contact_sheet(before, after)

    for filename, image in outputs.items():
        image.save(OUTPUT_DIR / filename)
        print(OUTPUT_DIR / filename)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
