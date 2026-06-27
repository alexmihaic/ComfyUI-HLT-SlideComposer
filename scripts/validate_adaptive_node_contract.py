from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_custom_node_package() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "comfyui_hlt_slide_composer_adaptive_validation",
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
    size: tuple[int, int],
) -> torch.Tensor:
    width, height = size
    tensor = torch.zeros((1, height, width, 3), dtype=torch.float32, device="cpu")
    tensor[:, :, :, 0] = color[0]
    tensor[:, :, :, 1] = color[1]
    tensor[:, :, :, 2] = color[2]
    tensor[:, 0:2, :, :] = 1.0
    tensor[:, -2:, :, :] = 1.0
    tensor[:, :, 0:2, :] = 1.0
    tensor[:, :, -2:, :] = 1.0
    return tensor


def mask(*, size: tuple[int, int]) -> torch.Tensor:
    width, height = size
    tensor = torch.ones((1, height, width), dtype=torch.float32, device="cpu")
    tensor[:, 0:2, :] = 0.0
    tensor[:, -2:, :] = 0.0
    return tensor


def kwargs(**overrides):
    base = {
        "image_1": image((1.0, 0.0, 0.0), size=(40, 40)),
        "canvas_preset": "Custom",
        "custom_width": 240,
        "custom_height": 360,
        "layout": "adaptive_mosaic",
        "background_mode": "solid",
        "background_color": "#000000",
        "background_fit": "cover",
        "background_opacity": 1.0,
        "overlay_opacity": 0.0,
        "title": "ADAPTIVE",
        "label_1": "SQUARE",
        "label_2": "LANDSCAPE",
        "label_3": "PORTRAIT",
        "label_4": "TALL",
        "title_color": "#E92124",
        "label_color": "#E92124",
        "cell_background_color": "#111111",
        "image_fit": "stretch",
        "contain_fill_mode": "cell_color",
        "crop_anchor": "top",
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
        "corner_radius": 4,
        "border_width": 1,
        "border_color": "#E92124",
        "logo_width_percent": 18.0,
        "logo_max_height_percent": 8.0,
        "logo_opacity": 1.0,
        "logo_bottom_offset": 0,
        "invert_logo_mask": True,
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
    node_class = package.NODE_CLASS_MAPPINGS["HLTSlideComposer"]
    required = node_class.INPUT_TYPES()["required"]
    assert "adaptive_mosaic" in required["layout"][0]
    assert required["layout"][1]["default"] == "vertical_stack"
    assert required["adaptive_strategy"][0] == ("balanced", "editorial", "compact")
    assert required["adaptive_strategy"][1]["default"] == "balanced"
    assert required["adaptive_hero"][0] == ("auto", "image_1", "image_2", "image_3", "image_4")
    assert required["adaptive_hero"][1]["default"] == "auto"
    assert list(required)[-2:] == ["adaptive_strategy", "adaptive_hero"]
    for layout in ("vertical_stack", "grid_2x2", "auto_social", "adaptive_mosaic"):
        assert layout in required["layout"][0]

    node = node_class()
    output = node.compose(
        **kwargs(
            image_2=image((0.0, 1.0, 0.0), size=(64, 36)),
            image_3=image((0.0, 0.0, 1.0), size=(36, 48)),
            image_4=image((1.0, 1.0, 0.0), size=(36, 64)),
            background_mode="image_with_overlay",
            background_image=image((0.2, 0.3, 0.5), size=(240, 360)),
            overlay_opacity=0.25,
            logo_image=image((1.0, 0.0, 0.0), size=(40, 20)),
            logo_mask=mask(size=(40, 20)),
            debug_layout=True,
        )
    )[0]
    assert_image_tensor(output, (240, 360))
    print("HLT adaptive node contract validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
