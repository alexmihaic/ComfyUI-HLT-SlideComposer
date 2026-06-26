"""ComfyUI integration layer for HLT Slide Composer."""

from __future__ import annotations

import warnings
from typing import Any

import numpy as np
from PIL import Image

if __package__:
    from .hlt_slide.config import (
        BACKGROUND_SIZE_PRESET_NAME,
        CUSTOM_PRESET_NAME,
        CanvasSize,
        RESOLUTION_PRESETS,
    )
    from .hlt_slide.exceptions import prefixed_message
    from .hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack
    from .hlt_slide.tensor_io import (
        mask_like_to_pillow,
        numpy_to_pillow,
        pillow_to_bhwc_numpy,
        tensor_like_to_numpy,
        torch_from_numpy_image,
    )
else:
    from hlt_slide.config import (
        BACKGROUND_SIZE_PRESET_NAME,
        CUSTOM_PRESET_NAME,
        CanvasSize,
        RESOLUTION_PRESETS,
    )
    from hlt_slide.exceptions import prefixed_message
    from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack
    from hlt_slide.tensor_io import (
        mask_like_to_pillow,
        numpy_to_pillow,
        pillow_to_bhwc_numpy,
        tensor_like_to_numpy,
        torch_from_numpy_image,
    )


NODE_NAME = "HLTSlideComposer"
NODE_DISPLAY_NAME = "HLT · Slide Composer"
NODE_CATEGORY = "HLT / Composition"


class HLTSlideComposer:
    """Thin ComfyUI node wrapper around the pure Pillow renderer."""

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("slide",)
    FUNCTION = "compose"
    CATEGORY = NODE_CATEGORY

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, Any]]:
        preset_names = tuple(preset.name for preset in RESOLUTION_PRESETS)
        return {
            "required": {
                "image_1": ("IMAGE",),
                "canvas_preset": (preset_names, {"default": "9:16 Social · 1080x1920"}),
                "custom_width": ("INT", {"default": 1080, "min": 1, "max": 8192, "step": 1}),
                "custom_height": ("INT", {"default": 1920, "min": 1, "max": 8192, "step": 1}),
                "layout": (("vertical_stack", "grid_2x2", "auto_social"), {"default": "vertical_stack"}),
                "background_mode": (("solid", "image", "image_with_overlay"), {"default": "solid"}),
                "background_color": ("STRING", {"default": "#000000"}),
                "background_fit": (("cover", "contain", "stretch"), {"default": "cover"}),
                "background_opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "overlay_opacity": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "title": ("STRING", {"default": "", "multiline": True}),
                "label_1": ("STRING", {"default": "", "multiline": True}),
                "label_2": ("STRING", {"default": "", "multiline": True}),
                "label_3": ("STRING", {"default": "", "multiline": True}),
                "label_4": ("STRING", {"default": "", "multiline": True}),
                "title_color": ("STRING", {"default": "#E92124"}),
                "label_color": ("STRING", {"default": "#E92124"}),
                "cell_background_color": ("STRING", {"default": "#111111"}),
                "image_fit": (("cover", "contain", "stretch"), {"default": "cover"}),
                "crop_anchor": (("top", "center", "bottom"), {"default": "center"}),
                "font_path": ("STRING", {"default": ""}),
                "title_font_size": ("INT", {"default": 64, "min": 8, "max": 240, "step": 1}),
                "label_font_size": ("INT", {"default": 34, "min": 8, "max": 160, "step": 1}),
                "minimum_font_size": ("INT", {"default": 18, "min": 1, "max": 120, "step": 1}),
                "max_label_lines": ("INT", {"default": 2, "min": 1, "max": 4, "step": 1}),
                "line_spacing": ("INT", {"default": 8, "min": 0, "max": 80, "step": 1}),
                "outer_margin": ("INT", {"default": 64, "min": 0, "max": 300, "step": 1}),
                "top_margin": ("INT", {"default": 60, "min": 0, "max": 300, "step": 1}),
                "bottom_margin": ("INT", {"default": 54, "min": 0, "max": 300, "step": 1}),
                "title_gap": ("INT", {"default": 36, "min": 0, "max": 160, "step": 1}),
                "block_gap": ("INT", {"default": 30, "min": 0, "max": 160, "step": 1}),
                "image_label_gap": ("INT", {"default": 14, "min": 0, "max": 100, "step": 1}),
                "inner_padding": ("INT", {"default": 30, "min": 0, "max": 160, "step": 1}),
                "corner_radius": ("INT", {"default": 18, "min": 0, "max": 160, "step": 1}),
                "border_width": ("INT", {"default": 0, "min": 0, "max": 40, "step": 1}),
                "border_color": ("STRING", {"default": "#E92124"}),
                "logo_width_percent": ("FLOAT", {"default": 18.0, "min": 0.0, "max": 100.0, "step": 0.5}),
                "logo_max_height_percent": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.5}),
                "logo_opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "logo_bottom_offset": ("INT", {"default": 0, "min": -400, "max": 400, "step": 1}),
                "invert_logo_mask": ("BOOLEAN", {"default": True}),
                "uppercase_title": ("BOOLEAN", {"default": True}),
                "uppercase_labels": ("BOOLEAN", {"default": False}),
                "debug_layout": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "background_image": ("IMAGE",),
                "logo_image": ("IMAGE",),
                "logo_mask": ("MASK",),
            },
        }

    def compose(
        self,
        image_1: Any,
        canvas_preset: str,
        custom_width: int,
        custom_height: int,
        layout: str,
        background_mode: str,
        background_color: str,
        background_fit: str,
        background_opacity: float,
        overlay_opacity: float,
        title: str,
        label_1: str,
        label_2: str,
        label_3: str,
        label_4: str,
        title_color: str,
        label_color: str,
        cell_background_color: str,
        image_fit: str,
        crop_anchor: str,
        font_path: str,
        title_font_size: int,
        label_font_size: int,
        minimum_font_size: int,
        max_label_lines: int,
        line_spacing: int,
        outer_margin: int,
        top_margin: int,
        bottom_margin: int,
        title_gap: int,
        block_gap: int,
        image_label_gap: int,
        inner_padding: int,
        corner_radius: int,
        border_width: int,
        border_color: str,
        logo_width_percent: float,
        logo_max_height_percent: float,
        logo_opacity: float,
        logo_bottom_offset: int,
        invert_logo_mask: bool,
        uppercase_title: bool,
        uppercase_labels: bool,
        debug_layout: bool,
        image_2: Any | None = None,
        image_3: Any | None = None,
        image_4: Any | None = None,
        background_image: Any | None = None,
        logo_image: Any | None = None,
        logo_mask: Any | None = None,
    ) -> tuple[Any]:
        image_pairs = (
            (image_1, label_1, "image_1"),
            (image_2, label_2, "image_2"),
            (image_3, label_3, "image_3"),
            (image_4, label_4, "image_4"),
        )
        items = [
            SlideItem(_image_tensor_to_pillow(image, name), label)
            for image, label, name in image_pairs
            if image is not None
        ]
        settings = RenderSettings(
            canvas_preset=canvas_preset,
            background_color=background_color,
            background_mode=background_mode,
            background_fit=background_fit,
            background_opacity=background_opacity,
            overlay_opacity=overlay_opacity,
            title_color=title_color,
            label_color=label_color,
            cell_background_color=cell_background_color,
            font_path=font_path.strip() or None,
            title_font_size=title_font_size,
            label_font_size=label_font_size,
            minimum_font_size=minimum_font_size,
            line_spacing=line_spacing,
            max_label_lines=max_label_lines,
            uppercase_title=uppercase_title,
            uppercase_labels=uppercase_labels,
            outer_margin=outer_margin,
            top_margin=top_margin,
            bottom_margin=bottom_margin,
            title_gap=title_gap,
            block_gap=block_gap,
            image_label_gap=image_label_gap,
            inner_padding=inner_padding,
            image_fit=image_fit,
            crop_anchor=crop_anchor,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            logo_width_percent=logo_width_percent,
            logo_max_height_percent=logo_max_height_percent,
            logo_opacity=logo_opacity,
            logo_bottom_offset=logo_bottom_offset,
            invert_logo_mask=invert_logo_mask,
            debug_layout=debug_layout,
            layout=layout,
        )
        rendered = render_vertical_stack(
            items,
            title=title,
            canvas_size=_node_canvas_size(canvas_preset, custom_width, custom_height),
            settings=settings,
            background_image=_optional_image_tensor_to_pillow(background_image, "background_image"),
            logo_image=_optional_image_tensor_to_pillow(logo_image, "logo_image"),
            logo_mask=_optional_mask_tensor_to_pillow(logo_mask, "logo_mask"),
        )
        return (torch_from_numpy_image(pillow_to_bhwc_numpy(rendered)),)


