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
    print("HLT Comfy runtime validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
