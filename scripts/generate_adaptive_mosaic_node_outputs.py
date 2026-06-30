from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from PIL import Image, ImageDraw, ImageFont

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path("examples") / "outputs" / "adaptive-mosaic-node"
CANVAS = (720, 1280)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    package = load_custom_node_package()
    node = package.NODE_CLASS_MAPPINGS["HLTSlideComposer"]()
    cases = {
        "node-balanced.png": compose_image(node, adaptive_strategy="balanced"),
        "node-editorial.png": compose_image(node, adaptive_strategy="editorial"),
        "node-compact.png": compose_image(node, adaptive_strategy="compact"),
        "node-hero-image-1.png": compose_image(
            node, adaptive_strategy="editorial", adaptive_hero="image_1"
        ),
        "node-background-logo.png": compose_image(
            node,
            adaptive_strategy="balanced",
            background_mode="image_with_overlay",
            background_image=tensor_from_pil(synthetic_background(CANVAS)),
            overlay_opacity=0.35,
            logo_image=tensor_from_pil(synthetic_logo().convert("RGB")),
            logo_mask=logo_mask(),
        ),
        "node-debug.png": compose_image(node, title="DEBUG", debug_layout=True),
    }
    for filename, image in cases.items():
        image.save(OUTPUT_DIR / filename)
    contact_sheet(tuple(cases.values()), tuple(cases.keys())).save(
        OUTPUT_DIR / "review-contact-sheet.png"
    )
    return 0


def load_custom_node_package() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "comfyui_hlt_slide_composer_node_outputs",
        PROJECT_ROOT / "__init__.py",
        submodule_search_locations=[str(PROJECT_ROOT)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create import spec for custom node package.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def compose_image(node, **overrides) -> Image.Image:
    output = node.compose(**kwargs(**overrides))[0]
    array = output.detach().cpu().numpy()[0]
    image = Image.fromarray((array.clip(0.0, 1.0) * 255).round().astype("uint8"), "RGB")
    return image


def kwargs(**overrides):
    base = {
        "image_1": tensor_from_pil(synthetic_ratio_image((480, 480), (206, 68, 80), "1:1")),
        "image_2": tensor_from_pil(synthetic_ratio_image((640, 360), (68, 168, 94), "16:9")),
        "image_3": tensor_from_pil(synthetic_ratio_image((360, 480), (76, 112, 220), "3:4")),
        "image_4": tensor_from_pil(synthetic_ratio_image((360, 640), (230, 168, 66), "9:16")),
        "canvas_preset": "Custom",
        "custom_width": CANVAS[0],
        "custom_height": CANVAS[1],
        "layout": "adaptive_mosaic",
        "background_mode": "solid",
        "background_color": "#111111",
        "background_fit": "cover",
        "background_opacity": 1.0,
        "overlay_opacity": 0.0,
        "title": "NODE ADAPTIVE",
        "label_1": "SQUARE 1:1",
        "label_2": "LANDSCAPE 16:9",
        "label_3": "PORTRAIT 3:4",
        "label_4": "TALL 9:16",
        "title_color": "#E92124",
        "label_color": "#E92124",
        "cell_background_color": "#111111",
        "image_fit": "stretch",
        "contain_fill_mode": "cell_color",
        "crop_anchor": "top",
        "font_path": "",
        "title_font_size": 64,
        "label_font_size": 30,
        "minimum_font_size": 16,
        "max_label_lines": 2,
        "line_spacing": 6,
        "outer_margin": 64,
        "top_margin": 58,
        "bottom_margin": 50,
        "title_gap": 28,
        "block_gap": 30,
        "image_label_gap": 14,
        "inner_padding": 24,
        "corner_radius": 18,
        "border_width": 2,
        "border_color": "#E92124",
        "logo_width_percent": 20.0,
        "logo_max_height_percent": 8.0,
        "logo_opacity": 1.0,
        "logo_bottom_offset": 0,
        "invert_logo_mask": False,
        "uppercase_title": True,
        "uppercase_labels": False,
        "debug_layout": False,
        "label_padding_top": 6,
        "label_padding_bottom": 10,
        "label_after_gap": 20,
        "label_min_height": 32,
        "label_vertical_align": "center",
        "label_clip": True,
        "adaptive_strategy": "balanced",
        "adaptive_hero": "auto",
        "background_image": None,
        "logo_image": None,
        "logo_mask": None,
    }
    base.update(overrides)
    return base


def tensor_from_pil(image: Image.Image) -> torch.Tensor:
    rgb = image.convert("RGB")
    data = torch.ByteTensor(bytearray(rgb.tobytes())).reshape(rgb.height, rgb.width, 3)
    return data.to(dtype=torch.float32).unsqueeze(0) / 255.0


def logo_mask() -> torch.Tensor:
    mask = torch.zeros((1, 90, 220), dtype=torch.float32)
    mask[:, 18:72, 12:208] = 1.0
    return mask


def synthetic_ratio_image(
    size: tuple[int, int],
    color: tuple[int, int, int],
    ratio_label: str,
) -> Image.Image:
    image = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(image)
    width, height = size
    draw.rectangle((4, 4, width - 5, height - 5), outline=(255, 255, 255), width=5)
    draw.rectangle((18, 18, width - 19, height - 19), outline=(0, 0, 0), width=3)
    draw.line((0, 0, width - 1, height - 1), fill=(255, 255, 255), width=4)
    draw.line((0, height - 1, width - 1, 0), fill=(0, 0, 0), width=4)
    draw.text((width // 2 - 18, height // 2 - 6), ratio_label, fill=(255, 255, 255))
    return image


def synthetic_background(size: tuple[int, int]) -> Image.Image:
    image = Image.new("RGB", size, (44, 46, 58))
    draw = ImageDraw.Draw(image)
    for x in range(-size[1], size[0], 44):
        draw.line((x, 0, x + size[1], size[1]), fill=(92, 94, 112), width=4)
    return image


def synthetic_logo() -> Image.Image:
    image = Image.new("RGBA", (220, 90), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((12, 18, 208, 72), radius=18, fill=(233, 33, 36, 230))
    draw.text((76, 38), "HLT", fill=(255, 255, 255, 255), font=ImageFont.load_default())
    return image


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
        draw.text((x + 8, y + 8), labels[index], fill=(235, 235, 235))
    return sheet


if __name__ == "__main__":
    raise SystemExit(main())
