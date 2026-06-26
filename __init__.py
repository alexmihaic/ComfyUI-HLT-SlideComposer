"""ComfyUI entrypoint for HLT Slide Composer."""

from __future__ import annotations

if __package__:
    from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
else:
    import importlib.util
    import sys
    from pathlib import Path

    _nodes_path = Path(__file__).with_name("nodes.py")
    _spec = importlib.util.spec_from_file_location("_hlt_slide_composer_nodes", _nodes_path)
    if _spec is None or _spec.loader is None:
        raise ImportError(f"Could not load local nodes module from {_nodes_path}")
    _nodes_module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _nodes_module
    _spec.loader.exec_module(_nodes_module)
    NODE_CLASS_MAPPINGS = _nodes_module.NODE_CLASS_MAPPINGS
    NODE_DISPLAY_NAME_MAPPINGS = _nodes_module.NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
