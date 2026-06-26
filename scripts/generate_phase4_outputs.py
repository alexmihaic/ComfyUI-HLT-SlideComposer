from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from hlt_slide.config import CanvasSize
from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack


OUTPUT_DIR = Path("examples/outputs")


def synthetic_photo(size: tuple[int, int] = (900, 520), seed: int = 1) -> Image.Image:
    image = Image.new("RGB", size, (20, 20, 20))
    draw = ImageDraw.Draw(image)
    colors = [
        ((230, 48, 48), (40, 80, 220)),
        ((40, 190, 90), (230, 220, 40)),
        ((40, 160, 230), (230, 60, 160)),
        ((220, 120, 40), (70, 220, 220)),
    ]
    top, bottom = colors[(seed - 1) % len(colors)]
    for y in range(size[1]):
        mix = y / max(1, size[1] - 1)
        color = tuple(round(top[channel] * (1 - mix) + bottom[channel] * mix) for channel in range(3))
        draw.line((0, y, size[0], y), fill=color)
    draw.rectangle((8, 8, size[0] - 9, size[1] - 9), outline=(255, 255, 255), width=4)
    draw.text((size[0] // 2 - 8, size[1] // 2 - 8), str(seed), fill=(255, 255, 255))
    return image


def synthetic_background(size: tuple[int, int] = (720, 1280)) -> Image.Image:
    image = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(image)
    for y in range(size[1]):
        mix = y / max(1, size[1] - 1)
        color = (
            round(35 + 100 * mix),
            round(70 + 40 * (1 - mix)),
            round(120 + 80 * mix),
        )
        draw.line((0, y, size[0], y), fill=color)
    for x in range(0, size[0], 80):
        draw.line((x, 0, x, size[1]), fill=(255, 255, 255), width=1)
    return image


def synthetic_logo(alpha: bool = True) -> Image.Image:
    mode = "RGBA" if alpha else "RGB"
    image = Image.new(mode, (420, 160), (0, 0, 0, 0) if alpha else (233, 33, 36))
    draw = ImageDraw.Draw(image)
    fill = (233, 33, 36, 255) if alpha else (233, 33, 36)
    draw.rounded_rectangle((20, 20, 400, 140), radius=36, fill=fill)
    draw.text((155, 68), "HLT", fill=(255, 255, 255, 255) if alpha else (255, 255, 255))
    return image


def synthetic_mask(size: tuple[int, int] = (420, 160), inverted_source: bool = False) -> Image.Image:
    mask = Image.new("L", size, 255 if inverted_source else 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((40, 10, size[0] - 40, size[1] - 10), fill=0 if inverted_source else 255)
    return mask


def save(name: str, image: Image.Image) -> None:
    path = OUTPUT_DIR / name
    image.save(path)
    assert image.mode == "RGB"
    print(path)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    items = [
        SlideItem(synthetic_photo(seed=1), "REF0"),
        SlideItem(synthetic_photo((520, 900), seed=2), "REF1"),
        SlideItem(synthetic_photo(seed=3), "RESULTADO"),
    ]
    background = synthetic_background()

    save(
        "phase4_background_cover.png",
        render_vertical_stack(
            [items[0]],
            title="BACKGROUND COVER",
            background_image=background,
            settings=RenderSettings(background_mode="image", background_fit="cover"),
        ),
    )
    save(
        "phase4_background_contain.png",
        render_vertical_stack(
            [items[0]],
            title="BACKGROUND CONTAIN",
            background_image=background,
            settings=RenderSettings(background_mode="image", background_fit="contain", background_color="#111111"),
        ),
    )
    save(
        "phase4_background_overlay.png",
        render_vertical_stack(
            [items[0]],
            title="BACKGROUND OVERLAY",
            background_image=background,
            settings=RenderSettings(background_mode="image_with_overlay", background_color="#000000", overlay_opacity=0.55),
        ),
    )
    save(
        "phase4_background_opacity.png",
        render_vertical_stack(
            [items[0]],
            title="BACKGROUND OPACITY",
            background_image=background,
            settings=RenderSettings(background_mode="image", background_color="#000000", background_opacity=0.35),
        ),
    )
    save(
        "phase4_logo_opaque.png",
        render_vertical_stack(
            [items[0]],
            title="LOGO OPAQUE",
            logo_image=synthetic_logo(alpha=False),
            settings=RenderSettings(logo_width_percent=24),
        ),
    )
    save(
        "phase4_logo_rgba.png",
        render_vertical_stack(
            [items[0]],
            title="LOGO RGBA",
            logo_image=synthetic_logo(alpha=True),
            settings=RenderSettings(logo_width_percent=24),
        ),
    )
    save(
        "phase4_logo_mask_direct.png",
        render_vertical_stack(
            [items[0]],
            title="MASK DIRECT",
            logo_image=synthetic_logo(alpha=False),
            logo_mask=synthetic_mask(inverted_source=False),
            settings=RenderSettings(logo_width_percent=24, invert_logo_mask=False),
        ),
    )
    save(
        "phase4_logo_mask_inverted.png",
        render_vertical_stack(
            [items[0]],
            title="MASK INVERTED",
            logo_image=synthetic_logo(alpha=False),
            logo_mask=synthetic_mask(inverted_source=True),
            settings=RenderSettings(logo_width_percent=24, invert_logo_mask=True),
        ),
    )
    save(
        "phase4_logo_scaled.png",
        render_vertical_stack(
            [items[0]],
            title="LOGO SCALED",
            logo_image=synthetic_logo(alpha=True),
            settings=RenderSettings(logo_width_percent=60, logo_max_height_percent=5),
        ),
    )
    complete_settings = RenderSettings(
        background_mode="image_with_overlay",
        background_color="#000000",
        overlay_opacity=0.45,
        reserve_footer=True,
        footer_height=150,
        logo_width_percent=20,
        debug_layout=False,
    )
    save(
        "phase4_complete_slide.png",
        render_vertical_stack(
            items,
            title="REFERENCIAS Y RESULTADO",
            background_image=background,
            logo_image=synthetic_logo(alpha=True),
            settings=complete_settings,
        ),
    )
    save(
        "phase4_complete_slide_debug.png",
        render_vertical_stack(
            items,
            title="REFERENCIAS Y RESULTADO",
            background_image=background,
            logo_image=synthetic_logo(alpha=True),
            settings=RenderSettings(
                background_mode="image_with_overlay",
                background_color="#000000",
                overlay_opacity=0.45,
                reserve_footer=True,
                footer_height=150,
                logo_width_percent=20,
                debug_layout=True,
            ),
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
