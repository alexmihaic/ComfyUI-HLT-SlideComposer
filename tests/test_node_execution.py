from __future__ import annotations

import warnings
import json
from pathlib import Path

import pytest
from PIL import Image


try:
    import torch
except ImportError:
    torch = None


requires_torch = pytest.mark.skipif(
    torch is None,
    reason="torch is required for node execution tests",
)

import nodes  # noqa: E402
from nodes import HLTSlideComposer  # noqa: E402


def _image(
    color: tuple[float, float, float],
    *,
    size: tuple[int, int] = (32, 24),
    batch: int = 1,
):
    height, width = size[1], size[0]
    tensor = torch.zeros((batch, height, width, 3), dtype=torch.float32)
    tensor[:, :, :, 0] = color[0]
    tensor[:, :, :, 1] = color[1]
    tensor[:, :, :, 2] = color[2]
    return tensor


def _pattern_image(*, size: tuple[int, int], color: tuple[float, float, float]):
    tensor = _image(color, size=size)
    tensor[:, 0:2, :, :] = 1.0
    tensor[:, -2:, :, :] = 1.0
    tensor[:, :, 0:2, :] = 1.0
    tensor[:, :, -2:, :] = 1.0
    return tensor


def _mask(*, size: tuple[int, int] = (32, 24), batch: int = 1):
    height, width = size[1], size[0]
    return torch.zeros((batch, height, width), dtype=torch.float32)


def _compose_kwargs(**overrides):
    base = {
        "image_1": _image((1.0, 0.0, 0.0)),
        "canvas_preset": "Custom",
        "custom_width": 320,
        "custom_height": 480,
        "layout": "vertical_stack",
        "background_mode": "solid",
        "background_color": "#000000",
        "background_fit": "cover",
        "background_opacity": 1.0,
        "overlay_opacity": 0.0,
        "title": "",
        "label_1": "",
        "label_2": "",
        "label_3": "",
        "label_4": "",
        "title_color": "#E92124",
        "label_color": "#E92124",
        "cell_background_color": "#111111",
        "image_fit": "cover",
        "contain_fill_mode": "transparent",
        "crop_anchor": "center",
        "font_path": "",
        "title_font_size": 64,
        "label_font_size": 34,
        "minimum_font_size": 18,
        "max_label_lines": 2,
        "line_spacing": 8,
        "outer_margin": 64,
        "top_margin": 60,
        "bottom_margin": 54,
        "title_gap": 36,
        "block_gap": 30,
        "image_label_gap": 14,
        "inner_padding": 30,
        "corner_radius": 0,
        "border_width": 0,
        "border_color": "#E92124",
        "logo_width_percent": 18.0,
        "logo_max_height_percent": 8.0,
        "logo_opacity": 1.0,
        "logo_bottom_offset": 0,
        "invert_logo_mask": True,
        "uppercase_title": True,
        "uppercase_labels": False,
        "debug_layout": False,
        "label_padding_top": 6,
        "label_padding_bottom": 10,
        "label_after_gap": 20,
        "label_min_height": 32,
        "label_vertical_align": "center",
        "label_clip": True,
        "adaptive_strategy": "balanced",
        "adaptive_hero": "auto",
    }
    base.update(overrides)
    return base


@requires_torch
def test_node_executes_one_image_vertical_stack() -> None:
    node = HLTSlideComposer()
    (output,) = node.compose(**_compose_kwargs(title="One", label_1="A"))

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert output.dtype is torch.float32
    assert float(output.min()) >= 0.0
    assert float(output.max()) <= 1.0


@requires_torch
def test_node_executes_with_default_canvas_preset_from_input_types() -> None:
    node = HLTSlideComposer()
    inputs = HLTSlideComposer.INPUT_TYPES()
    default_preset = inputs["required"]["canvas_preset"][1]["default"]

    (output,) = node.compose(
        **_compose_kwargs(
            canvas_preset=default_preset,
            custom_width=320,
            custom_height=480,
        )
    )

    assert tuple(output.shape) == (1, 1920, 1080, 3)
    assert output.dtype is torch.float32
    assert float(output.min()) >= 0.0
    assert float(output.max()) <= 1.0


@requires_torch
def test_node_contain_transparent_preserves_background_in_letterbox_bands() -> None:
    node = HLTSlideComposer()
    (output,) = node.compose(
        **_compose_kwargs(
            background_mode="image",
            background_image=_image((0.0, 0.0, 1.0), size=(320, 480)),
            image_1=_image((1.0, 0.0, 0.0), size=(240, 80)),
            image_fit="contain",
            contain_fill_mode="transparent",
            corner_radius=0,
            border_width=0,
        )
    )

    sample = output[0, 110, 160]
    assert float(sample[2]) > 0.9
    assert float(sample[0]) < 0.1


