from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from hlt_slide.config import CanvasSize
from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack


OUTPUT_DIR = Path("examples/outputs")


def synthetic_image(index: int, size: tuple[int, int]) -> Image.Image:
    colors = [
        ((230, 48, 48), (40, 80, 220)),
        ((40, 190, 90), (230, 220, 40)),
        ((40, 160, 230), (230, 60, 160)),
        ((220, 120, 40), (70, 220, 220)),
    ]
    top, bottom = colors[(index - 1) % len(colors)]
    image = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(image)
    for y in range(size[1]):
        mix = y / max(1, size[1] - 1)
        color = tuple(round(top[channel] * (1 - mix) + bottom[channel] * mix) for channel in range(3))
        draw.line((0, y, size[0], y), fill=color)
    draw.rectangle((8, 8, size[0] - 9, size[1] - 9), outline=(255, 255, 255), width=4)
    draw.text((size[0] // 2 - 12, size[1] // 2 - 12), str(index), fill=(255, 255, 255))
    return image


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = {
        "phase3_vertical_1_image.png": (
            [SlideItem(synthetic_image(1, (900, 520)), "REF 1")],
            "UNA IMAGEN",
            CanvasSize(1080, 1920),
            RenderSettings(),
        ),
        "phase3_vertical_2_images.png": (
            [
                SlideItem(synthetic_image(1, (900, 520)), "HORIZONTAL"),
                SlideItem(synthetic_image(2, (520, 900)), "VERTICAL"),
            ],
            "DOS IMAGENES",
            CanvasSize(1080, 1920),
            RenderSettings(),
        ),
        "phase3_vertical_3_images.png": (
            [
                SlideItem(synthetic_image(1, (900, 520)), "REF0"),
                SlideItem(synthetic_image(2, (520, 900)), "REF1"),
                SlideItem(synthetic_image(3, (900, 520)), "RESULTADO"),
            ],
            "REFERENCIAS Y RESULTADO",
            CanvasSize(1080, 1920),
            RenderSettings(),
        ),
        "phase3_vertical_4_images.png": (
            [
                SlideItem(synthetic_image(1, (900, 520)), "A"),
                SlideItem(synthetic_image(2, (520, 900)), "B"),
                SlideItem(synthetic_image(3, (900, 520)), "C"),
                SlideItem(synthetic_image(4, (520, 900)), "D"),
            ],
            "CUATRO IMAGENES",
            CanvasSize(1080, 1920),
            RenderSettings(label_font_size=30),
        ),
        "phase3_vertical_long_title.png": (
            [SlideItem(synthetic_image(1, (900, 520)), "RESULTADO")],
            "TITULO MUY LARGO PARA COMPROBAR AJUSTE AUTOMATICO",
            CanvasSize(1080, 1920),
            RenderSettings(),
        ),
        "phase3_vertical_long_labels.png": (
            [
                SlideItem(synthetic_image(1, (900, 520)), "ETIQUETA MUY LARGA DE REFERENCIA PRODUCTO"),
                SlideItem(synthetic_image(2, (520, 900)), "ETIQUETA MUY LARGA DE RESULTADO FINAL"),
            ],
            "ETIQUETAS LARGAS",
            CanvasSize(1080, 1920),
            RenderSettings(max_label_lines=2),
        ),
        "phase3_vertical_footer_reserved.png": (
            [SlideItem(synthetic_image(1, (900, 520)), "CON FOOTER")],
            "FOOTER RESERVADO",
            CanvasSize(1080, 1920),
            RenderSettings(reserve_footer=True, footer_height=140),
        ),
        "phase3_vertical_debug.png": (
            [
                SlideItem(synthetic_image(1, (900, 520)), "REF0"),
                SlideItem(synthetic_image(2, (520, 900)), "REF1"),
                SlideItem(synthetic_image(3, (900, 520)), "RESULTADO"),
            ],
            "DEBUG",
            CanvasSize(1080, 1920),
            RenderSettings(reserve_footer=True, footer_height=140, debug_layout=True),
        ),
        "phase3_vertical_3x4.png": (
            [
                SlideItem(synthetic_image(1, (900, 520)), "REF0"),
                SlideItem(synthetic_image(2, (520, 900)), "REF1"),
                SlideItem(synthetic_image(3, (900, 520)), "RESULTADO"),
            ],
            "FORMATO 3:4",
            CanvasSize(1536, 2048),
            RenderSettings(),
        ),
    }
    for name, (items, title, size, settings) in cases.items():
        image = render_vertical_stack(items, title=title, canvas_size=size, settings=settings)
        path = OUTPUT_DIR / name
        image.save(path)
        assert image.mode == "RGB"
        assert image.size == (size.width, size.height)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
