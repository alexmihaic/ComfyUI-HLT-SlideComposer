from __future__ import annotations

import warnings

import pytest

try:
    import torch
except ImportError:
    torch = None

from nodes import HLTTextComposer


requires_torch = pytest.mark.skipif(torch is None, reason="torch is required for node execution tests")


def _image(color: tuple[float, float, float], *, size: tuple[int, int] = (32, 24), batch: int = 1):
    width, height = size
    tensor = torch.zeros((batch, height, width, 3), dtype=torch.float32)
    tensor[:, :, :, 0] = color[0]
    tensor[:, :, :, 1] = color[1]
    tensor[:, :, :, 2] = color[2]
    return tensor


def _mask(*, size: tuple[int, int] = (32, 24), batch: int = 1):
    width, height = size
    return torch.ones((batch, height, width), dtype=torch.float32)


def _kwargs(**overrides):
    base = {
        "text_1": "YOUR TEXT",
        "text_2": "",
        "text_3": "",
        "text_4": "",
        "canvas_preset": "Custom",
        "custom_width": 320,
        "custom_height": 480,
        "layout": "auto_text",
        "text_1_role": "headline",
        "text_2_role": "headline",
        "text_3_role": "headline",
        "text_4_role": "headline",
        "split_axis": "auto",
        "background_mode": "solid",
        "background_color": "#000000",
        "background_fit": "cover",
        "background_opacity": 1.0,
        "overlay_opacity": 0.0,
        "text_color": "#F3F0E8",
        "accent_color": "#E92124",
        "accent_target": "none",
        "font_path": "",
        "font_scale": 1.0,
        "horizontal_align": "auto",
        "vertical_align": "auto",
        "uppercase": False,
        "preserve_words": True,
        "clipping": True,
        "outer_margin": 64,
        "top_margin": 60,
        "bottom_margin": 54,
        "block_gap": 30,
        "inner_padding": 30,
        "logo_width_percent": 18.0,
        "logo_max_height_percent": 8.0,
        "logo_opacity": 1.0,
        "logo_bottom_offset": 0,
        "invert_logo_mask": True,
        "reserve_logo_space": True,
        "logo_gap": 24,
        "debug_layout": False,
    }
    base.update(overrides)
    return base


def _assert_tensor(output, size: tuple[int, int]) -> None:
    width, height = size
    assert tuple(output.shape) == (1, height, width, 3)
    assert output.dtype is torch.float32
    assert output.device.type == "cpu"
    assert float(output.min()) >= 0.0
    assert float(output.max()) <= 1.0


@requires_torch
@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_text_node_executes_auto_text_counts(count: int) -> None:
    overrides = {f"text_{index}": f"TEXT {index}" for index in range(1, count + 1)}
    (output,) = HLTTextComposer().compose(**_kwargs(**overrides))
    _assert_tensor(output, (320, 480))


@requires_torch
@pytest.mark.parametrize("layout", ["centered_statement", "vertical_stack", "split_2", "grid_2x2", "editorial_quote"])
def test_text_node_executes_explicit_layouts(layout: str) -> None:
    texts = {"centered_statement": ("ONE", "", "", ""), "editorial_quote": ("QUOTE", "AUTHOR", "", "")}.get(
        layout, ("ONE", "TWO", "THREE", "FOUR")
    )
    if layout == "split_2":
        texts = ("ONE", "TWO", "", "")
    (output,) = HLTTextComposer().compose(
        **_kwargs(layout=layout, text_1=texts[0], text_2=texts[1], text_3=texts[2], text_4=texts[3])
    )
    _assert_tensor(output, (320, 480))


@requires_torch
@pytest.mark.parametrize("role", ["headline", "subheadline", "body", "quote", "caption", "number", "label"])
def test_text_node_executes_roles(role: str) -> None:
    (output,) = HLTTextComposer().compose(**_kwargs(text_1_role=role))
    _assert_tensor(output, (320, 480))


@requires_torch
def test_text_node_executes_options_background_logo_debug_and_background_size() -> None:
    (output,) = HLTTextComposer().compose(
        **_kwargs(
            text_1="uno",
            text_2="dos",
            text_3="tres",
            canvas_preset="Background size",
            background_mode="image_with_overlay",
            background_image=_image((0.2, 0.3, 0.5), size=(320, 480)),
            background_opacity=0.8,
            overlay_opacity=0.2,
            logo_image=_image((1.0, 0.0, 0.0), size=(40, 20)),
            logo_mask=_mask(size=(40, 20)),
            accent_target="text_1",
            uppercase=True,
            horizontal_align="center",
            vertical_align="top",
            clipping=True,
            debug_layout=True,
        )
    )
    _assert_tensor(output, (320, 480))


@requires_torch
def test_text_node_warnings_and_errors_use_text_prefix() -> None:
    node = HLTTextComposer()
    with pytest.raises(ValueError, match=r"\[HLT Text Composer\].*at least one active"):
        node.compose(**_kwargs(text_1="", text_2="", text_3="", text_4=""))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        (output,) = node.compose(
            **_kwargs(
                text_1="A",
                text_2="",
                accent_target="text_2",
                background_image=_image((0.1, 0.2, 0.3), batch=2),
                logo_image=_image((1.0, 0.0, 0.0), batch=2),
                logo_mask=_mask(batch=2),
            )
        )
    _assert_tensor(output, (320, 480))
    messages = [str(item.message) for item in caught]
    assert any("[HLT Text Composer] accent_target='text_2'" in message for message in messages)
    assert any("[HLT Text Composer] background_image batch contains 2 frames" in message for message in messages)
    assert any("[HLT Text Composer] logo_image batch contains 2 frames" in message for message in messages)
    assert any("[HLT Text Composer] logo_mask batch contains 2 frames" in message for message in messages)
