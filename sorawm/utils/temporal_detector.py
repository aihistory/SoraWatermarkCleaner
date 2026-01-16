"""
时序一致性检测器
用于提高水印检测的稳定性和准确性，减少闪烁现象
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import deque
from loguru import logger

from sorawm.configs import (
    DETECTION_MIN_CONFIDENCE,
    DETECTION_HIGH_CONFIDENCE,
    DETECTION_TEMPORAL_CONSISTENCY_WINDOW,
    DETECTION_MIN_CONSISTENT_FRAMES,
    DETECTION_MAX_JUMP_DISTANCE,
    BBOX_STABILITY_THRESHOLD,
)


class TemporalConsistencyDetector:
    """时序一致性检测器，用于稳定水印检测结果"""
    
    def __init__(self):
        # 检测历史记录
        self.detection_history = deque(maxlen=DETECTION_TEMPORAL_CONSISTENCY_WINDOW)
        self.bbox_history = deque(maxlen=DETECTION_TEMPORAL_CONSISTENCY_WINDOW)
        self.confidence_history = deque(maxlen=DETECTION_TEMPORAL_CONSISTENCY_WINDOW)
        
        # 状态跟踪
        self.stable_detection_count = 0
        self.last_stable_bbox = None
        self.last_stable_confidence = 0.0
        
    def process_detection(
        self, 
        detection_result: Dict[str, Any], 
        frame_idx: int
    ) -> Dict[str, Any]:
        """
        处理单帧检测结果，应用时序一致性检查
        
        Args:
            detection_result: 原始检测结果
            frame_idx: 帧索引
            
        Returns:
            经过时序一致性处理的检测结果
        """
        # 记录当前检测结果
        detected = detection_result.get("detected", False)
        bbox = detection_result.get("bbox")
        confidence = detection_result.get("confidence", 0.0)
        
        # 添加到历史记录
        self.detection_history.append(detected)
        self.bbox_history.append(bbox)
        self.confidence_history.append(confidence)
        
        # 应用时序一致性检查
        processed_result = self._apply_temporal_consistency(
            detected, bbox, confidence, frame_idx
        )
        
        return processed_result
    
    def _apply_temporal_consistency(
        self, 
        detected: bool, 
        bbox: Optional[Tuple[int, int, int, int]], 
        confidence: float,
        frame_idx: int
    ) -> Dict[str, Any]:
        """
        应用时序一致性检查
        
        Args:
            detected: 是否检测到水印
            bbox: 边界框坐标
            confidence: 检测置信度
            frame_idx: 帧索引
            
        Returns:
            处理后的检测结果
        """
        # 如果当前帧检测到水印
        if detected and bbox is not None:
            # 检查置信度是否足够高
            if confidence >= DETECTION_HIGH_CONFIDENCE:
                # 高置信度检测，直接接受
                self._update_stable_detection(bbox, confidence)
                return {
                    "detected": True,
                    "bbox": bbox,
                    "confidence": confidence,
                    "center": self._calculate_center(bbox),
                    "stable": True
                }
            
            # 中等置信度检测，需要时序验证
            elif confidence >= DETECTION_MIN_CONFIDENCE:
                # 检查时序一致性
                if self._check_temporal_consistency(bbox, confidence):
                    self._update_stable_detection(bbox, confidence)
                    return {
                        "detected": True,
                        "bbox": bbox,
                        "confidence": confidence,
                        "center": self._calculate_center(bbox),
                        "stable": True
                    }
                else:
                    # 时序不一致，使用历史稳定检测
                    if self.last_stable_bbox is not None:
                        return {
                            "detected": True,
                            "bbox": self.last_stable_bbox,
                            "confidence": self.last_stable_confidence,
                            "center": self._calculate_center(self.last_stable_bbox),
                            "stable": False,
                            "interpolated": True
                        }
        
        # 当前帧未检测到水印
        # 检查是否有稳定的历史检测
        if self.last_stable_bbox is not None:
            # 检查是否应该继续使用历史检测
            if self._should_continue_stable_detection():
                return {
                    "detected": True,
                    "bbox": self.last_stable_bbox,
                    "confidence": self.last_stable_confidence,
                    "center": self._calculate_center(self.last_stable_bbox),
                    "stable": False,
                    "interpolated": True
                }
            else:
                # 重置稳定检测状态
                self._reset_stable_detection()
        
        return {
            "detected": False,
            "bbox": None,
            "confidence": 0.0,
            "center": None,
            "stable": False
        }
    
    def _check_temporal_consistency(
        self, 
        bbox: Tuple[int, int, int, int], 
        confidence: float
    ) -> bool:
        """
        检查时序一致性
        
        Args:
            bbox: 当前检测的边界框
            confidence: 当前检测的置信度
            
        Returns:
            是否通过时序一致性检查
        """
        if len(self.bbox_history) < 2:
            return True  # 历史记录不足，接受检测
        
        # 检查边界框位置的一致性
        recent_bboxes = [b for b in self.bbox_history if b is not None]
        if len(recent_bboxes) >= DETECTION_MIN_CONSISTENT_FRAMES:
            # 计算与最近检测的距离
            distances = []
            for recent_bbox in recent_bboxes[-DETECTION_MIN_CONSISTENT_FRAMES:]:
                distance = self._calculate_bbox_distance(bbox, recent_bbox)
                distances.append(distance)
            
            # 检查距离是否在合理范围内
            max_distance = max(distances) if distances else 0
            if max_distance > DETECTION_MAX_JUMP_DISTANCE:
                logger.debug(f"Bbox jump too large: {max_distance} > {DETECTION_MAX_JUMP_DISTANCE}")
                return False
        
        # 检查置信度的稳定性
        recent_confidences = [c for c in self.confidence_history if c > 0]
        if len(recent_confidences) >= DETECTION_MIN_CONSISTENT_FRAMES:
            confidence_std = np.std(recent_confidences[-DETECTION_MIN_CONSISTENT_FRAMES:])
            if confidence_std > 0.2:  # 置信度变化过大
                logger.debug(f"Confidence too unstable: std={confidence_std}")
                return False
        
        return True
    
    def _should_continue_stable_detection(self) -> bool:
        """
        检查是否应该继续使用稳定的历史检测
        
        Returns:
            是否应该继续使用历史检测
        """
        # 检查最近几帧的检测情况
        recent_detections = list(self.detection_history)[-DETECTION_TEMPORAL_CONSISTENCY_WINDOW:]
        detection_rate = sum(recent_detections) / len(recent_detections) if recent_detections else 0
        
        # 如果检测率仍然较高，继续使用历史检测
        return detection_rate >= 0.3
    
    def _update_stable_detection(self, bbox: Tuple[int, int, int, int], confidence: float):
        """
        更新稳定检测状态
        
        Args:
            bbox: 稳定的边界框
            confidence: 稳定的置信度
        """
        self.stable_detection_count += 1
        self.last_stable_bbox = bbox
        self.last_stable_confidence = confidence
    
    def _reset_stable_detection(self):
        """重置稳定检测状态"""
        self.stable_detection_count = 0
        self.last_stable_bbox = None
        self.last_stable_confidence = 0.0
    
    def _calculate_bbox_distance(
        self, 
        bbox1: Tuple[int, int, int, int], 
        bbox2: Tuple[int, int, int, int]
    ) -> float:
        """
        计算两个边界框中心点之间的距离
        
        Args:
            bbox1: 第一个边界框
            bbox2: 第二个边界框
            
        Returns:
            中心点之间的距离
        """
        center1 = self._calculate_center(bbox1)
        center2 = self._calculate_center(bbox2)
        
        if center1 is None or center2 is None:
            return float('inf')
        
        return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def _calculate_center(self, bbox: Tuple[int, int, int, int]) -> Optional[Tuple[int, int]]:
        """
        计算边界框的中心点
        
        Args:
            bbox: 边界框坐标
            
        Returns:
            中心点坐标
        """
        if bbox is None:
            return None
        
        x1, y1, x2, y2 = bbox
        return (int((x1 + x2) / 2), int((y1 + y2) / 2))
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """
        获取检测统计信息
        
        Returns:
            检测统计信息
        """
        recent_detections = list(self.detection_history)
        recent_confidences = list(self.confidence_history)
        
        return {
            "detection_rate": sum(recent_detections) / len(recent_detections) if recent_detections else 0,
            "avg_confidence": np.mean([c for c in recent_confidences if c > 0]) if recent_confidences else 0,
            "stable_detection_count": self.stable_detection_count,
            "has_stable_detection": self.last_stable_bbox is not None,
            "history_length": len(recent_detections)
        }
