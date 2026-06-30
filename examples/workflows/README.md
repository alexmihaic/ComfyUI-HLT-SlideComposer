# Example Workflows

## Included

- `hlt-slide-composer-grid-4-images.json`
- `hlt-slide-composer-adaptive-mosaic.json`
- `hlt-text-composer-v0.3-experimental.json`

This workflow was exported from ComfyUI and uses:

- four content `Load Image` nodes;
- one background `Load Image` node;
- one logo `Load Image` node with mask output;
- `HLT · Slide Composer`;
- `Preview Image`;
- `auto_social`, which resolves to `grid_2x2` with four content images.

The adaptive workflow uses:

- four content `Load Image` nodes;
- one background `Load Image` node;
- one logo `Load Image` node with mask output;
- `HLT · Slide Composer`;
- `Preview Image`;
- `adaptive_mosaic`;
- `adaptive_strategy = balanced`;
- `adaptive_hero = auto`.

The image file names stored inside the workflow are local example names only. Users must select their own local images in the `Load Image` nodes after loading the workflow.

The Text Composer workflow is experimental for the `feat/text-composer-v0.3`
branch. It uses only `HLT · Text Composer` and `SaveImage`, with no external
image assets. It is intended for manual ComfyUI validation before a public
release.

## Publication Rules

- Do not add workflows created by hand.
- Reopen every workflow in ComfyUI before committing it.
- Inspect JSON before committing: no absolute private paths, local usernames, secrets, tokens, client names or private prompts.
- Do not commit original source images unless they are explicitly approved for publication.