def _node_canvas_size(
    canvas_preset: str,
    custom_width: int,
    custom_height: int,
) -> CanvasSize | None:
    if canvas_preset == CUSTOM_PRESET_NAME:
        return CanvasSize(custom_width, custom_height)
    if canvas_preset == BACKGROUND_SIZE_PRESET_NAME:
        return None
    return None


def _optional_image_tensor_to_pillow(tensor_like: Any | None, name: str) -> Image.Image | None:
    if tensor_like is None:
        return None
    return _image_tensor_to_pillow(tensor_like, name)


def _image_tensor_to_pillow(tensor_like: Any, name: str) -> Image.Image:
    array = tensor_like_to_numpy(tensor_like)
    _warn_if_batched(name, array.shape[0])
    return numpy_to_pillow(array[0])


def _optional_mask_tensor_to_pillow(tensor_like: Any | None, name: str) -> Image.Image | None:
    if tensor_like is None:
        return None
    array = _tensor_like_to_array(tensor_like)
    if array.ndim >= 3:
        _warn_if_batched(name, int(array.shape[0]))
    return mask_like_to_pillow(tensor_like)


def _tensor_like_to_array(tensor_like: Any) -> np.ndarray:
    value = tensor_like
    for method_name in ("detach", "cpu", "numpy"):
        method = getattr(value, method_name, None)
        if callable(method):
            value = method()
    return np.asarray(value)


def _warn_if_batched(name: str, batch_size: int) -> None:
    if batch_size > 1:
        warnings.warn(
            prefixed_message(
                f"{name} batch contains {batch_size} frames; using the first frame."
            ),
            stacklevel=3,
        )


NODE_CLASS_MAPPINGS = {
    NODE_NAME: HLTSlideComposer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    NODE_NAME: NODE_DISPLAY_NAME,
}
