# HLT Slide Composer v0.1.0

Initial public alpha release of `HLT · Slide Composer`, a ComfyUI custom node for composing 1–4 images into editorial slides with titles, labels, backgrounds, overlays and logos.

## Highlights

- Adds the `HLT · Slide Composer` node under `HLT / Composition`.
- Supports `vertical_stack`, `grid_2x2`, and `auto_social`.
- Supports 1–4 active images without gaps from disconnected optional inputs.
- Supports solid or image backgrounds, overlays, logo images and masks.
- Supports `cover`, `contain`, and `stretch` image fitting.
- Includes transparent `contain` bands, label padding, label spacing, vertical label alignment, and clipping.
- Includes a real ComfyUI-exported example workflow for four images.
- Validated with automated tests, package-discovery checks, node-integration checks, and real ComfyUI execution.

## Tested environment

- ComfyUI 0.26.1
- ComfyUI frontend 1.45.19
- Python 3.11.8
- Pillow 10.4.0
- NumPy 1.26.4
- Torch 2.9.1+cu130
- Windows

Other versions may work but have not yet been verified.

## Known limitations

- Maximum of four images.
- Only the first frame of each batch is used.
- No adaptive mosaic yet.
- No background blur.
- No custom frontend.
- Example workflows require users to select their own local images.
- External font paths depend on the local machine.

## Installation

```powershell
cd "PATH_TO_COMFYUI\ComfyUI\custom_nodes"
git clone https://github.com/alexmihaic/ComfyUI-HLT-SlideComposer.git
```

Restart ComfyUI, search for `HLT · Slide Composer`, and find it under `HLT / Composition`.

## Example workflow

Load:

`examples/workflows/hlt-slide-composer-grid-4-images.json`

Replace the local files in each `Load Image` node with your own images before running the workflow.
