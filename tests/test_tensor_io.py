from __future__ import annotations

import sys

import numpy as np
import pytest
from PIL import Image

from hlt_slide.exceptions import HLTSlideError, InvalidTensorError
from hlt_slide.tensor_io import (
    numpy_to_pillow,
    pillow_to_numpy,
    tensor_like_to_numpy,
    torch_from_numpy_image,
)


def test_pillow_to_numpy_returns_float32_rgb_in_unit_range() -> None:
    image = Image.new("RGB", (2, 1))
    image.putpixel((0, 0), (0, 128, 255))
    image.putpixel((1, 0), (255, 0, 0))

    array = pillow_to_numpy(image)

    assert array.shape == (1, 2, 3)
    assert array.dtype == np.float32
    assert float(array.min()) >= 0.0
    assert float(array.max()) <= 1.0
    assert np.isclose(array[0, 0, 1], 128 / 255)


def test_numpy_to_pillow_clips_values_and_converts_to_rgb() -> None:
    array = np.array(
        [[[-1.0, 0.5, 2.0], [1.0, 0.0, 0.25]]],
        dtype=np.float32,
    )

    image = numpy_to_pillow(array)

    assert image.mode == "RGB"
    assert image.size == (2, 1)
    assert image.getpixel((0, 0)) == (0, 128, 255)
    assert image.getpixel((1, 0)) == (255, 0, 64)


def test_numpy_to_pillow_rejects_invalid_shape() -> None:
    with pytest.raises(InvalidTensorError):
        numpy_to_pillow(np.zeros((10, 10), dtype=np.float32))

    with pytest.raises(InvalidTensorError):
        numpy_to_pillow(np.zeros((10, 10, 4), dtype=np.float32))


def test_tensor_like_to_numpy_uses_detach_cpu_numpy_chain() -> None:
    class TensorLike:
        def __init__(self, array: np.ndarray) -> None:
            self.array = array
            self.calls: list[str] = []

        def detach(self) -> "TensorLike":
            self.calls.append("detach")
            return self

        def cpu(self) -> "TensorLike":
            self.calls.append("cpu")
            return self

        def numpy(self) -> np.ndarray:
            self.calls.append("numpy")
            return self.array

    tensor = TensorLike(np.zeros((1, 2, 3, 3), dtype=np.float32))
    array = tensor_like_to_numpy(tensor)

    assert array.shape == (1, 2, 3, 3)
    assert tensor.calls == ["detach", "cpu", "numpy"]


def test_tensor_like_to_numpy_validates_comfyui_image_shape() -> None:
    with pytest.raises(InvalidTensorError):
        tensor_like_to_numpy(np.zeros((2, 3, 3), dtype=np.float32))

    with pytest.raises(InvalidTensorError):
        tensor_like_to_numpy(np.zeros((1, 2, 3, 4), dtype=np.float32))


def test_torch_creation_reports_actionable_error_when_torch_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "torch", None)

    with pytest.raises(HLTSlideError, match="Torch is required"):
        torch_from_numpy_image(np.zeros((1, 2, 3, 3), dtype=np.float32))


@pytest.mark.torch
def test_torch_creation_with_real_comfyui_python() -> None:
    torch = pytest.importorskip("torch")

    tensor = torch_from_numpy_image(np.zeros((1, 2, 3, 3), dtype=np.float32))

    assert tuple(tensor.shape) == (1, 2, 3, 3)
    assert tensor.dtype is torch.float32
