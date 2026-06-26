"""Pillow and NumPy image conversion helpers.

Torch is intentionally imported only inside the function that creates a Torch
tensor so this package remains importable outside ComfyUI.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image

from .exceptions import HLTSlideError, InvalidTensorError, prefixed_message


def pillow_to_numpy(image: Image.Image) -> np.ndarray:
    rgb = image.convert("RGB")
    array = np.asarray(rgb, dtype=np.float32) / 255.0
    return np.clip(array, 0.0, 1.0).astype(np.float32, copy=False)


def numpy_to_pillow(array: np.ndarray) -> Image.Image:
    normalized = _validate_hwc_rgb_array(np.asarray(array))
    clipped = np.clip(normalized, 0.0, 1.0)
    uint8 = np.rint(clipped * 255.0).astype(np.uint8)
    return Image.fromarray(uint8, mode="RGB")


def tensor_like_to_numpy(tensor_like: Any) -> np.ndarray:
    value = tensor_like
    for method_name in ("detach", "cpu", "numpy"):
        method = getattr(value, method_name, None)
        if callable(method):
            value = method()
    array = np.asarray(value)
    return _validate_bhwc_rgb_array(array)


def torch_from_numpy_image(array: np.ndarray) -> Any:
    validated = _validate_bhwc_rgb_array(np.asarray(array)).astype(np.float32, copy=False)
    try:
        import torch  # type: ignore[import-not-found]
    except ImportError as exc:
        raise HLTSlideError(
            prefixed_message(
                "Torch is required to create a ComfyUI IMAGE tensor. "
                "Run this with the Python environment provided by ComfyUI."
            )
        ) from exc
    return torch.from_numpy(validated)


def first_frame_to_pillow(tensor_like: Any) -> Image.Image:
    array = tensor_like_to_numpy(tensor_like)
    return numpy_to_pillow(array[0])


def mask_like_to_pillow(tensor_like: Any) -> Image.Image:
    value = tensor_like
    for method_name in ("detach", "cpu", "numpy"):
        method = getattr(value, method_name, None)
        if callable(method):
            value = method()
    array = np.asarray(value)
    mask = _first_mask_frame(array)
    clipped = np.clip(mask.astype(np.float32, copy=False), 0.0, 1.0)
    uint8 = np.rint(clipped * 255.0).astype(np.uint8)
    return Image.fromarray(uint8, mode="L")


def pillow_to_bhwc_numpy(image: Image.Image) -> np.ndarray:
    return pillow_to_numpy(image)[np.newaxis, ...]


def _validate_hwc_rgb_array(array: np.ndarray) -> np.ndarray:
    if array.ndim != 3 or array.shape[2] != 3:
        raise InvalidTensorError(
            prefixed_message(
                "Expected an RGB image array with shape [H, W, 3]."
            )
        )
    return array.astype(np.float32, copy=False)


def _validate_bhwc_rgb_array(array: np.ndarray) -> np.ndarray:
    if array.ndim != 4 or array.shape[3] != 3:
        raise InvalidTensorError(
            prefixed_message(
                "Expected a ComfyUI image tensor with shape [B, H, W, 3]."
            )
        )
    return np.clip(array.astype(np.float32, copy=False), 0.0, 1.0)


def _first_mask_frame(array: np.ndarray) -> np.ndarray:
    if array.ndim == 2:
        return array
    if array.ndim == 3:
        return array[0]
    if array.ndim == 4 and array.shape[3] == 1:
        return array[0, :, :, 0]
    raise InvalidTensorError(
        prefixed_message(
            "Expected a ComfyUI mask tensor with shape [B, H, W], [H, W], or [B, H, W, 1]."
        )
    )
