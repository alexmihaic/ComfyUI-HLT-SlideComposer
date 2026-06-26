from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path

from hlt_slide.config import RESOLUTION_PRESETS


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_node_module_exports_class_and_mappings() -> None:
    node_module = importlib.import_module("nodes")

    assert hasattr(node_module, "HLTSlideComposer")
    assert node_module.NODE_CLASS_MAPPINGS == {"HLTSlideComposer": node_module.HLTSlideComposer}
    assert node_module.NODE_DISPLAY_NAME_MAPPINGS == {
        "HLTSlideComposer": "HLT · Slide Composer"
    }
    assert not hasattr(node_module, "WEB_DIRECTORY")


def test_root_init_exports_only_comfyui_mappings() -> None:
    spec = importlib.util.spec_from_file_location(
        "hlt_slide_composer_root",
        PROJECT_ROOT / "__init__.py",
        submodule_search_locations=[str(PROJECT_ROOT)],
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.NODE_CLASS_MAPPINGS
    assert module.NODE_DISPLAY_NAME_MAPPINGS
    assert module.__all__ == ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
    assert not hasattr(module, "WEB_DIRECTORY")


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
    assert required["layout"][0] == ("vertical_stack", "grid_2x2", "auto_social")
    assert required["layout"][1]["default"] == "vertical_stack"
    assert required["background_color"][1]["default"] == "#000000"
    assert required["title_color"][1]["default"] == "#E92124"
    assert required["label_color"][1]["default"] == "#E92124"
    assert required["debug_layout"][1]["default"] is False


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

    assert "WEB_DIRECTORY" not in nodes_source
    assert "javascript" not in nodes_source.lower()
    assert "import comfy" not in nodes_source
    assert "folder_paths" not in nodes_source
    assert "import nodes" not in nodes_source
    assert "WEB_DIRECTORY" not in root_source
