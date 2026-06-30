# HLT Slide Composer v0.2.0

## Highlights

HLT Slide Composer v0.2.0 adds the public `adaptive_mosaic` layout to `HLT · Slide Composer` for mixed portrait, landscape and square image sets.

The node remains a pure backend ComfyUI custom node. It outputs a standard ComfyUI `IMAGE` tensor and keeps the renderer independent from ComfyUI for local testing.

## Adaptive Mosaic

`adaptive_mosaic` generates and scores several internal layout candidates, then renders the selected layout without cropping or stretching source images. Images are placed with proportional transparent containment, so the slide background may remain visible when that is the best way to preserve aspect ratios.

Use:

```text
layout = adaptive_mosaic
adaptive_strategy = balanced | editorial | compact
adaptive_hero = auto | image_1 | image_2 | image_3 | image_4
```

Hero selection is geometric, not semantic. If an explicit hero points to a disconnected image, the node warns and falls back to `auto`.

## Strategies

`balanced` prioritizes readability, visual balance and reasonable image sizes.

`editorial` allows one image to become dominant.

`compact` prioritizes lower empty area.

## Compatibility

Historical widget defaults remain unchanged. The new widgets are appended after the previous widget order:

```text
adaptive_strategy
adaptive_hero
```

Existing workflows can load without JSON changes and receive the default adaptive values. `vertical_stack`, `grid_2x2` and `auto_social` keep their previous behavior. `auto_social` does not automatically select `adaptive_mosaic`.

## Installation

```powershell
cd "PATH_TO_COMFYUI\ComfyUI\custom_nodes"
git clone https://github.com/alexmihaic/ComfyUI-HLT-SlideComposer.git
```

Restart ComfyUI and search for `HLT · Slide Composer` under `HLT / Composition`.

## Update

```powershell
cd "PATH_TO_COMFYUI\ComfyUI\custom_nodes\ComfyUI-HLT-SlideComposer"
git switch main
git pull --ff-only origin main
```

Restart ComfyUI after updating.

## Example Workflow

The public adaptive workflow is:

```text
examples/workflows/hlt-slide-composer-adaptive-mosaic.json
```

It uses local image filenames as placeholders. Replace them with images from your own ComfyUI input folder before queueing.

## Tested Environment

Validated environment:

```text
ComfyUI 0.26.1
ComfyUI frontend 1.45.19
Python 3.11.8
Pillow 10.4.0
NumPy 1.26.4
Torch 2.9.1+cu130
Windows
```

The project owner also confirmed manual execution inside their real ComfyUI interface.

## Known Limitations

- Maximum of four images.
- Only the first frame of each input batch is used.
- `adaptive_mosaic` hero selection is geometric, not semantic.
- Preserving aspect ratios can leave visible background.
- Main validation for this release is on Windows.
- Example workflows require users to select their own local images.
- HLT Text Composer is not implemented in this release.
