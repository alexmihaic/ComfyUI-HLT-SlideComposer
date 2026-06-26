from __future__ import annotations

import warnings

import pytest


torch = pytest.importorskip("torch")

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
    }
    base.update(overrides)
    return base


@pytest.mark.torch
def test_node_executes_one_image_vertical_stack() -> None:
    node = HLTSlideComposer()
    (output,) = node.compose(**_compose_kwargs(title="One", label_1="A"))

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert output.dtype is torch.float32
    assert float(output.min()) >= 0.0
    assert float(output.max()) <= 1.0


@pytest.mark.torch
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


@pytest.mark.torch
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


@pytest.mark.torch
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


@pytest.mark.torch
def test_node_uses_first_frame_and_warns_for_larger_batches() -> None:
    node = HLTSlideComposer()
    batched = _image((1.0, 0.0, 0.0), batch=2)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        (output,) = node.compose(**_compose_kwargs(image_1=batched))

    assert tuple(output.shape) == (1, 480, 320, 3)
    assert any("image_1 batch contains 2 frames" in str(item.message) for item in caught)


@pytest.mark.torch
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
