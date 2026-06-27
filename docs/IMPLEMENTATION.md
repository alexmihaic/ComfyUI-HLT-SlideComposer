# Implementation Notes

This document records the main technical decisions for `HLT · Slide Composer`.

## Current State

`v0.1.0` includes:

- pure Pillow renderer in `hlt_slide/`;
- ComfyUI adapter in `nodes.py`;
- root package mappings in `__init__.py`;
- `vertical_stack`, `grid_2x2`, and `auto_social`;
- title, labels, background, overlay, logo, mask, border, rounded corner, and debug controls;
- `IMAGE` output as `[1, H, W, 3]`, `float32`, range `0.0-1.0`;
- first-frame batch behavior with warnings for larger batches;
- automated tests and validation scripts;
- public README, release checklist, publication checklist, and safe synthetic README assets.

## Architecture

The package `hlt_slide` stays independent from ComfyUI. It contains pure renderer, geometry, text, image, color, logo, and tensor utilities.

`nodes.py` is intentionally thin:

- defines ComfyUI inputs and outputs;
- converts `IMAGE` and `MASK` inputs;
- builds `RenderSettings`;
- calls the pure Pillow renderer;
- converts the result back to a ComfyUI `IMAGE`.

`tensor_io.py` does not import Torch at package import time. Torch is only imported when creating the final output tensor, so the pure package can be tested without ComfyUI.

## Composition Order

1. base background color;
2. optional background image;
3. optional overlay;
4. content images;
5. title;
6. labels;
7. logo;
8. debug guides.

## Text and Labels

Text placement uses the full Pillow `textbbox` result. The renderer compensates `left` and `top` offsets when drawing, so real ink stays inside the calculated rectangle.

Labels reserve:

```text
label_padding_top
fitted text height
label_padding_bottom
```

The final reserved height is:

```python
max(label_min_height, label_padding_top + fitted_text_height + label_padding_bottom)
```

When `label_clip=True`, the label is rendered into an RGBA layer exactly the size of the label text area, then composited back into the slide. Only the label is clipped.

`label_after_gap` separates a label zone from the next block or row. `block_gap`/row gap remains the fallback between unlabeled blocks or rows.

## `contain` Fill Mode

`image_fit="contain"` supports:

- `transparent`: default; leftover bands show the already-composed slide background.
- `cell_color`: compatibility mode; leftover bands use `cell_background_color`.

## ComfyUI Discovery

ComfyUI loads custom nodes as packages from their installed folder. The repository root `__init__.py` exports only:

- `NODE_CLASS_MAPPINGS`
- `NODE_DISPLAY_NAME_MAPPINGS`

The discovery path is validated by `scripts/validate_package_discovery.py`, which simulates a ComfyUI-style package import and verifies the mappings come from this package's `nodes.py`.

## Checked Runtime

Validation has been run with:

- local development Python for tests and coverage;
- a ComfyUI embedded Python runtime for package discovery and node integration.

Generic validation commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --cov=hlt_slide
git diff --check

$ComfyPython = "PATH_TO_COMFYUI\python_embeded\python.exe"
& $ComfyPython scripts\validate_package_discovery.py
& $ComfyPython scripts\validate_node_integration.py
```

These scripts do not modify the ComfyUI installation and do not copy the repository into `custom_nodes`.

## Out of Scope for v0.1.0

- full batch processing;
- JavaScript UI extension;
- OpenCV;
- drag-and-drop editor;
- video output;
- `background_blur`;
- ComfyUI Registry publication.
