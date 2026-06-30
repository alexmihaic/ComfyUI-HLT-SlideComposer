# v0.2.0 Release Checklist

Use this checklist before creating the `v0.2.0` tag and GitHub Release.

## Automated QA

- [ ] Run `.\.venv\Scripts\python.exe -m pytest -q`.
- [ ] Run `.\.venv\Scripts\python.exe -m pytest --cov=hlt_slide`.
- [ ] Run `git diff --check`.
- [ ] Run `PATH_TO_COMFYUI\python_embeded\python.exe scripts\validate_package_discovery.py`.
- [ ] Run `PATH_TO_COMFYUI\python_embeded\python.exe scripts\validate_node_integration.py`.
- [ ] Run `PATH_TO_COMFYUI\python_embeded\python.exe scripts\validate_adaptive_node_contract.py`.
- [ ] Run `PATH_TO_COMFYUI\python_embeded\python.exe -m pytest tests/test_node_execution.py -q`.
- [ ] Validate all PNG assets can be opened.
- [ ] Validate all workflow JSON files parse successfully.
- [ ] Validate README relative links resolve.
- [ ] Confirm no mojibake remains in public docs or workflow JSON.

## Clean Install QA

- [ ] Clone into a clean `ComfyUI/custom_nodes` folder.
- [ ] Restart ComfyUI.
- [ ] Confirm the node appears as `HLT · Slide Composer`.
- [ ] Confirm the node is under `HLT / Composition`.
- [ ] Create a one-image `vertical_stack` slide.
- [ ] Create a three-image `vertical_stack` slide.
- [ ] Create a four-image `grid_2x2` slide.
- [ ] Test `auto_social` with four images.
- [ ] Test a background image with overlay.
- [ ] Test a logo image with mask.
- [ ] Test long labels with clipping enabled.
- [ ] Confirm `adaptive_mosaic` is visible in the layout widget.
- [ ] Confirm `adaptive_strategy` is visible with `balanced`, `editorial`, and `compact`.
- [ ] Confirm `adaptive_hero` is visible with `auto` and `image_1` to `image_4`.
- [ ] Create a four-image `adaptive_mosaic` slide.
- [ ] Confirm output is RGB and the selected resolution is preserved.
- [ ] Confirm manual UI test was completed by the project owner.

## Workflow QA

- [ ] Reopen `examples/workflows/hlt-slide-composer-grid-4-images.json` from disk.
- [ ] Reopen `examples/workflows/hlt-slide-composer-adaptive-mosaic.json` from disk.
- [ ] Queue the workflow successfully.
- [ ] Confirm no disconnected optional inputs leave visual gaps.
- [ ] Confirm the workflow uses four content images, a background image, logo image, logo mask, `HLTSlideComposer`, and `PreviewImage`.
- [ ] Confirm the adaptive workflow uses `adaptive_mosaic`, `balanced`, and `adaptive_hero=auto`.
- [ ] Confirm the v0.1.0 workflow remains compatible and still uses `auto_social`.
- [ ] Inspect JSON files for private absolute paths or sensitive data.

## Screenshot QA

- [ ] Capture `docs/assets/readme/node-interface.png`.
- [ ] Capture `docs/assets/readme/workflow-overview.png`.
- [ ] Confirm screenshots do not show private paths, usernames, private prompts, local model names, or client imagery.
- [ ] Update README if screenshots are added.

## Privacy Audit

- [ ] Run a repository text search for secrets, tokens, keys, passwords, `.env`, and absolute local paths.
- [ ] Check `git status --short --untracked-files=all`.
- [ ] Confirm no `.env`, local caches, virtual environments, ComfyUI outputs, or model files are tracked.
- [ ] Review all public screenshots and PNGs.

## Tag and Release

- [ ] Confirm `pyproject.toml` version is `0.2.0`.
- [ ] Confirm `hlt_slide/__init__.py` version is `0.2.0`.
- [ ] Confirm `CHANGELOG.md` has `## 0.2.0 - 2026-06-30`.
- [ ] Confirm `docs/RELEASE_NOTES_v0.2.0.md` exists.
- [ ] Confirm README links to the real workflow JSON.
- [ ] Confirm public adaptive assets were reduced to selected README assets.
- [ ] Confirm `main` is pushed.
- [ ] Confirm clean clone verification is pending until after merge to `main`.
- [ ] Create tag: `git tag -a v0.2.0 -m "v0.2.0"`.
- [ ] Push tag: `git push origin v0.2.0`.
- [ ] Create GitHub Release from `v0.2.0`.
- [ ] Paste release notes from `docs/RELEASE_NOTES_v0.2.0.md`.

## Rollback Plan

- [ ] If install fails, delete or rename `ComfyUI-HLT-SlideComposer` in `custom_nodes`.
- [ ] Restart ComfyUI and confirm startup is restored.
- [ ] If a release has already been published with a serious issue, mark the GitHub Release as pre-release or delete the release.
- [ ] If the tag is wrong and has not been widely consumed, delete the remote tag only after confirming the correction plan.
- [ ] Prepare a patch release such as `v0.1.1` for fixes after publication.
