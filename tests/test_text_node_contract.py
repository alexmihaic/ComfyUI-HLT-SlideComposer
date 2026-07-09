from __future__ import annotations

import importlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ORDER = [
    "text_1", "text_2", "text_3", "text_4",
    "canvas_preset", "custom_width", "custom_height",
    "layout",
    "text_1_role", "text_2_role", "text_3_role", "text_4_role",
    "split_axis",
    "background_mode", "background_color", "background_fit", "background_opacity", "overlay_opacity",
    "text_color", "accent_color", "accent_target",
    "font_path", "font_scale",
    "horizontal_align", "vertical_align", "uppercase", "preserve_words", "clipping",
    "outer_margin", "top_margin", "bottom_margin", "block_gap", "inner_padding",
    "logo_width_percent", "logo_max_height_percent", "logo_opacity", "logo_bottom_offset",
    "invert_logo_mask", "reserve_logo_space", "logo_gap",
    "debug_layout",
]


def test_text_node_class_metadata_and_mappings_order() -> None:
    node_module = importlib.import_module("nodes")

    assert hasattr(node_module, "HLTTextComposer")
    assert node_module.TEXT_NODE_NAME == "HLTTextComposer"
    assert node_module.TEXT_NODE_DISPLAY_NAME == "HLT · Text Composer"
    assert list(node_module.NODE_CLASS_MAPPINGS) == ["HLTSlideComposer", "HLTTextComposer"]
    assert list(node_module.NODE_DISPLAY_NAME_MAPPINGS) == ["HLTSlideComposer", "HLTTextComposer"]
    assert node_module.NODE_CLASS_MAPPINGS["HLTSlideComposer"] is node_module.HLTSlideComposer
    assert node_module.NODE_CLASS_MAPPINGS["HLTTextComposer"] is node_module.HLTTextComposer
    assert node_module.NODE_DISPLAY_NAME_MAPPINGS["HLTTextComposer"] == "HLT · Text Composer"

    node_class = node_module.HLTTextComposer
    assert node_class.RETURN_TYPES == ("IMAGE",)
    assert node_class.RETURN_NAMES == ("design",)
    assert node_class.FUNCTION == "compose"
    assert node_class.CATEGORY == "HLT / Composition"


def test_text_node_input_types_order_defaults_and_no_frontend() -> None:
    inputs = importlib.import_module("nodes").HLTTextComposer.INPUT_TYPES()
    required = inputs["required"]
    optional = inputs["optional"]

    assert list(required) == REQUIRED_ORDER
    assert list(optional) == ["background_image", "logo_image", "logo_mask"]
    assert optional == {
        "background_image": ("IMAGE",),
        "logo_image": ("IMAGE",),
        "logo_mask": ("MASK",),
    }
    assert required["text_1"] == ("STRING", {"default": "YOUR TEXT", "multiline": True})
    for name in ("text_2", "text_3", "text_4"):
        assert required[name] == ("STRING", {"default": "", "multiline": True})
    assert required["layout"][0] == (
        "auto_text", "centered_statement", "vertical_stack", "split_2", "grid_2x2", "editorial_quote"
    )
    assert required["layout"][1]["default"] == "auto_text"
    roles = ("headline", "subheadline", "body", "quote", "caption", "number", "label")
    for name in ("text_1_role", "text_2_role", "text_3_role", "text_4_role"):
        assert required[name][0] == roles
        assert required[name][1]["default"] == "headline"
    assert required["preserve_words"][1]["default"] is True
    assert required["accent_target"][1]["default"] == "none"
    assert required["reserve_logo_space"][1]["default"] is True

    source = (PROJECT_ROOT / "nodes.py").read_text(encoding="utf-8")
    assert "forceInput" not in source
    assert "WEB_DIRECTORY" not in source
    assert "javascript" not in source.lower()


def test_slide_composer_contract_still_has_historical_widget_order() -> None:
    required = importlib.import_module("nodes").HLTSlideComposer.INPUT_TYPES()["required"]

    assert list(required)[0] == "image_1"
    assert required["layout"][0] == ("vertical_stack", "grid_2x2", "auto_social", "adaptive_mosaic", "comparison")
    assert list(required)[-9:] == [
        "label_padding_top", "label_padding_bottom", "label_after_gap", "label_min_height",
        "label_vertical_align", "label_clip", "adaptive_strategy", "adaptive_hero",
        "style_preset",
    ]


def test_text_workflow_contract() -> None:
    workflow_path = PROJECT_ROOT / "examples" / "workflows" / "hlt-text-composer-v0.3-experimental.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    types = {node["type"] for node in workflow["nodes"]}

    assert "HLTTextComposer" in types
    assert "SaveImage" in types
    assert "LoadImage" not in types
    assert "C:\\Users" not in workflow_path.read_text(encoding="utf-8")
    text_node = next(node for node in workflow["nodes"] if node["type"] == "HLTTextComposer")
    widgets = text_node["widgets_values"]
    assert widgets[3] == ""
    assert widgets[7] == "auto_text"
    assert widgets[20] == "text_1"
    assert widgets[26] is True
    assert len(widgets) == len(REQUIRED_ORDER)
    assert workflow["links"][0][1] == text_node["id"]
