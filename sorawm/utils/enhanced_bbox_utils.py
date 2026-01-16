"""
增强的边界框处理工具
提供更智能的边界框平滑和插值算法
"""

import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from collections import deque
from loguru import logger

from sorawm.configs import (
    BBOX_SMOOTHING_WINDOW,
    BBOX_STABILITY_THRESHOLD,
    BBOX_PADDING_RATIO,
    BBOX_MIN_EDGE_PX,
)


class EnhancedBBoxProcessor:
    """增强的边界框处理器，提供更智能的平滑和插值"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.bbox_history = deque(maxlen=BBOX_SMOOTHING_WINDOW)
        self.confidence_history = deque(maxlen=BBOX_SMOOTHING_WINDOW)
        self.stability_scores = deque(maxlen=BBOX_SMOOTHING_WINDOW)
        
    def process_bbox_sequence(
        self, 
        bboxes: List[Optional[Tuple[int, int, int, int]]],
        confidences: List[float]
    ) -> List[Optional[Tuple[int, int, int, int]]]:
        """
        处理边界框序列，应用增强的平滑算法
        
        Args:
            bboxes: 边界框序列
            confidences: 对应的置信度序列
            
        Returns:
            处理后的边界框序列
        """
        if not bboxes:
            return []
        
        processed_bboxes = []
        
        for i, (bbox, confidence) in enumerate(zip(bboxes, confidences)):
            # 添加到历史记录
            self.bbox_history.append(bbox)
            self.confidence_history.append(confidence)
            
            # 计算稳定性分数
            stability_score = self._calculate_stability_score()
            self.stability_scores.append(stability_score)
            
            # 应用智能平滑
            processed_bbox = self._apply_intelligent_smoothing(bbox, confidence, stability_score)
            processed_bboxes.append(processed_bbox)
        
        return processed_bboxes
    
    def _apply_intelligent_smoothing(
        self, 
        current_bbox: Optional[Tuple[int, int, int, int]], 
        confidence: float,
        stability_score: float
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        应用智能平滑算法
        
        Args:
            current_bbox: 当前边界框
            confidence: 当前置信度
            stability_score: 稳定性分数
            
        Returns:
            平滑后的边界框
        """
        if current_bbox is None:
            # 尝试从历史记录中插值
            return self._interpolate_missing_bbox()
        
        # 如果稳定性很高，直接使用当前检测
        if stability_score >= BBOX_STABILITY_THRESHOLD and confidence >= 0.6:
            return current_bbox
        
        # 应用加权平滑
        return self._apply_weighted_smoothing(current_bbox, confidence)
    
    def _apply_weighted_smoothing(
        self, 
        current_bbox: Tuple[int, int, int, int], 
        confidence: float
    ) -> Tuple[int, int, int, int]:
        """
        应用加权平滑算法
        
        Args:
            current_bbox: 当前边界框
            confidence: 当前置信度
            
        Returns:
            平滑后的边界框
        """
        # 获取有效的历史边界框
        valid_bboxes = [b for b in self.bbox_history if b is not None]
        valid_confidences = [c for c in self.confidence_history if c > 0]
        
        if len(valid_bboxes) < 2:
            return current_bbox
        
        # 计算权重（置信度越高，权重越大）
        weights = []
        for i, conf in enumerate(valid_confidences):
            # 时间衰减 + 置信度权重
            time_weight = 1.0 / (len(valid_confidences) - i)  # 越近的帧权重越大
            conf_weight = conf
            total_weight = time_weight * conf_weight
            weights.append(total_weight)
        
        # 归一化权重
        weights = np.array(weights)
        weights = weights / np.sum(weights)
        
        # 加权平均
        weighted_bbox = np.zeros(4)
        for bbox, weight in zip(valid_bboxes, weights):
            weighted_bbox += np.array(bbox) * weight
        
        # 应用自适应平滑强度
        smooth_factor = min(0.7, 1.0 - confidence)  # 置信度越低，平滑越强
        smoothed_bbox = (
            current_bbox[0] * (1 - smooth_factor) + weighted_bbox[0] * smooth_factor,
            current_bbox[1] * (1 - smooth_factor) + weighted_bbox[1] * smooth_factor,
            current_bbox[2] * (1 - smooth_factor) + weighted_bbox[2] * smooth_factor,
            current_bbox[3] * (1 - smooth_factor) + weighted_bbox[3] * smooth_factor,
        )
        
        # 确保边界框有效
        return self._ensure_valid_bbox(smoothed_bbox)
    
    def _interpolate_missing_bbox(self) -> Optional[Tuple[int, int, int, int]]:
        """
        插值缺失的边界框
        
        Returns:
            插值后的边界框，如果无法插值则返回None
        """
        valid_bboxes = [b for b in self.bbox_history if b is not None]
        
        if len(valid_bboxes) < 2:
            return None
        
        # 使用最近的两个有效边界框进行线性插值
        recent_bboxes = valid_bboxes[-2:]
        
        # 简单平均（可以改进为更复杂的插值算法）
        interpolated = np.mean(recent_bboxes, axis=0)
        
        return self._ensure_valid_bbox(interpolated)
    
    def _calculate_stability_score(self) -> float:
        """
        计算边界框序列的稳定性分数
        
        Returns:
            稳定性分数 (0-1)
        """
        valid_bboxes = [b for b in self.bbox_history if b is not None]
        
        if len(valid_bboxes) < 2:
            return 0.0
        
        # 计算边界框位置的变化
        positions = []
        for bbox in valid_bboxes:
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            positions.append([center_x, center_y])
        
        positions = np.array(positions)
        
        # 计算位置的标准差
        position_std = np.std(positions, axis=0)
        avg_std = np.mean(position_std)
        
        # 计算尺寸的变化
        sizes = []
        for bbox in valid_bboxes:
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            sizes.append([width, height])
        
        sizes = np.array(sizes)
        size_std = np.std(sizes, axis=0)
        avg_size_std = np.mean(size_std)
        
        # 计算稳定性分数（变化越小，分数越高）
        position_stability = max(0, 1 - avg_std / 50)  # 位置稳定性
        size_stability = max(0, 1 - avg_size_std / 20)  # 尺寸稳定性
        
        # 综合稳定性分数
        stability_score = (position_stability + size_stability) / 2
        
        return min(1.0, max(0.0, stability_score))
    
    def _ensure_valid_bbox(self, bbox: Tuple[float, float, float, float]) -> Tuple[int, int, int, int]:
        """
        确保边界框有效
        
        Args:
            bbox: 边界框坐标
            
        Returns:
            有效的边界框坐标
        """
        x1, y1, x2, y2 = bbox
        
        # 确保坐标顺序正确
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        # 裁剪到图像边界
        x1 = max(0, min(int(x1), self.width - 1))
        y1 = max(0, min(int(y1), self.height - 1))
        x2 = max(x1 + 1, min(int(x2), self.width))
        y2 = max(y1 + 1, min(int(y2), self.height))
        
        # 确保最小尺寸
        if x2 - x1 < BBOX_MIN_EDGE_PX:
            center_x = (x1 + x2) / 2
            x1 = max(0, int(center_x - BBOX_MIN_EDGE_PX / 2))
            x2 = min(self.width, int(center_x + BBOX_MIN_EDGE_PX / 2))
        
        if y2 - y1 < BBOX_MIN_EDGE_PX:
            center_y = (y1 + y2) / 2
            y1 = max(0, int(center_y - BBOX_MIN_EDGE_PX / 2))
            y2 = min(self.height, int(center_y + BBOX_MIN_EDGE_PX / 2))
        
        return (int(x1), int(y1), int(x2), int(y2))
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        获取处理统计信息
        
        Returns:
            处理统计信息
        """
        valid_bboxes = [b for b in self.bbox_history if b is not None]
        valid_confidences = [c for c in self.confidence_history if c > 0]
        
        return {
            "total_frames": len(self.bbox_history),
            "detected_frames": len(valid_bboxes),
            "detection_rate": len(valid_bboxes) / len(self.bbox_history) if self.bbox_history else 0,
            "avg_confidence": np.mean(valid_confidences) if valid_confidences else 0,
            "avg_stability": np.mean(self.stability_scores) if self.stability_scores else 0,
            "current_stability": self.stability_scores[-1] if self.stability_scores else 0
        }


def enhanced_smooth_bbox_sequence(
    bboxes: List[Optional[Tuple[int, int, int, int]]],
    confidences: List[float],
    width: int,
    height: int
) -> List[Optional[Tuple[int, int, int, int]]]:
    """
    增强的边界框序列平滑函数
    
    Args:
        bboxes: 边界框序列
        confidences: 对应的置信度序列
        width: 图像宽度
        height: 图像高度
        
    Returns:
        平滑后的边界框序列
    """
    processor = EnhancedBBoxProcessor(width, height)
    return processor.process_bbox_sequence(bboxes, confidences)
