from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

import numpy as np


BBox = Tuple[int, int, int, int]


def expand_and_clip_bbox(
    bbox: BBox,
    width: int,
    height: int,
    padding_ratio: float = 0.0,
    min_edge: int = 0,
) -> BBox:
    """Expand a bounding box by a padding ratio and clamp it to image bounds."""
    x1, y1, x2, y2 = bbox
    box_w = max(0, x2 - x1)
    box_h = max(0, y2 - y1)

    pad_x = int(round(box_w * padding_ratio))
    pad_y = int(round(box_h * padding_ratio))

    nx1 = max(0, x1 - pad_x)
    ny1 = max(0, y1 - pad_y)
    nx2 = min(width, x2 + pad_x)
    ny2 = min(height, y2 + pad_y)

    nx1, ny1, nx2, ny2 = _ensure_min_edge(nx1, ny1, nx2, ny2, width, height, min_edge)

    return int(nx1), int(ny1), int(nx2), int(ny2)


def smooth_bbox_sequence(
    bboxes: Iterable[Optional[BBox]],
    width: int,
    height: int,
    window: int = 5,
) -> List[Optional[BBox]]:
    """Apply a simple moving-average smoothing to a sequence of bounding boxes."""
    bbox_list = list(bboxes)
    if window <= 1 or not bbox_list:
        return bbox_list

    filled = _forward_backward_fill(bbox_list)
    if all(item is None for item in filled):
        return bbox_list

    half = window // 2
    smoothed: List[Optional[BBox]] = []

    for idx, bbox in enumerate(filled):
        if bbox is None:
            smoothed.append(None)
            continue

        start = max(0, idx - half)
        end = min(len(filled), idx + half + 1)

        neighbours = [filled[i] for i in range(start, end) if filled[i] is not None]
        if not neighbours:
            smoothed.append(tuple(map(int, bbox)))
            continue

        mean_box = np.mean(neighbours, axis=0)
        mean_box = _clip_bbox(mean_box, width, height)

        smoothed.append(
            (
                int(round(mean_box[0])),
                int(round(mean_box[1])),
                int(round(mean_box[2])),
                int(round(mean_box[3])),
            )
        )

    return smoothed


def _forward_backward_fill(
    bboxes: Iterable[Optional[BBox]],
) -> List[Optional[np.ndarray]]:
    forward: List[Optional[np.ndarray]] = []
    last_valid: Optional[np.ndarray] = None

    # Forward fill
    for bbox in bboxes:
        if bbox is not None:
            last_valid = np.array(bbox, dtype=float)
        forward.append(
            None if last_valid is None else np.array(last_valid, dtype=float)
        )

    # Backward fill
    last_valid = None
    for idx in range(len(forward) - 1, -1, -1):
        if forward[idx] is not None:
            last_valid = forward[idx]
        elif last_valid is not None:
            forward[idx] = np.array(last_valid, dtype=float)

    return forward


def _clip_bbox(bbox: np.ndarray, width: int, height: int) -> np.ndarray:
    bbox[0] = np.clip(bbox[0], 0, width - 1)
    bbox[2] = np.clip(bbox[2], bbox[0] + 1, width)
    bbox[1] = np.clip(bbox[1], 0, height - 1)
    bbox[3] = np.clip(bbox[3], bbox[1] + 1, height)
    return bbox


def _ensure_min_edge(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    width: int,
    height: int,
    min_edge: int,
) -> Tuple[int, int, int, int]:
    if min_edge <= 0:
        return x1, y1, x2, y2

    box_w = x2 - x1
    box_h = y2 - y1

    if box_w < min_edge:
        extra = min_edge - box_w
        x1 = max(0, x1 - (extra + 1) // 2)
        x2 = min(width, x2 + extra // 2 + 1)

    if box_h < min_edge:
        extra = min_edge - box_h
        y1 = max(0, y1 - (extra + 1) // 2)
        y2 = min(height, y2 + extra // 2 + 1)

    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(x1 + 1, min(x2, width))
    y2 = max(y1 + 1, min(y2, height))

    return x1, y1, x2, y2