@requires_torch
def test_node_executes_grid_and_auto_social_with_optional_images() -> None:
    node = HLTSlideComposer()

    (grid,) = node.compose(
        **_compose_kwargs(
            image_2=_image((0.0, 1.0, 0.0)),
            image_3=_image((0.0, 0.0, 1.0)),
            image_4=_image((1.0, 1.0, 0.0)),
            layout="grid_2x2",
            title="Grid",
            label_1="A",
            label_2="B",
            label_3="C",
            label_4="D",
        )
    )
    (auto,) = node.compose(
        **_compose_kwargs(
            image_2=_image((0.0, 1.0, 0.0)),
            image_3=_image((0.0, 0.0, 1.0)),
            image_4=_image((1.0, 1.0, 0.0)),
            layout="auto_social",
        )
    )

    assert tuple(grid.shape) == (1, 480, 320, 3)
    assert tuple(auto.shape) == (1, 480, 320, 3)
    assert grid.dtype is auto.dtype is torch.float32


@requires_torch
def test_node_executes_background_logo_mask_debug_and_background_size() -> None:
    node = HLTSlideComposer()
    background = _image((0.25, 0.35, 0.45), size=(77, 55))
    logo = _image((1.0, 0.0, 0.0), size=(40, 20))

    (output,) = node.compose(
        **_compose_kwargs(
            canvas_preset="Background size",
            background_image=background,
            background_mode="image_with_overlay",
            overlay_opacity=0.25,
            logo_image=logo,
            logo_mask=_mask(size=(40, 20)),
            invert_logo_mask=True,
            debug_layout=True,
        )
    )

    assert tuple(output.shape) == (1, 55, 77, 3)
    assert output.dtype is torch.float32
    assert float(output.min()) >= 0.0
    assert float(output.max()) <= 1.0


@requires_torch
def test_node_uses_first_frame_and_warns_for_larger_batches() -> None:
    node = HLTSlideComposer()
    batched = _image((1.0, 0.0, 0.0), batch=2)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        (output,) = node.compose(**_compose_kwargs(image_1=batched))

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert any("image_1 batch contains 2 frames" in str(item.message) for item in caught)


@requires_torch
def test_node_ignores_interleaved_missing_optional_images() -> None:
    node = HLTSlideComposer()
    (output,) = node.compose(
        **_compose_kwargs(
            image_2=None,
            image_3=_image((0.0, 0.0, 1.0)),
            image_4=None,
            layout="auto_social",
            label_3="C",
        )
    )

    assert tuple(output.shape) == (1, 480, 320, 3)


@requires_torch
@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_node_executes_adaptive_mosaic_with_one_to_four_ratio_mixed_images(count: int) -> None:
    node = HLTSlideComposer()
    images = (
        _pattern_image(size=(40, 40), color=(1.0, 0.0, 0.0)),
        _pattern_image(size=(64, 36), color=(0.0, 1.0, 0.0)),
        _pattern_image(size=(36, 48), color=(0.0, 0.0, 1.0)),
        _pattern_image(size=(36, 64), color=(1.0, 1.0, 0.0)),
    )
    overrides = {
        "layout": "adaptive_mosaic",
        "image_1": images[0],
        "title": "Adaptive",
        "label_1": "A",
        "image_fit": "stretch",
        "contain_fill_mode": "cell_color",
    }
    for index in range(1, count):
        overrides[f"image_{index + 1}"] = images[index]
        overrides[f"label_{index + 1}"] = chr(ord("A") + index)

    (output,) = node.compose(**_compose_kwargs(**overrides))

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert output.dtype is torch.float32
    assert float(output.min()) >= 0.0
    assert float(output.max()) <= 1.0


@requires_torch
@pytest.mark.parametrize("strategy", ["balanced", "editorial", "compact"])
def test_node_executes_adaptive_mosaic_strategies(strategy: str) -> None:
    node = HLTSlideComposer()

    (output,) = node.compose(
        **_compose_kwargs(
            layout="adaptive_mosaic",
            adaptive_strategy=strategy,
            image_1=_pattern_image(size=(40, 40), color=(1.0, 0.0, 0.0)),
            image_2=_pattern_image(size=(64, 36), color=(0.0, 1.0, 0.0)),
            image_3=_pattern_image(size=(36, 48), color=(0.0, 0.0, 1.0)),
            image_4=_pattern_image(size=(36, 64), color=(1.0, 1.0, 0.0)),
            label_1="SQUARE",
            label_2="LANDSCAPE",
            label_3="PORTRAIT",
            label_4="TALL",
        )
    )

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert output.dtype is torch.float32


@requires_torch
@pytest.mark.parametrize("hero", ["auto", "image_1", "image_2", "image_4"])
def test_node_executes_adaptive_mosaic_hero_options(hero: str) -> None:
    node = HLTSlideComposer()

    (output,) = node.compose(
        **_compose_kwargs(
            layout="adaptive_mosaic",
            adaptive_strategy="editorial",
            adaptive_hero=hero,
            image_1=_pattern_image(size=(40, 40), color=(1.0, 0.0, 0.0)),
            image_2=_pattern_image(size=(64, 36), color=(0.0, 1.0, 0.0)),
            image_3=_pattern_image(size=(36, 48), color=(0.0, 0.0, 1.0)),
            image_4=_pattern_image(size=(36, 64), color=(1.0, 1.0, 0.0)),
        )
    )

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert output.dtype is torch.float32


