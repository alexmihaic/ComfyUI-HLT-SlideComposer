from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hlt_slide.config import CanvasSize
from hlt_slide.text_renderer import TextRenderSettings, render_text_composition


OUTPUT_DIR = PROJECT_ROOT / "examples" / "outputs" / "text-composer-rendered"
TEXT_COLOR = (243, 240, 232)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [
        _save(
            "01-centered-statement-9x16.png",
            render_text_composition(
                ("PENSAR CON\nMÁS CONTEXTO",),
                roles=("headline",),
                settings=TextRenderSettings(layout="centered_statement", accent_target="first_active"),
            ),
        ),
        _save(
            "02-split-portrait.png",
            render_text_composition(
                ("NO ES GENERAR MÁS", "ES DECIDIR MEJOR"),
                roles=("headline", "headline"),
                settings=TextRenderSettings(layout="split_2"),
            ),
        ),
        _save(
            "03-split-landscape.png",
            render_text_composition(
                ("NO ES GENERAR MÁS", "ES DECIDIR MEJOR"),
                roles=("headline", "headline"),
                canvas_size=CanvasSize(1920, 1080),
                settings=TextRenderSettings(layout="split_2", accent_target="text_2"),
            ),
        ),
        _save(
            "04-vertical-manifest.png",
            render_text_composition(
                ("PRIMERO MIRAR", "DESPUÉS PENSAR", "LUEGO CREAR"),
                roles=("headline", "headline", "headline"),
                settings=TextRenderSettings(layout="vertical_stack"),
            ),
        ),
        _save(
            "05-grid-concepts.png",
            render_text_composition(
                ("CONTEXTO", "CRITERIO", "DIRECCIÓN", "EJECUCIÓN"),
                roles=("headline", "headline", "headline", "headline"),
                settings=TextRenderSettings(layout="grid_2x2", accent_target="text_1"),
            ),
        ),
        _save(
            "06-editorial-quote.png",
            render_text_composition(
                ("LA HERRAMIENTA\nNO SUSTITUYE\nEL CRITERIO.", "HAZ LO TUYO"),
                roles=("quote", "caption"),
                settings=TextRenderSettings(layout="editorial_quote", accent_target="text_2"),
            ),
        ),
        _save(
            "07-background-overlay-logo.png",
            render_text_composition(
                ("SISTEMA", "FONDO SINTÉTICO\nCON LOGO"),
                roles=("headline", "body"),
                background_image=_synthetic_background(),
                logo_image=_synthetic_logo(),
                settings=TextRenderSettings(
                    layout="split_2",
                    background_mode="image_with_overlay",
                    background_color="#000000",
                    overlay_opacity=0.42,
                    reserve_logo_space=True,
                ),
            ),
        ),
        _save(
            "08-accent-targets.png",
            render_text_composition(
                ("UNO", "DOS", "TRES", "CUATRO"),
                roles=("headline", "headline", "headline", "headline"),
                settings=TextRenderSettings(layout="grid_2x2", accent_target="text_3"),
            ),
        ),
        _save(
            "09-debug-layout.png",
            render_text_composition(
                ("DEBUG", "RECTÁNGULOS\nY FITTING", "TRUNCADO " * 20),
                roles=("headline", "subheadline", "caption"),
                logo_image=_synthetic_logo(),
                settings=TextRenderSettings(
                    layout="auto_text",
                    debug_layout=True,
                    reserve_logo_space=True,
                    accent_target="first_active",
                    font_scale=1.1,
                ),
            ),
        ),
        _save(
            "10-long-word-and-wrapping.png",
            render_text_composition(
                ("GENERAR\nCONTEXTO\nCRITERIO\nEXTRAORDINARIAMENTEEXTRAORDINARIAMENTE",),
                roles=("headline",),
                settings=TextRenderSettings(
                    layout="centered_statement",
                    warn_on_truncation=True,
                    accent_target="first_active",
                ),
            ),
        ),
    ]
    _contact_sheet(outputs, OUTPUT_DIR / "review-contact-sheet.png")
    for path in outputs:
        print(path.relative_to(PROJECT_ROOT))
    print((OUTPUT_DIR / "review-contact-sheet.png").relative_to(PROJECT_ROOT))


def _save(filename: str, image: Image.Image) -> Path:
    path = OUTPUT_DIR / filename
    image.save(path)
    return path


def _synthetic_background() -> Image.Image:
    image = Image.new("RGB", (960, 1440), (18, 34, 48))
    draw = ImageDraw.Draw(image)
    for index in range(0, image.height, 80):
        color = (18 + (index // 8) % 80, 42, 72)
        draw.rectangle((0, index, image.width, index + 40), fill=color)
    draw.rectangle((120, 180, 840, 1260), outline=(233, 33, 36), width=12)
    draw.line((0, image.height, image.width, 0), fill=(243, 240, 232), width=6)
    return image


def _synthetic_logo() -> Image.Image:
    image = Image.new("RGBA", (240, 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((12, 12, 228, 108), radius=24, fill=(233, 33, 36, 255))
    draw.rectangle((62, 36, 178, 84), fill=(243, 240, 232, 255))
    return image


def _contact_sheet(paths: list[Path], output_path: Path) -> None:
    columns = 5
    thumb_w = 300
    thumb_h = 460
    rows = 2
    sheet = Image.new("RGB", (columns * thumb_w, rows * thumb_h), (20, 20, 20))
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w - 24, thumb_h - 54))
        panel = Image.new("RGB", (thumb_w, thumb_h), (30, 30, 30))
        panel.paste(image, ((thumb_w - image.width) // 2, 12))
        ImageDraw.Draw(panel).text((12, thumb_h - 34), path.name, fill=TEXT_COLOR)
        sheet.paste(panel, ((index % columns) * thumb_w, (index // columns) * thumb_h))
    sheet.save(output_path)


if __name__ == "__main__":
    main()
