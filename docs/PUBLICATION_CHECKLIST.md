# Publication Checklist

This checklist is for making the repository public and publishing `v0.1.0`.

## Before Changing Visibility

- [ ] Confirm `docs/RELEASE_CHECKLIST.md` is complete.
- [ ] Confirm no private screenshots or workflow JSON files are tracked.
- [ ] Confirm tracked screenshots and PNGs are publication-safe.
- [ ] Confirm workflow JSON files contain no absolute paths or secrets.
- [ ] Confirm resource licensing is acceptable for every tracked visual asset.
- [ ] Confirm `README.md` uses generic install paths only.
- [ ] Confirm license is present.
- [ ] Confirm `origin/main` contains the release preparation commit.
- [ ] Confirm there are no GitHub Actions, package publishing workflows, or Registry automation that would publish unexpectedly.

## Change Repository to Public

1. Open the GitHub repository settings.
2. Go to the visibility or danger zone section.
3. Choose the option to change visibility to public.
4. Confirm the repository name when GitHub asks for confirmation.
5. Reopen the public repository page in a private/incognito browser session.
6. Verify README images render and no private data is visible.

## Create Tag

```powershell
git checkout main
git pull origin main
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

## Create GitHub Prerelease

1. Open GitHub Releases.
2. Draft a new release from tag `v0.1.0`.
3. Title: `HLT Slide Composer v0.1.0`.
4. Paste the release notes below.
5. Attach no private local files.
6. Mark it as a prerelease for the first public alpha.
7. Publish the prerelease.

## Public Clone Verification

```powershell
cd "TEMP_TEST_DIRECTORY"
git clone https://github.com/alexmihaic/ComfyUI-HLT-SlideComposer.git
cd ComfyUI-HLT-SlideComposer
git checkout v0.1.0
```

Verify README links and workflow files are present in the public clone.

## External Testers

- [ ] Send the public repository URL to 2-3 testers.
- [ ] Ask each tester to install with `git clone`.
- [ ] Ask each tester to load the example workflow and replace image inputs.
- [ ] Collect issues and screenshots.
- [ ] Triage fixes for `v0.1.1`.

## ComfyUI Registry

Do not publish to ComfyUI Registry for `v0.1.0` until a separate Registry checklist is completed.

## Proposed Release Notes

```markdown
## HLT Slide Composer v0.1.0

Initial public alpha release of `HLT · Slide Composer`, a ComfyUI custom node for composing one to four images into an editorial slide with title, labels, background, and optional logo.

### Highlights

- Adds the `HLT · Slide Composer` node under `HLT / Composition`.
- Supports `vertical_stack`, `grid_2x2`, and `auto_social`.
- Supports 1 to 4 active images without gaps from disconnected optional inputs.
- Outputs ComfyUI `IMAGE` tensors as `[1, H, W, 3]`, `float32`, range `0.0-1.0`.
- Includes 9:16, 4:5, 3:4, 1:1, custom, and background-size canvas presets.
- Supports solid backgrounds, image backgrounds, overlays, image fit modes, rounded corners, borders, and optional logos with masks.
- Uses transparent `contain` bands by default so the slide background remains visible.
- Adds label padding, minimum height, vertical alignment, after-gap, and clipping controls.
- Fixes package discovery for ComfyUI-style loading.
- Keeps the renderer independent from ComfyUI for direct testing.

### Validation

- Unit and integration tests pass.
- Package discovery and node integration are validated with a ComfyUI embedded Python runtime.

### Known Limitations

- Processes only the first frame of each input batch in v0.1.0.
- No JavaScript UI extension.
- No OpenCV.
- No video output.
- Example workflow uses local image filenames; users must select their own files.
- UI screenshots should be reviewed before wider announcement.
```

## Rollback

- Remove or rename `ComfyUI-HLT-SlideComposer` from `ComfyUI/custom_nodes`.
- Restart ComfyUI.
- If the GitHub Release has a blocking issue, mark it as pre-release or remove it and publish a corrected patch release.
- Use `v0.1.1` for post-publication fixes instead of rewriting `v0.1.0` after testers have pulled it.
