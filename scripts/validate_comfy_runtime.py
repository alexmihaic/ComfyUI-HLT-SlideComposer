from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image
import numpy as np
import PIL
import torch

from hlt_slide.tensor_io import pillow_to_bhwc_numpy, torch_from_numpy_image
from hlt_slide.config import CanvasSize
from hlt_slide.renderer import RenderSettings, SlideItem, render_vertical_stack


def main() -> int:
    print(f"Python {sys.version}")
    print(f"Executable {sys.executable}")
    print(f"Pillow {PIL.__version__}")
    print(f"NumPy {np.__version__}")
    print(f"Torch {torch.__version__}")

    image = Image.new("RGB", (8, 6), (10, 120, 240))
    array = pillow_to_bhwc_numpy(image)
    tensor = torch_from_numpy_image(array)

    assert tuple(tensor.shape) == (1, 6, 8, 3), tuple(tensor.shape)
    assert tensor.dtype is torch.float32, tensor.dtype
    assert tensor.device.type == "cpu", tensor.device
    assert float(tensor.min()) >= 0.0
    assert float(tensor.max()) <= 1.0

    inspected = tensor.detach().cpu().numpy()
    assert inspected.shape == (1, 6, 8, 3)
    background = Image.new("RGB", (24, 24), (60, 80, 120))
    logo = Image.new("RGBA", (20, 10), (255, 0, 0, 128))
    mask = Image.new("L", (10, 5), 255)
    rendered = render_vertical_stack(
        [SlideItem(Image.new("RGB", (16, 16), (20, 200, 80)), "OK")],
        title="RUNTIME",
        canvas_size=CanvasSize(128, 192),
        background_image=background,
        logo_image=logo,
        logo_mask=mask,
        settings=RenderSettings(
            background_mode="image_with_overlay",
            background_color="#000000",
            overlay_opacity=0.25,
            logo_width_percent=20,
            invert_logo_mask=False,
            corner_radius=0,
        ),
    )
    assert rendered.mode == "RGB"
    assert rendered.size == (128, 192)

    grid_items = [
        SlideItem(Image.new("RGB", (24, 16), (255, 0, 0)), "A"),
        SlideItem(Image.new("RGB", (16, 24), (0, 255, 0)), "B"),
        SlideItem(Image.new("RGB", (24, 16), (0, 0, 255)), "C"),
        SlideItem(Image.new("RGB", (16, 24), (255, 255, 0)), "D"),
    ]
    grid = render_vertical_stack(
        grid_items,
        title="GRID",
        canvas_size=CanvasSize(160, 240),
        background_image=background,
        logo_image=logo,
        settings=RenderSettings(
            layout="grid_2x2",
            background_mode="image_with_overlay",
            background_color="#000000",
            overlay_opacity=0.2,
            logo_width_percent=20,
            corner_radius=0,
        ),
    )
    auto = render_vertical_stack(
        grid_items,
        title="AUTO",
        canvas_size=CanvasSize(160, 240),
        background_image=background,
        logo_image=logo,
        settings=RenderSettings(
            layout="auto_social",
            background_mode="image_with_overlay",
            background_color="#000000",
            overlay_opacity=0.2,
            logo_width_percent=20,
            corner_radius=0,
        ),
    )
    assert grid.mode == auto.mode == "RGB"
    assert grid.size == auto.size == (160, 240)
    grid_tensor = torch_from_numpy_image(pillow_to_bhwc_numpy(grid))
    auto_tensor = torch_from_numpy_image(pillow_to_bhwc_numpy(auto))
    assert tuple(grid_tensor.shape) == (1, 240, 160, 3)
    assert tuple(auto_tensor.shape) == (1, 240, 160, 3)
    assert grid_tensor.dtype is torch.float32
    assert auto_tensor.dtype is torch.float32
    print("HLT Comfy runtime validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
