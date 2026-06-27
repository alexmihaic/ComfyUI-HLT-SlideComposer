# Example Workflows

The planned example workflow files are:

- `hlt_slide_composer_grid_4_images.json`
- `hlt_slide_composer_vertical_3_images.json`

Do not create these JSON files by hand. They must be exported from ComfyUI during manual QA.

## Export Checklist

1. Install this repository in a clean ComfyUI `custom_nodes` folder with `git clone`.
2. Restart ComfyUI and confirm the node appears as `HLT · Slide Composer`.
3. Build a 4-image `grid_2x2` workflow using only safe public or synthetic images.
4. Export it as `examples/workflows/hlt_slide_composer_grid_4_images.json`.
5. Build a 3-image `vertical_stack` workflow using only safe public or synthetic images.
6. Export it as `examples/workflows/hlt_slide_composer_vertical_3_images.json`.
7. Reopen both JSON files in ComfyUI and confirm they execute.
8. Inspect the JSON before committing: no absolute private paths, no local usernames, no secrets, no client assets.
