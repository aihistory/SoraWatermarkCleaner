from __future__ import annotations

import numpy as np
import cv2

from typing import Tuple


def build_dilated_mask(
    height: int,
    width: int,
    bbox: Tuple[int, int, int, int],
    kernel_size: int = 5,
    iterations: int = 1,
) -> np.ndarray:
    """Create a binary mask for the bbox and dilate it to cover watermark fringes."""
    mask = np.zeros((height, width), dtype=np.uint8)
    x1, y1, x2, y2 = bbox
    mask[y1:y2, x1:x2] = 255

    kernel_size = max(1, kernel_size)
    if kernel_size % 2 == 0:
        kernel_size += 1

    if kernel_size > 1 and iterations > 0:
        kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=iterations)

    return mask
