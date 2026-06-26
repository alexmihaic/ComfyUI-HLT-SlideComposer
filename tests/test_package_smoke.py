from __future__ import annotations

import importlib
from pathlib import Path


def test_package_imports_and_exposes_initial_version() -> None:
    package = importlib.import_module("hlt_slide")

    assert package.__version__ == "0.1.0"


def test_phase_zero_directories_exist() -> None:
    project_root = Path(__file__).resolve().parents[1]

    expected_paths = [
        project_root / "hlt_slide",
        project_root / "examples" / "workflows",
        project_root / "examples" / "outputs",
        project_root / "docs" / "references",
    ]

    for path in expected_paths:
        assert path.exists(), f"Missing expected path: {path}"
