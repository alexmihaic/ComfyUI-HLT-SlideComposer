# Manual QA Plan for ComfyUI

Use this plan after installing the repository manually in a ComfyUI `custom_nodes` folder.

The workflow JSON examples must be exported from ComfyUI after this plan passes.

## Expected Flow

```text
Load Image -> image_1
Load Image -> image_2
Load Image -> image_3
Load Image logo -> logo_image
Load Image logo -> logo_mask
HLT · Slide Composer
Preview Image
Save Image
```

## Recommended Initial Values

- `canvas_preset`: `9:16 Social · 1080x1920`
- `layout`: `vertical_stack`
- `background_mode`: `solid`
- `background_color`: `#000000`
- `title`: `REFERENCES AND RESULT`
- `label_1`: `REF0 · PRODUCT`
- `label_2`: `REF1 · PERSON`
- `label_3`: `RESULT`
- `image_fit`: `cover`
- `crop_anchor`: `center`
- `logo_width_percent`: `18`
- `invert_logo_mask`: `true`

## Checks

- The node appears as `HLT · Slide Composer`.
- The output reaches `Preview Image`.
- The resolution is `1080 x 1920`.
- Optional disconnected images do not leave gaps.
- The logo keeps its aspect ratio and is centered at the bottom.
- The logo mask responds to `invert_logo_mask`.
- Long labels stay inside their label rectangles.
- The ComfyUI console shows no custom node startup errors.
