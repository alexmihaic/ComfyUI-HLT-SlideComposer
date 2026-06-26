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
    print("HLT Comfy runtime validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
