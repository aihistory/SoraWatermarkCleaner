from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Dict

import cv2
import numpy as np
from loguru import logger

from sorawm.configs import (
    WATER_MARK_TEMPLATE_IMAGE_PATH,
    TEMPLATE_MATCH_SCALES,
    TEMPLATE_MATCH_MIN_SCORE,
    TEMPLATE_SEARCH_EXPANSION_RATIO,
)

BBox = Tuple[int, int, int, int]


@dataclass(frozen=True)
class TemplateVariant:
    image: np.ndarray
    scale: float
    size: Tuple[int, int]


class WatermarkTemplateMatcher:
    """Template matching helper used as a fallback when YOLO misses the watermark."""

    def __init__(self, template_path: Path | None = None):
        self.template_path = Path(template_path or WATER_MARK_TEMPLATE_IMAGE_PATH)
        self.variants: List[TemplateVariant] = []
        self._load_variants()

    def _load_variants(self) -> None:
        if not self.template_path.exists():
            logger.warning(f"Watermark template not found at {self.template_path}")
            return

        template = cv2.imread(str(self.template_path), cv2.IMREAD_UNCHANGED)
        if template is None:
            logger.warning(f"Failed to read watermark template: {self.template_path}")
            return

        if template.shape[-1] == 4:
            alpha = template[:, :, 3]
            template = cv2.cvtColor(template[:, :, :3], cv2.COLOR_BGR2GRAY)
            template = cv2.bitwise_and(template, template, mask=alpha)
        else:
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        for scale in TEMPLATE_MATCH_SCALES:
            scaled = cv2.resize(
                template,
                (0, 0),
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC if scale > 1.0 else cv2.INTER_AREA,
            )
            if scaled.size == 0 or scaled.shape[0] < 5 or scaled.shape[1] < 5:
                continue
            self.variants.append(
                TemplateVariant(image=scaled, scale=scale, size=(scaled.shape[1], scaled.shape[0]))
            )

        logger.debug(f"Loaded {len(self.variants)} watermark template variants")

    def match(
        self,
        frame: np.ndarray,
        previous_bbox: Optional[BBox] = None,
    ) -> Dict[str, Optional[object]]:
        """Try to locate the watermark via template matching."""
        if frame is None or not self.variants:
            return self._empty_result()

        frame_gray = self._to_gray(frame)
        search_region, offset = self._extract_search_region(frame_gray, previous_bbox)

        best_score = -1.0
        best_bbox: Optional[BBox] = None

        for variant in self.variants:
            if (
                search_region.shape[0] < variant.image.shape[0]
                or search_region.shape[1] < variant.image.shape[1]
            ):
                continue

            result = cv2.matchTemplate(search_region, variant.image, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > best_score:
                top_left = (max_loc[0] + offset[0], max_loc[1] + offset[1])
                bottom_right = (
                    top_left[0] + variant.size[0],
                    top_left[1] + variant.size[1],
                )
                best_bbox = (top_left[0], top_left[1], bottom_right[0], bottom_right[1])
                best_score = float(max_val)

        if best_bbox is None or best_score < TEMPLATE_MATCH_MIN_SCORE:
            return self._empty_result()

        center = (
            int((best_bbox[0] + best_bbox[2]) / 2),
            int((best_bbox[1] + best_bbox[3]) / 2),
        )

        return {
            "detected": True,
            "bbox": best_bbox,
            "confidence": best_score,
            "center": center,
            "source": "template",
        }

    @staticmethod
    def _to_gray(frame: np.ndarray) -> np.ndarray:
        if frame.ndim == 2:
            return frame
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def _extract_search_region(
        self,
        frame_gray: np.ndarray,
        previous_bbox: Optional[BBox],
    ) -> Tuple[np.ndarray, Tuple[int, int]]:
        """Crop a region of interest to speed up matching."""
        height, width = frame_gray.shape[:2]
        if previous_bbox is None:
            return frame_gray, (0, 0)

        x1, y1, x2, y2 = previous_bbox
        box_w = x2 - x1
        box_h = y2 - y1

        expand_w = int(box_w * TEMPLATE_SEARCH_EXPANSION_RATIO)
        expand_h = int(box_h * TEMPLATE_SEARCH_EXPANSION_RATIO)

        roi_x1 = max(0, x1 - expand_w)
        roi_y1 = max(0, y1 - expand_h)
        roi_x2 = min(width, x2 + expand_w)
        roi_y2 = min(height, y2 + expand_h)

        return frame_gray[roi_y1:roi_y2, roi_x1:roi_x2], (roi_x1, roi_y1)

    def _empty_result(self) -> Dict[str, Optional[object]]:
        return {
            "detected": False,
            "bbox": None,
            "confidence": 0.0,
            "center": None,
            "source": "template",
        }