@requires_torch
def test_node_warns_and_uses_auto_when_adaptive_hero_image_is_disconnected() -> None:
    node = HLTSlideComposer()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        (output,) = node.compose(
            **_compose_kwargs(
                layout="adaptive_mosaic",
                adaptive_hero="image_4",
                image_2=_pattern_image(size=(64, 36), color=(0.0, 1.0, 0.0)),
                image_3=None,
                image_4=None,
            )
        )

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert any("[HLT Slide Composer]" in str(item.message) and "image_4" in str(item.message) for item in caught)


@requires_torch
def test_node_executes_adaptive_mosaic_background_overlay_logo_mask_and_debug() -> None:
    node = HLTSlideComposer()
    (output,) = node.compose(
        **_compose_kwargs(
            layout="adaptive_mosaic",
            image_1=_pattern_image(size=(40, 40), color=(1.0, 0.0, 0.0)),
            image_2=_pattern_image(size=(64, 36), color=(0.0, 1.0, 0.0)),
            image_3=_pattern_image(size=(36, 48), color=(0.0, 0.0, 1.0)),
            image_4=_pattern_image(size=(36, 64), color=(1.0, 1.0, 0.0)),
            background_mode="image_with_overlay",
            background_image=_image((0.2, 0.3, 0.5), size=(320, 480)),
            overlay_opacity=0.25,
            title="Adaptive Debug",
            label_1="A",
            label_2="B",
            label_3="C",
            label_4="D",
            logo_image=_image((1.0, 0.0, 0.0), size=(40, 20)),
            logo_mask=_mask(size=(40, 20)),
            debug_layout=True,
            border_width=2,
            corner_radius=8,
        )
    )

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert output.dtype is torch.float32
    assert float(output.min()) >= 0.0
    assert float(output.max()) <= 1.0


@requires_torch
def test_node_executes_adaptive_mosaic_with_background_size_canvas() -> None:
    node = HLTSlideComposer()
    (output,) = node.compose(
        **_compose_kwargs(
            layout="adaptive_mosaic",
            canvas_preset="Background size",
            custom_width=111,
            custom_height=222,
            background_mode="image",
            background_image=_image((0.2, 0.3, 0.5), size=(777, 555)),
            image_1=_pattern_image(size=(40, 40), color=(1.0, 0.0, 0.0)),
            image_2=_pattern_image(size=(64, 36), color=(0.0, 1.0, 0.0)),
            label_1="A",
            label_2="B",
        )
    )

    assert tuple(output.shape) == (1, 555, 777, 3)
    assert output.dtype is torch.float32
    assert float(output.min()) >= 0.0
    assert float(output.max()) <= 1.0


@requires_torch
def test_node_maps_adaptive_label_after_gap_independently_from_image_label_gap(monkeypatch) -> None:
    captured = {}

    def fake_render_adaptive_mosaic(*args, **kwargs):
        captured["adaptive_settings"] = kwargs["adaptive_settings"]
        return Image.new("RGB", (320, 480), (0, 0, 0))

    monkeypatch.setattr(nodes, "render_adaptive_mosaic", fake_render_adaptive_mosaic)

    node = HLTSlideComposer()
    (output,) = node.compose(
        **_compose_kwargs(
            layout="adaptive_mosaic",
            image_label_gap=3,
            label_after_gap=37,
            label_1="A",
        )
    )

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert captured["adaptive_settings"].label_after_gap == 37
    assert captured["adaptive_settings"].label_after_gap != 3


@requires_torch
def test_historical_layouts_keep_image_and_label_gap_settings(monkeypatch) -> None:
    captured = {}

    def fake_render_vertical_stack(*args, **kwargs):
        settings = kwargs["settings"]
        captured["image_label_gap"] = settings.image_label_gap
        captured["label_after_gap"] = settings.label_after_gap
        return Image.new("RGB", (320, 480), (0, 0, 0))

    monkeypatch.setattr(nodes, "render_vertical_stack", fake_render_vertical_stack)

    node = HLTSlideComposer()
    (output,) = node.compose(
        **_compose_kwargs(
            layout="vertical_stack",
            image_label_gap=3,
            label_after_gap=37,
            label_1="A",
        )
    )

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert captured == {"image_label_gap": 3, "label_after_gap": 37}


@requires_torch
def test_old_workflows_can_call_compose_without_adaptive_widgets() -> None:
    node = HLTSlideComposer()
    kwargs = _compose_kwargs()
    kwargs.pop("adaptive_strategy")
    kwargs.pop("adaptive_hero")

    (output,) = node.compose(**kwargs)

    assert tuple(output.shape) == (1, 480, 320, 3)


def test_public_v010_workflow_widget_values_remain_historically_aligned() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / "examples" / "workflows" / "hlt-slide-composer-grid-4-images.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    node = next(item for item in workflow["nodes"] if item["type"] == "HLTSlideComposer")
    widgets = node["widgets_values"]

    assert widgets[3] == "auto_social"
    assert widgets[48] == "center"
    assert widgets[49] is True
    assert len(widgets) >= 50
