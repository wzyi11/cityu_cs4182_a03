"""Small deterministic helpers for assignment figures."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def as_uint8(image: np.ndarray) -> np.ndarray:
    """Convert a floating-point or integer image to RGB uint8."""
    array = np.asarray(image)
    if array.ndim == 2:
        array = np.repeat(array[..., None], 3, axis=-1)
    if array.shape[-1] == 4:
        array = array[..., :3]
    if np.issubdtype(array.dtype, np.floating):
        array = np.clip(array, 0.0, 1.0) * 255.0
    return np.clip(array, 0, 255).astype(np.uint8)


def save_image(path: str | Path, image: np.ndarray) -> Path:
    """Save an image and create its parent directory if necessary."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(as_uint8(image), mode="RGB").save(output)
    return output


def checkerboard(height: int, width: int, frequency: int = 12) -> np.ndarray:
    """Return a black-and-white high-frequency test image."""
    y, x = np.mgrid[:height, :width]
    pattern = ((x * frequency // max(width, 1)) + (y * frequency // max(height, 1))) % 2
    return np.repeat(pattern[..., None], 3, axis=-1).astype(float)


def load_implementation(default: str):
    """Load a student or instructor implementation selected by an environment variable."""
    import importlib
    import os

    return importlib.import_module(os.environ.get("CS4182_IMPL_MODULE", default))

