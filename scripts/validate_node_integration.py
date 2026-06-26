from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[1]

import torch


def load_custom_node_package() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "comfyui_hlt_slide_composer",
        PROJECT_ROOT / "__init__.py",
        submodule_search_locations=[str(PROJECT_ROOT)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create import spec for custom node package.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def image(
    color: tuple[float, float, float],
    *,
    size: tuple[int, int] = (32, 24),
    batch: int = 1,
) -> torch.Tensor:
    width, height = size
    tensor = torch.zeros((batch, height, width, 3), dtype=torch.float32, device="cpu")
    tensor[:, :, :, 0] = color[0]
    tensor[:, :, :, 1] = color[1]
    tensor[:, :, :, 2] = color[2]
    return tensor


def mask(*, size: tuple[int, int] = (32, 24), batch: int = 1) -> torch.Tensor:
    width, height = size
    return torch.zeros((batch, height, width), dtype=torch.float32, device="cpu")


def kwargs(**overrides):
    base = {
        "image_1": image((1.0, 0.0, 0.0)),
        "canvas_preset": "Custom",
        "custom_width": 160,
        "custom_height": 240,
        "layout": "vertical_stack",
        "background_mode": "solid",
        "background_color": "#000000",
        "background_fit": "cover",
        "background_opacity": 1.0,
        "overlay_opacity": 0.0,
        "title": "RUNTIME",
        "label_1": "A",
        "label_2": "",
        "label_3": "",
        "label_4": "",
        "title_color": "#E92124",
        "label_color": "#E92124",
        "cell_background_color": "#111111",
        "image_fit": "cover",
        "crop_anchor": "center",
        "font_path": "",
        "title_font_size": 32,
        "label_font_size": 18,
        "minimum_font_size": 10,
        "max_label_lines": 2,
        "line_spacing": 4,
        "outer_margin": 24,
        "top_margin": 24,
        "bottom_margin": 20,
        "title_gap": 12,
        "block_gap": 12,
        "image_label_gap": 6,
        "inner_padding": 12,
        "corner_radius": 0,
        "border_width": 0,
        "border_color": "#E92124",
        "logo_width_percent": 18.0,
        "logo_max_height_percent": 8.0,
        "logo_opacity": 1.0,
        "logo_bottom_offset": 0,
        "invert_logo_mask": True,
        "uppercase_title": True,
        "uppercase_labels": False,
        "debug_layout": False,
    }
    base.update(overrides)
    return base


def assert_image_tensor(tensor: torch.Tensor, size: tuple[int, int]) -> None:
    width, height = size
    assert tuple(tensor.shape) == (1, height, width, 3), tuple(tensor.shape)
    assert tensor.dtype is torch.float32, tensor.dtype
    assert tensor.device.type == "cpu", tensor.device
    assert float(tensor.min()) >= 0.0
    assert float(tensor.max()) <= 1.0


def main() -> int:
    package = load_custom_node_package()
    assert "HLTSlideComposer" in package.NODE_CLASS_MAPPINGS
    assert package.NODE_DISPLAY_NAME_MAPPINGS["HLTSlideComposer"] == "HLT · Slide Composer"

    node_class = package.NODE_CLASS_MAPPINGS["HLTSlideComposer"]
    assert node_class.__module__ == "comfyui_hlt_slide_composer.nodes"
    inputs = node_class.INPUT_TYPES()
    assert inputs["required"]["image_1"] == ("IMAGE",)
    assert inputs["optional"]["logo_mask"] == ("MASK",)
    default_preset = inputs["required"]["canvas_preset"][1]["default"]
    assert default_preset == "9:16 Social · 1080x1920"

    node = node_class()
    default = node.compose(**kwargs(canvas_preset=default_preset))[0]
    assert_image_tensor(default, (1080, 1920))

    custom = node.compose(**kwargs())[0]
    assert_image_tensor(custom, (160, 240))

    background_sized = node.compose(
        **kwargs(
            canvas_preset="Background size",
            background_mode="image",
            background_image=image((0.2, 0.3, 0.5), size=(80, 120)),
        )
    )[0]
    assert_image_tensor(background_sized, (80, 120))

    three = node.compose(
        **kwargs(
            image_2=image((0.0, 1.0, 0.0)),
            image_3=image((0.0, 0.0, 1.0)),
            label_2="B",
            label_3="C",
        )
    )[0]
    assert_image_tensor(three, (160, 240))

    four_auto = node.compose(
        **kwargs(
            image_2=image((0.0, 1.0, 0.0)),
            image_3=image((0.0, 0.0, 1.0)),
            image_4=image((1.0, 1.0, 0.0)),
            layout="auto_social",
            background_mode="image_with_overlay",
            background_image=image((0.2, 0.3, 0.5), size=(80, 120)),
            overlay_opacity=0.25,
            logo_image=image((1.0, 0.0, 0.0), size=(40, 20)),
            logo_mask=mask(size=(40, 20)),
        )
    )[0]
    assert_image_tensor(four_auto, (160, 240))

    print("HLT Comfy node integration validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
