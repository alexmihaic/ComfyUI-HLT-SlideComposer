from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from hlt_slide.config import CanvasSize
from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack


OUTPUT_DIR = Path("examples/outputs")


def synthetic_image(index: int, size: tuple[int, int]) -> Image.Image:
    palettes = [
        ((235, 45, 48), (40, 85, 225)),
        ((45, 190, 90), (235, 220, 45)),
        ((45, 165, 235), (230, 65, 160)),
        ((225, 125, 45), (70, 220, 220)),
    ]
    top, bottom = palettes[(index - 1) % len(palettes)]
    image = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(image)
    for y in range(size[1]):
        mix = y / max(1, size[1] - 1)
        color = tuple(round(top[channel] * (1 - mix) + bottom[channel] * mix) for channel in range(3))
        draw.line((0, y, size[0], y), fill=color)
    for offset in range(0, max(size), 72):
        draw.line((offset, 0, 0, offset), fill=(255, 255, 255), width=2)
    draw.rectangle((10, 10, size[0] - 11, size[1] - 11), outline=(255, 255, 255), width=5)
    draw.text((size[0] // 2 - 16, size[1] // 2 - 16), str(index), fill=(255, 255, 255))
    return image


def synthetic_background(size: tuple[int, int] = (900, 1600)) -> Image.Image:
    image = Image.new("RGB", size, (20, 20, 20))
    draw = ImageDraw.Draw(image)
    for y in range(size[1]):
        mix = y / max(1, size[1] - 1)
        color = (
            round(30 + 80 * mix),
            round(55 + 55 * (1 - mix)),
            round(115 + 60 * mix),
        )
        draw.line((0, y, size[0], y), fill=color)
    for x in range(0, size[0], 90):
        draw.line((x, 0, x, size[1]), fill=(180, 180, 180), width=1)
    for y in range(0, size[1], 90):
        draw.line((0, y, size[0], y), fill=(180, 180, 180), width=1)
    return image


def synthetic_logo() -> Image.Image:
    image = Image.new("RGBA", (420, 150), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((20, 20, 400, 130), radius=32, fill=(233, 33, 36, 210))
    draw.text((155, 64), "HLT", fill=(255, 255, 255, 255))
    return image


def make_items(count: int, *, long_labels: bool = False) -> list[SlideItem]:
    sizes = [(920, 520), (520, 920), (840, 640), (560, 900)]
    labels = ["REF 1", "REF 2", "RESULT", "ALT"]
    if long_labels:
        labels = [
            "REFERENCE IMAGE WITH A LONG LABEL",
            "SECOND SOURCE WITH EXTRA DETAILS",
            "OUTPUT VERSION WITH LONG DESCRIPTION",
            "ALTERNATIVE VARIANT LABEL",
        ]
    return [
        SlideItem(synthetic_image(index + 1, sizes[index]), labels[index])
        for index in range(count)
    ]


def save(name: str, image: Image.Image) -> Path:
    path = OUTPUT_DIR / name
    image.save(path)
    assert image.mode == "RGB"
    print(path)
    return path


def make_contact_sheet(paths: list[Path]) -> Image.Image:
    thumb_width = 220
    thumb_height = 390
    columns = 4
    rows = (len(paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_width, rows * (thumb_height + 28)), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        x = (index % columns) * thumb_width + (thumb_width - image.width) // 2
        y = (index // columns) * (thumb_height + 28)
        sheet.paste(image, (x, y))
        draw.text((index % columns * thumb_width + 6, y + image.height + 4), path.name, fill=(230, 230, 230))
    return sheet


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    background = synthetic_background()
    logo = synthetic_logo()
    outputs: list[Path] = []

    for count in (1, 2, 3, 4):
        outputs.append(
            save(
                f"phase5_grid_{count}_image{'s' if count > 1 else ''}.png",
                render_vertical_stack(
                    make_items(count),
                    title=f"GRID {count}",
                    settings=RenderSettings(layout="grid_2x2", corner_radius=18),
                ),
            )
        )

    outputs.append(
        save(
            "phase5_grid_long_labels.png",
            render_vertical_stack(
                make_items(4, long_labels=True),
                title="LONG GRID LABELS",
                settings=RenderSettings(layout="grid_2x2", max_label_lines=2, label_font_size=30),
            ),
        )
    )
    outputs.append(
        save(
            "phase5_grid_background_logo.png",
            render_vertical_stack(
                make_items(4),
                title="BACKGROUND + LOGO",
                background_image=background,
                logo_image=logo,
                settings=RenderSettings(
                    layout="grid_2x2",
                    background_mode="image_with_overlay",
                    background_color="#000000",
                    overlay_opacity=0.45,
                    logo_width_percent=22,
                ),
            ),
        )
    )
    outputs.append(
        save(
            "phase5_grid_square.png",
            render_vertical_stack(
                make_items(4),
                title="SQUARE GRID",
                canvas_size=CanvasSize(1080, 1080),
                settings=RenderSettings(layout="grid_2x2", label_font_size=28),
            ),
        )
    )
    outputs.append(
        save(
            "phase5_grid_3x4.png",
            render_vertical_stack(
                make_items(3),
                title="EDITORIAL GRID",
                canvas_size=CanvasSize(1536, 2048),
                settings=RenderSettings(layout="grid_2x2"),
            ),
        )
    )
    outputs.append(
        save(
            "phase5_grid_debug.png",
            render_vertical_stack(
                make_items(4),
                title="GRID DEBUG",
                logo_image=logo,
                settings=RenderSettings(layout="grid_2x2", debug_layout=True, logo_width_percent=22),
            ),
        )
    )

    for count in (1, 2, 3, 4):
        outputs.append(
            save(
                f"phase5_auto_{count}_image{'s' if count > 1 else ''}.png",
                render_vertical_stack(
                    make_items(count),
                    title=f"AUTO {count}",
                    background_image=background,
                    logo_image=logo if count == 4 else None,
                    settings=RenderSettings(
                        layout="auto_social",
                        background_mode="image_with_overlay",
                        background_color="#000000",
                        overlay_opacity=0.35,
                        logo_width_percent=22,
                    ),
                ),
            )
        )

    save("phase5_review_contact_sheet.png", make_contact_sheet(outputs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
