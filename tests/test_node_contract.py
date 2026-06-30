from __future__ import annotations

import importlib.abc
import importlib
import importlib.util
import sys
import types
from pathlib import Path

from hlt_slide.config import CanvasSize, RESOLUTION_PRESETS, resolve_canvas_size


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class _BlockTopLevelHltSlide(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path: object = None, target: object = None) -> None:
        if fullname == "hlt_slide" or fullname.startswith("hlt_slide."):
            raise ModuleNotFoundError("blocked top-level hlt_slide")
        return None


def _load_as_comfyui_package(package_name: str):
    spec = importlib.util.spec_from_file_location(
        package_name,
        PROJECT_ROOT / "__init__.py",
        submodule_search_locations=[str(PROJECT_ROOT)],
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _clear_temp_package(package_name: str) -> None:
    for module_name in tuple(sys.modules):
        if module_name == package_name or module_name.startswith(f"{package_name}."):
            sys.modules.pop(module_name, None)


def test_root_package_loads_internal_nodes_without_top_level_hlt_slide() -> None:
    package_name = "comfyui_hlt_slide_composer_test"
    blocker = _BlockTopLevelHltSlide()
    saved_hlt_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "hlt_slide" or name.startswith("hlt_slide.")
    }
    saved_nodes_module = sys.modules.get("nodes")
    for module_name in saved_hlt_modules:
        sys.modules.pop(module_name, None)
    fake_nodes = types.ModuleType("nodes")
    fake_nodes.NODE_CLASS_MAPPINGS = {}
    fake_nodes.NODE_DISPLAY_NAME_MAPPINGS = {}
    sys.modules["nodes"] = fake_nodes
    sys.meta_path.insert(0, blocker)
    try:
        module = _load_as_comfyui_package(package_name)

        assert set(module.NODE_CLASS_MAPPINGS) == {"HLTSlideComposer"}
        assert module.NODE_DISPLAY_NAME_MAPPINGS == {
            "HLTSlideComposer": "HLT · Slide Composer"
        }
        node_class = module.NODE_CLASS_MAPPINGS["HLTSlideComposer"]
        assert node_class.__name__ == "HLTSlideComposer"
        assert node_class.__module__ == f"{package_name}.nodes"
    finally:
        sys.meta_path.remove(blocker)
        _clear_temp_package(package_name)
        sys.modules.pop("nodes", None)
        if saved_nodes_module is not None:
            sys.modules["nodes"] = saved_nodes_module
        sys.modules.update(saved_hlt_modules)


def test_node_module_exports_class_and_mappings() -> None:
    node_module = importlib.import_module("nodes")

    assert hasattr(node_module, "HLTSlideComposer")
    assert node_module.NODE_CLASS_MAPPINGS == {"HLTSlideComposer": node_module.HLTSlideComposer}
    assert node_module.NODE_DISPLAY_NAME_MAPPINGS == {
        "HLTSlideComposer": "HLT · Slide Composer"
    }
    assert not hasattr(node_module, "WEB_DIRECTORY")


def test_root_init_exports_only_comfyui_mappings() -> None:
    package_name = "hlt_slide_composer_root"
    try:
        module = _load_as_comfyui_package(package_name)

        assert module.NODE_CLASS_MAPPINGS
        assert module.NODE_DISPLAY_NAME_MAPPINGS
        assert module.__all__ == ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
        assert not hasattr(module, "WEB_DIRECTORY")
    finally:
        _clear_temp_package(package_name)


