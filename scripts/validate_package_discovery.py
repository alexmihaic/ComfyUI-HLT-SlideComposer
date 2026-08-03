from __future__ import annotations

import importlib.abc
import importlib.util
import sys
import types
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "comfyui_hlt_slide_composer_discovery"


class BlockTopLevelHltSlide(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path: object = None, target: object = None) -> None:
        if fullname == "hlt_slide" or fullname.startswith("hlt_slide."):
            raise ModuleNotFoundError("blocked top-level hlt_slide")
        return None


def clear_package_modules(package_name: str) -> None:
    for module_name in tuple(sys.modules):
        if module_name == package_name or module_name.startswith(f"{package_name}."):
            sys.modules.pop(module_name, None)


def load_custom_node_package() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        PACKAGE_NAME,
        PROJECT_ROOT / "__init__.py",
        submodule_search_locations=[str(PROJECT_ROOT)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create import spec for custom node package.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
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

    blocker = BlockTopLevelHltSlide()
    sys.meta_path.insert(0, blocker)
    try:
        package = load_custom_node_package()
        assert list(package.NODE_CLASS_MAPPINGS) == ["HLTSlideComposer"]
        assert package.NODE_DISPLAY_NAME_MAPPINGS == {
            "HLTSlideComposer": "HLT · Slide Composer",
        }
        node_class = package.NODE_CLASS_MAPPINGS["HLTSlideComposer"]
        assert node_class.__name__ == "HLTSlideComposer"
        assert node_class.__module__ == f"{PACKAGE_NAME}.nodes"
    finally:
        sys.meta_path.remove(blocker)
        clear_package_modules(PACKAGE_NAME)
        sys.modules.pop("nodes", None)
        if saved_nodes_module is not None:
            sys.modules["nodes"] = saved_nodes_module
        sys.modules.update(saved_hlt_modules)

    print("HLT Comfy package discovery validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
