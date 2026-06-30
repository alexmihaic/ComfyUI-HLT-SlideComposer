from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import nodes
WORKFLOW_PATH = PROJECT_ROOT / "examples" / "workflows" / "hlt-text-composer-v0.3-experimental.json"
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


def main() -> int:
    assert list(nodes.NODE_CLASS_MAPPINGS) == ["HLTSlideComposer", "HLTTextComposer"]
    assert nodes.NODE_DISPLAY_NAME_MAPPINGS["HLTTextComposer"] == "HLT · Text Composer"
    node_class = nodes.NODE_CLASS_MAPPINGS["HLTTextComposer"]
    assert node_class.CATEGORY == "HLT / Composition"
    assert node_class.RETURN_TYPES == ("IMAGE",)
    assert node_class.RETURN_NAMES == ("design",)

    inputs = node_class.INPUT_TYPES()
    assert list(inputs["required"]) == REQUIRED_ORDER
    assert list(inputs["optional"]) == ["background_image", "logo_image", "logo_mask"]
    assert inputs["required"]["text_1"][1]["multiline"] is True
    assert inputs["required"]["preserve_words"][1]["default"] is True
    assert inputs["required"]["reserve_logo_space"][1]["default"] is True

    source = (PROJECT_ROOT / "nodes.py").read_text(encoding="utf-8")
    assert "forceInput" not in source
    assert "WEB_DIRECTORY" not in source
    assert "javascript" not in source.lower()

    workflow_source = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow = json.loads(workflow_source)
    assert "C:\\Users" not in workflow_source
    assert "LoadImage" not in workflow_source
    text_node = next(node for node in workflow["nodes"] if node["type"] == "HLTTextComposer")
    assert len(text_node["widgets_values"]) == len(REQUIRED_ORDER)
    assert any(node["type"] == "SaveImage" for node in workflow["nodes"])
    print("HLT Text Composer contract validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