def test_input_types_define_required_optional_and_defaults() -> None:
    node_module = importlib.import_module("nodes")
    inputs = node_module.HLTSlideComposer.INPUT_TYPES()
    required = inputs["required"]
    optional = inputs["optional"]

    assert required["image_1"] == ("IMAGE",)
    for name in ("image_2", "image_3", "image_4", "background_image", "logo_image"):
        assert optional[name] == ("IMAGE",)
    assert optional["logo_mask"] == ("MASK",)

    preset_names = tuple(preset.name for preset in RESOLUTION_PRESETS)
    assert required["canvas_preset"][0] == preset_names
    assert required["canvas_preset"][1]["default"] == "9:16 Social · 1080x1920"
    assert required["layout"][0] == (
        "vertical_stack",
        "grid_2x2",
        "auto_social",
        "adaptive_mosaic",
    )
    assert required["layout"][1]["default"] == "vertical_stack"
    assert required["adaptive_strategy"][0] == ("balanced", "editorial", "compact")
    assert required["adaptive_strategy"][1]["default"] == "balanced"
    assert required["adaptive_hero"][0] == (
        "auto",
        "image_1",
        "image_2",
        "image_3",
        "image_4",
    )
    assert required["adaptive_hero"][1]["default"] == "auto"
    assert required["background_color"][1]["default"] == "#000000"
    assert required["title_color"][1]["default"] == "#E92124"
    assert required["label_color"][1]["default"] == "#E92124"
    assert required["contain_fill_mode"][0] == ("transparent", "cell_color")
    assert required["contain_fill_mode"][1]["default"] == "transparent"
    assert required["debug_layout"][1]["default"] is False
    assert list(required)[-8:] == [
        "label_padding_top",
        "label_padding_bottom",
        "label_after_gap",
        "label_min_height",
        "label_vertical_align",
        "label_clip",
        "adaptive_strategy",
        "adaptive_hero",
    ]
    assert required["label_padding_top"][1] == {"default": 6, "min": 0, "max": 256, "step": 1}
    assert required["label_padding_bottom"][1] == {"default": 10, "min": 0, "max": 256, "step": 1}
    assert required["label_after_gap"][1] == {"default": 20, "min": 0, "max": 512, "step": 1}
    assert required["label_min_height"][1] == {"default": 32, "min": 0, "max": 512, "step": 1}
    assert required["label_vertical_align"][0] == ("top", "center", "bottom")
    assert required["label_vertical_align"][1]["default"] == "center"
    assert required["label_clip"][1]["default"] is True


def test_complete_required_widget_order_is_stable() -> None:
    node_module = importlib.import_module("nodes")
    required = node_module.HLTSlideComposer.INPUT_TYPES()["required"]

    assert list(required) == [
        "image_1",
        "canvas_preset",
        "custom_width",
        "custom_height",
        "layout",
        "background_mode",
        "background_color",
        "background_fit",
        "background_opacity",
        "overlay_opacity",
        "title",
        "label_1",
        "label_2",
        "label_3",
        "label_4",
        "title_color",
        "label_color",
        "cell_background_color",
        "image_fit",
        "contain_fill_mode",
        "crop_anchor",
        "font_path",
        "title_font_size",
        "label_font_size",
        "minimum_font_size",
        "max_label_lines",
        "line_spacing",
        "outer_margin",
        "top_margin",
        "bottom_margin",
        "title_gap",
        "block_gap",
        "image_label_gap",
        "inner_padding",
        "corner_radius",
        "border_width",
        "border_color",
        "logo_width_percent",
        "logo_max_height_percent",
        "logo_opacity",
        "logo_bottom_offset",
        "invert_logo_mask",
        "uppercase_title",
        "uppercase_labels",
        "debug_layout",
        "label_padding_top",
        "label_padding_bottom",
        "label_after_gap",
        "label_min_height",
        "label_vertical_align",
        "label_clip",
        "adaptive_strategy",
        "adaptive_hero",
    ]


def test_node_default_canvas_preset_is_visible_clean_and_resolvable() -> None:
    node_module = importlib.import_module("nodes")
    inputs = node_module.HLTSlideComposer.INPUT_TYPES()
    preset_names = inputs["required"]["canvas_preset"][0]
    default = inputs["required"]["canvas_preset"][1]["default"]

    assert default in preset_names
    assert default == "9:16 Social · 1080x1920"
    assert all("\u00c2" not in name for name in preset_names)
    assert all("\u00c3" not in name for name in preset_names)
    assert all("\u0100" not in name for name in preset_names)

    resolved = resolve_canvas_size(default)
    assert resolved.size == CanvasSize(width=1080, height=1920)
    assert resolved.warnings == ()


def test_node_contract_metadata() -> None:
    node_module = importlib.import_module("nodes")
    node_class = node_module.HLTSlideComposer

    assert node_class.RETURN_TYPES == ("IMAGE",)
    assert node_class.RETURN_NAMES == ("slide",)
    assert node_class.FUNCTION == "compose"
    assert node_class.CATEGORY == "HLT / Composition"


def test_no_javascript_or_comfyui_imports_are_declared() -> None:
    nodes_source = (PROJECT_ROOT / "nodes.py").read_text(encoding="utf-8")
    root_source = (PROJECT_ROOT / "__init__.py").read_text(encoding="utf-8")
    integration_source = (
        PROJECT_ROOT / "scripts" / "validate_node_integration.py"
    ).read_text(encoding="utf-8")

    assert "WEB_DIRECTORY" not in nodes_source
    assert "javascript" not in nodes_source.lower()
    assert "import comfy" not in nodes_source
    assert "folder_paths" not in nodes_source
    assert "import nodes" not in nodes_source
    assert "from nodes import" not in root_source
    assert "except ImportError" not in root_source
    assert "WEB_DIRECTORY" not in root_source
    assert "sys.path.insert" not in integration_source
