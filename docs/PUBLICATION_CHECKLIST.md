# Publication Checklist

This checklist is for publishing `v0.2.0`.

## Before Publishing

- [ ] Confirm `docs/RELEASE_CHECKLIST.md` is complete.
- [ ] Confirm no private screenshots or workflow JSON files are tracked.
- [ ] Confirm tracked screenshots and PNGs are publication-safe.
- [ ] Confirm adaptive public assets are limited to selected README assets.
- [ ] Confirm workflow JSON files contain no absolute paths or secrets.
- [ ] Confirm `examples/workflows/hlt-slide-composer-adaptive-mosaic.json` is present.
- [ ] Confirm the adaptive workflow uses `adaptive_mosaic`, `balanced`, and `adaptive_hero=auto`.
- [ ] Confirm the v0.1.0 workflow remains compatible.
- [ ] Confirm no mojibake remains in public docs or workflow JSON.
- [ ] Confirm resource licensing is acceptable for every tracked visual asset.
- [ ] Confirm `README.md` uses generic install paths only.
- [ ] Confirm license is present.
- [ ] Confirm versioning is `0.2.0`.
- [ ] Confirm `docs/RELEASE_NOTES_v0.2.0.md` exists.
- [ ] Confirm manual UI test was completed by the project owner.
- [ ] Confirm `origin/main` contains the release preparation commit after merge.
- [ ] Confirm there are no GitHub Actions, package publishing workflows, or Registry automation that would publish unexpectedly.
- [ ] Confirm clean clone verification is pending until after merge to `main`.

## Create Tag

Only after the release preparation branch is merged to `main`:

```powershell
git checkout main
git pull origin main
git tag -a v0.2.0 -m "v0.2.0"
git push origin v0.2.0
```

## Create GitHub Release

1. Open GitHub Releases.
2. Draft a new release from tag `v0.2.0`.
3. Title: `HLT Slide Composer v0.2.0`.
4. Paste release notes from `docs/RELEASE_NOTES_v0.2.0.md`.
5. Attach no private local files.
6. Publish the release.

## Public Clone Verification

After merge and publication:

```powershell
cd "TEMP_TEST_DIRECTORY"
git clone https://github.com/alexmihaic/ComfyUI-HLT-SlideComposer.git
cd ComfyUI-HLT-SlideComposer
git checkout v0.2.0
```

Verify README links, workflow files and README assets are present in the public clone.

## External Testers

- [ ] Send the public repository URL to 2-3 testers.
- [ ] Ask each tester to install with `git clone`.
- [ ] Ask each tester to load the example workflows and replace image inputs.
- [ ] Collect issues and screenshots.
- [ ] Triage fixes for `v0.2.1`.

## ComfyUI Registry

Do not publish to ComfyUI Registry for `v0.2.0` until a separate Registry checklist is completed.

## Rollback

- Remove or rename `ComfyUI-HLT-SlideComposer` from `ComfyUI/custom_nodes`.
- Restart ComfyUI.
- If the GitHub Release has a blocking issue, mark it as pre-release or remove it and publish a corrected patch release.
- Use `v0.2.1` for post-publication fixes instead of rewriting `v0.2.0` after testers have pulled it.
