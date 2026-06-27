# HLT Slide Composer for ComfyUI

`HLT · Slide Composer` is a ComfyUI custom node for composing one to four images into an editorial slide with a title, per-image labels, optional background image, and optional bottom logo.

It is built for quick social/story layouts, visual comparisons, generation results, process documentation, and compact presentation slides.

> Breve descripcion en espanol: un nodo de ComfyUI para crear slides editoriales verticales con imagenes, titulo, etiquetas, fondo y logo.

![HLT Slide Composer hero](docs/assets/readme/hero.png)

## Screenshots

![Grid example](docs/assets/readme/grid-example.png)

![Vertical example](docs/assets/readme/vertical-example.png)

ComfyUI interface screenshots are intentionally not included until the final manual QA pass captures them from a clean installation. See `docs/assets/readme/README.md` for the exact expected files.

## Features

- Composes 1 to 4 connected images.
- Outputs a valid ComfyUI `IMAGE` tensor: `[1, H, W, 3]`, `float32`, range `0.0-1.0`.
- Main preset: `9:16 Social · 1080x1920`.
- Additional presets: `9:16 AI`, `9:16 4K`, `4:5`, `3:4`, `1:1`, `Custom`, and `Background size`.
- Layouts: `vertical_stack`, `grid_2x2`, and `auto_social`.
- Image fitting: `cover`, `contain`, and `stretch`.
- Transparent `contain` bands by default, so the slide background remains visible.
- Optional title and per-image labels.
- Label padding, minimum height, vertical alignment, after-gap, and clipping controls.
- Solid background, image background, and image background with overlay.
- Optional bottom logo with mask support, opacity, proportional scaling, and centering.
- Debug layout overlay for checking rectangles.
- No JavaScript, OpenCV, GUI framework, or bundled proprietary assets.

## Installation

Manual installation with `git clone`:

```powershell
cd "PATH_TO_COMFYUI\ComfyUI\custom_nodes"
git clone https://github.com/alexmihaic/ComfyUI-HLT-SlideComposer.git
```

Restart ComfyUI, then search for:

```text
HLT · Slide Composer
```

Runtime dependencies are intentionally small:

```text
Pillow>=10.0.0
numpy>=1.24.0
```

Torch is provided by ComfyUI and is not installed separately by this project.

## Update

```powershell
cd "PATH_TO_COMFYUI\ComfyUI\custom_nodes\ComfyUI-HLT-SlideComposer"
git pull origin main
```

Restart ComfyUI after updating.

## Quick Start

1. Add `HLT · Slide Composer`.
2. Connect `image_1`.
3. Optionally connect `image_2`, `image_3`, and `image_4`.
4. Set `canvas_preset` to `9:16 Social · 1080x1920`.
5. Choose `vertical_stack`, `grid_2x2`, or `auto_social`.
6. Add a title and labels if needed.
7. Optionally connect a background image, logo image, and logo mask.
8. Connect the output to `Preview Image` or `Save Image`.

Recommended first values:

```text
layout = vertical_stack
background_color = #000000
title_color = #E92124
label_color = #E92124
image_fit = cover
crop_anchor = center
```

## Layouts

### `vertical_stack`

Single-column layout for 1 to 4 images. Each active image gets its own block. Empty optional image inputs are ignored and do not leave gaps.

Label spacing sequence:

```text
image
image_label_gap
label_padding_top
text
label_padding_bottom
label_after_gap
next image
```

`block_gap` is used between blocks only when the previous block has no label.

### `grid_2x2`

Grid layout for 1 to 4 images:

- 1 image: one full-width cell.
- 2 images: two equal columns.
- 3 images: one full-width top cell and two lower columns.
- 4 images: regular 2 x 2 grid.

Labels in the same row share the same reserved label height, based on the tallest label in that row.

### `auto_social`

Automatic selector:

- 1 image: `vertical_stack`
- 2 images: `vertical_stack`
- 3 images: `vertical_stack`
- 4 images: `grid_2x2`

## Main Controls

- `canvas_preset`, `custom_width`, `custom_height`
- `layout`
- `background_mode`, `background_color`, `background_fit`, `background_opacity`, `overlay_opacity`
- `title`, `label_1`, `label_2`, `label_3`, `label_4`
- `title_color`, `label_color`, `font_path`, font sizes, line spacing
- `image_fit`, `contain_fill_mode`, `crop_anchor`
- `outer_margin`, `top_margin`, `bottom_margin`, `title_gap`, `block_gap`, `image_label_gap`
- `label_padding_top`, `label_padding_bottom`, `label_after_gap`, `label_min_height`, `label_vertical_align`, `label_clip`
- `inner_padding`, `corner_radius`, `border_width`, `border_color`
- `logo_width_percent`, `logo_max_height_percent`, `logo_opacity`, `logo_bottom_offset`, `invert_logo_mask`
- `debug_layout`

## Example Workflows

The repository reserves these workflow paths for ComfyUI-exported examples:

```text
examples/workflows/hlt_slide_composer_grid_4_images.json
examples/workflows/hlt_slide_composer_vertical_3_images.json
```

They are not committed yet because they must be exported from ComfyUI during manual QA, not invented by hand. See `examples/workflows/README.md` for the exact capture/export instructions.

## Checked Compatibility

Automated validation has been run on Windows with:

- Python `3.14.2` in the local development virtual environment.
- ComfyUI embedded Python `3.11.8`.
- Pillow `10.4.0` in the checked ComfyUI runtime.
- NumPy `1.26.4` in the checked ComfyUI runtime.
- Torch `2.9.1+cu130` in the checked ComfyUI runtime.

Validation scripts:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --cov=hlt_slide

$ComfyPython = "PATH_TO_COMFYUI\python_embeded\python.exe"
& $ComfyPython scripts\validate_package_discovery.py
& $ComfyPython scripts\validate_node_integration.py
```

## Limitations in v0.1.0

- Uses only the first frame of each input batch.
- Does not implement full batch zip/broadcast processing.
- No JavaScript UI extension.
- No OpenCV.
- No drag-and-drop visual editor.
- No manual per-image positioning.
- No video output.
- `background_blur` is not implemented in v0.1.0.
- Workflow JSON examples still require export from a clean ComfyUI manual QA pass.
- Public release tag and GitHub Release are prepared but not created in this repository state.

## Roadmap

Potential future work:

- `comparison` layout.
- `hero_stack` layout.
- Adaptive mosaic options such as `adaptive_mosaic`, `justified_rows`, `masonry_columns`, and `hero_mosaic`.
- Batch processing modes.
- Shadows and label background options.
- Style presets.
- ComfyUI Registry publication after public QA.

## Uninstall

1. Close ComfyUI.
2. Remove or rename:

```text
PATH_TO_COMFYUI\ComfyUI\custom_nodes\ComfyUI-HLT-SlideComposer
```

3. Restart ComfyUI.

## Development and Tests

Create a local development environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .[dev]
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --cov=hlt_slide
git diff --check
```

The pure renderer lives in `hlt_slide/`. The ComfyUI adapter is intentionally kept thin in `nodes.py`.

## License

MIT. See `LICENSE`.
