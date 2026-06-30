from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hlt_slide.config import CanvasSize, Rect
from hlt_slide.text_layouts import (
    TextLayoutSettings,
    active_text_blocks,
    describe_text_layout,
    select_text_layout,
)


OUTPUT_DIR = PROJECT_ROOT / "examples" / "outputs" / "text-layouts"
BACKGROUND = (16, 16, 16)
CONTENT_OUTLINE = (110, 110, 110)
TEXT_COLOR = (238, 238, 238)
ACCENT_COLORS = (
    (233, 33, 36),
    (0, 166, 214),
    (255, 191, 0),
    (111, 207, 151),
)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [
        _render_case(
            "01-centered-statement-9x16.png",
            CanvasSize(1080, 1920),
            ("Una frase editorial",),
            ("headline",),
            "centered_statement",
        ),
        _render_case(
            "02-split-2-portrait.png",
            CanvasSize(1080, 1920),
            ("Titular", "Subtitular"),
            ("headline", "subheadline"),
            "split_2",
        ),
        _render_case(
            "03-split-2-landscape.png",
            CanvasSize(1920, 1080),
            ("Titular", "Subtitular"),
            ("headline", "subheadline"),
            "split_2",
        ),
        _render_case(
            "04-vertical-stack-3.png",
            CanvasSize(1080, 1920),
            ("Manifiesto", "Principio", "Detalle"),
            ("headline", "subheadline", "body"),
            "vertical_stack",
        ),
        _render_case(
            "05-grid-2x2-4.png",
            CanvasSize(1080, 1920),
            ("Uno", "Dos", "Tres", "Cuatro"),
            ("number", "headline", "label", "caption"),
            "grid_2x2",
        ),
        _render_case(
            "06-editorial-quote.png",
            CanvasSize(1080, 1920),
            ("La cita ocupa el espacio principal", "Autor"),
            ("quote", "caption"),
            "editorial_quote",
        ),
        _render_auto_comparison(),
    ]
    _contact_sheet(outputs, OUTPUT_DIR / "review-contact-sheet.png")
    for path in outputs:
        print(path.relative_to(PROJECT_ROOT))
    print((OUTPUT_DIR / "review-contact-sheet.png").relative_to(PROJECT_ROOT))


def _render_case(
    filename: str,
    canvas_size: CanvasSize,
    texts: tuple[str, ...],
    roles: tuple[str, ...],
    requested_layout: str,
    *,
    settings: TextLayoutSettings | None = None,
) -> Path:
    layout = select_text_layout(
        canvas_size,
        active_text_blocks(texts, roles),
        settings or TextLayoutSettings(),
        requested_layout,
    )
    image = _draw_layout(canvas_size, layout)
    output_path = OUTPUT_DIR / filename
    image.save(output_path)
    return output_path


def _render_auto_comparison() -> Path:
    panels = []
    for count in range(1, 5):
        canvas_size = CanvasSize(540, 960)
        texts = tuple(f"Bloque {index}" for index in range(1, count + 1))
        roles = ("headline", "subheadline", "body", "caption")[:count]
        layout = select_text_layout(
            canvas_size,
            active_text_blocks(texts, roles),
            TextLayoutSettings(),
            "auto_text",
        )
        panels.append(_draw_layout(canvas_size, layout).resize((270, 480)))

    output = Image.new("RGB", (540, 960), BACKGROUND)
    output.paste(panels[0], (0, 0))
    output.paste(panels[1], (270, 0))
    output.paste(panels[2], (0, 480))
    output.paste(panels[3], (270, 480))
    output_path = OUTPUT_DIR / "07-auto-text-comparison.png"
    output.save(output_path)
    return output_path


def _draw_layout(canvas_size: CanvasSize, layout) -> Image.Image:
    image = Image.new("RGB", (canvas_size.width, canvas_size.height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    _outline(draw, layout.content_rect, CONTENT_OUTLINE, width=3)
    draw.text((20, 20), layout.effective_layout, fill=TEXT_COLOR)
    draw.text((20, 44), describe_text_layout(layout), fill=TEXT_COLOR)
    for index, block in enumerate(layout.blocks):
        color = ACCENT_COLORS[index % len(ACCENT_COLORS)]
        _outline(draw, block.rect, color, width=5)
        _outline(draw, block.inner_rect, tuple(max(0, value - 70) for value in color), width=2)
        label = (
            f"slot {block.source_index + 1} | {block.role} | "
            f"{block.rect.width}x{block.rect.height}"
        )
        draw.text((block.rect.x + 12, block.rect.y + 12), label, fill=TEXT_COLOR)
    return image


def _outline(draw: ImageDraw.ImageDraw, rect: Rect, color: tuple[int, int, int], *, width: int) -> None:
    draw.rectangle((rect.x, rect.y, rect.right - 1, rect.bottom - 1), outline=color, width=width)


def _contact_sheet(paths: list[Path], output_path: Path) -> None:
    thumbs = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((320, 480))
        panel = Image.new("RGB", (360, 540), (28, 28, 28))
        panel.paste(image, ((360 - image.width) // 2, 20))
        ImageDraw.Draw(panel).text((16, 500), path.name, fill=TEXT_COLOR)
        thumbs.append(panel)

    columns = 4
    rows = 2
    sheet = Image.new("RGB", (columns * 360, rows * 540), BACKGROUND)
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % columns) * 360, (index // columns) * 540))
    sheet.save(output_path)


if __name__ == "__main__":
    main()
