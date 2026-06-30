# Changelog

All notable changes to this project are documented in this file.

## Unreleased

### Added

- Experimental pure text-layout engine for the future `HLT · Text Composer` node.
- Experimental Pillow text renderer for the future `HLT · Text Composer` node.
- Role-based typography, automatic alignment, accent targeting, backgrounds, logo composition and debug rendering.
- Calibrated Text Composer typography to use the largest fitting role size.
- Preserved complete words during Text Composer wrapping.
- Changed future Text Composer default roles to four headlines.
- Registered the experimental `HLT · Text Composer` ComfyUI node.
- Added a self-contained experimental Text Composer workflow.
- Added ComfyUI contract, execution and package-discovery validation for the second node.

## 0.2.0 - 2026-06-30

### Added

- `adaptive_mosaic` layout.
- Automatic candidate generation.
- Aspect-ratio preservation.
- `balanced`, `editorial` and `compact` strategies.
- Automatic and explicit hero selection.
- Justified row candidates.
- Adaptive labels.
- Diagnostic scoring.
- Adaptive debug overlay.
- Public adaptive workflow.
- Node and renderer validation scripts.

### Changed

- Public layout options now include `adaptive_mosaic`.
- Two new widgets appended to the historical order:
  - `adaptive_strategy`;
  - `adaptive_hero`.
- Adaptive images always use proportional transparent containment.
- Documentation and examples updated for `v0.2.0`.

### Fixed

- Fixed adaptive label spacing mapping and minimum-size scaling against the resolved canvas.

### Compatibility

- Historical widget defaults remain unchanged.
- `vertical_stack`, `grid_2x2` and `auto_social` retain their previous behavior.
- Old workflows use default adaptive values without requiring JSON changes.
- `auto_social` does not automatically select `adaptive_mosaic`.

### Validated

- Local pytest suite.
- Package discovery.
- Node integration.
- Adaptive node contract.
- Torch execution with ComfyUI embedded Python.
- Manual execution inside the real ComfyUI interface.

## 0.1.0 - 2026-06-27

### Added

- Initial repository structure, MIT license, project metadata, and test setup.
- Pure Pillow/NumPy image engine with geometry models, canvas presets, color parsing, tensor conversion helpers, image fit modes, crop anchors, rounded corners, and borders.
- Text engine with font resolution, text fitting, wrapping, truncation, manual line break support, uppercase options, and bbox-aware drawing.
- `vertical_stack` layout for 1 to 4 active images.
- `grid_2x2` layout for 1 to 4 active images.
- `auto_social` selector based on the real number of connected images.
- Solid backgrounds, image backgrounds, background opacity, overlays, and `Background size` canvas preset.
- Optional bottom logo with alpha, external mask, mask inversion, opacity, proportional scaling, and centered placement.
- ComfyUI backend integration with `HLTSlideComposer`, `nodes.py`, root mappings, and `IMAGE` output.
- `INPUT_TYPES` for images, masks, canvas presets, layout, texts, colors, typography, geometry, image fitting, logo controls, and debug controls.
- First-frame batch behavior for v0.1.0 with warnings for larger batches.
- `contain_fill_mode` with `transparent` and `cell_color`.
- Transparent `contain` bands by default so the composed slide background remains visible.
- Label controls for top padding, bottom padding, after-gap, minimum height, vertical alignment, and clipping.
- Debug layout overlay for visual inspection.
- Automated tests for config, colors, image fitting, tensor I/O, fonts, text engine, backgrounds, logo masks, layouts, renderer behavior, node contract, and node execution.
- Validation scripts for package discovery and node integration using a ComfyUI-style package load.
- Example workflow exported from ComfyUI.
- Public README assets, including hero, workflow overview, grid result and vertical result images.
- Public release documentation and publication checklists.

### Fixed

- Corrected relative imports so ComfyUI-style package discovery loads the repository node instead of a global `nodes` module.
- Added realistic package discovery validation for ComfyUI custom node loading.
- Corrected mojibake in canonical canvas preset names.
- Preserved compatibility with older saved workflows through legacy preset aliases.
- Fixed `contain` rendering so transparent bands show the real slide background.
- Preserved historical widget order by appending new controls at the end.
- Fixed label text placement by compensating full `textbbox` left/top offsets.
- Added label clipping so label text cannot invade neighboring image or label rectangles.
- Added row-level label height reservation in `grid_2x2`.
- Removed duplicate public image assets and provisional workflow placeholders from the release tree.

### Validated

- Local test suite passes with coverage.
- Package discovery and node integration pass under the checked ComfyUI embedded Python runtime.
