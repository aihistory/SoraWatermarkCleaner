"""
高级检测策略
实现多尺度检测、置信度融合、区域增强等高级技术
"""

import numpy as np
import cv2
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from sorawm.configs import (
    DETECTION_MIN_CONFIDENCE,
    DETECTION_HIGH_CONFIDENCE,
    DETECTION_MAX_JUMP_DISTANCE,
    BBOX_PADDING_RATIO
)


class AdvancedDetectionStrategy:
    """高级检测策略，提高检测精度和稳定性"""
    
    def __init__(self):
        self.detection_history = []
        self.confidence_history = []
        self.bbox_history = []
        
    def multi_scale_detection(
        self, 
        detector, 
        image: np.ndarray, 
        scales: List[float] = [0.8, 1.0, 1.2]
    ) -> Dict[str, Any]:
        """
        多尺度检测，提高检测鲁棒性
        
        Args:
            detector: 检测器实例
            image: 输入图像
            scales: 检测尺度列表
            
        Returns:
            融合后的检测结果
        """
        detections = []
        confidences = []
        
        for scale in scales:
            # 缩放图像
            if scale != 1.0:
                h, w = image.shape[:2]
                new_h, new_w = int(h * scale), int(w * scale)
                scaled_image = cv2.resize(image, (new_w, new_h))
            else:
                scaled_image = image
            
            # 在缩放图像上检测
            result = detector.detect(scaled_image)
            
            if result["detected"] and result["bbox"] is not None:
                # 将坐标缩放回原始尺寸
                if scale != 1.0:
                    x1, y1, x2, y2 = result["bbox"]
                    original_bbox = (
                        int(x1 / scale),
                        int(y1 / scale), 
                        int(x2 / scale),
                        int(y2 / scale)
                    )
                    result["bbox"] = original_bbox
                
                detections.append(result)
                confidences.append(result["confidence"])
        
        # 融合多个检测结果
        if detections:
            return self._fuse_detections(detections, confidences)
        else:
            return {"detected": False, "bbox": None, "confidence": 0.0, "center": None}
    
    def _fuse_detections(
        self, 
        detections: List[Dict[str, Any]], 
        confidences: List[float]
    ) -> Dict[str, Any]:
        """
        融合多个检测结果
        
        Args:
            detections: 检测结果列表
            confidences: 对应的置信度列表
            
        Returns:
            融合后的检测结果
        """
        if not detections:
            return {"detected": False, "bbox": None, "confidence": 0.0, "center": None}
        
        # 计算加权平均边界框
        weighted_bbox = np.zeros(4)
        total_weight = 0
        
        for detection, confidence in zip(detections, confidences):
            bbox = detection["bbox"]
            weight = confidence ** 2  # 使用置信度的平方作为权重
            
            weighted_bbox += np.array(bbox) * weight
            total_weight += weight
        
        if total_weight > 0:
            weighted_bbox /= total_weight
            
            # 计算融合后的置信度
            fused_confidence = np.mean(confidences) + 0.1 * np.std(confidences)
            fused_confidence = min(1.0, fused_confidence)
            
            # 计算中心点
            x1, y1, x2, y2 = weighted_bbox
            center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            
            return {
                "detected": True,
                "bbox": (int(x1), int(y1), int(x2), int(y2)),
                "confidence": fused_confidence,
                "center": center,
                "multi_scale": True
            }
        else:
            return {"detected": False, "bbox": None, "confidence": 0.0, "center": None}
    
    def region_enhanced_detection(
        self, 
        detector, 
        image: np.ndarray, 
        previous_bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> Dict[str, Any]:
        """
        区域增强检测，在可能的水印区域进行重点检测
        
        Args:
            detector: 检测器实例
            image: 输入图像
            previous_bbox: 前一帧的边界框，用于区域预测
            
        Returns:
            检测结果
        """
        h, w = image.shape[:2]
        
        # 如果前一帧有检测结果，在附近区域进行增强检测
        if previous_bbox is not None:
            # 扩展搜索区域
            x1, y1, x2, y2 = previous_bbox
            expand_ratio = 0.5  # 扩展50%
            
            box_w = x2 - x1
            box_h = y2 - y1
            
            expand_x = int(box_w * expand_ratio)
            expand_y = int(box_h * expand_ratio)
            
            # 计算搜索区域
            search_x1 = max(0, x1 - expand_x)
            search_y1 = max(0, y1 - expand_y)
            search_x2 = min(w, x2 + expand_x)
            search_y2 = min(h, y2 + expand_y)
            
            # 裁剪搜索区域
            search_region = image[search_y1:search_y2, search_x1:search_x2]
            
            # 在搜索区域检测
            result = detector.detect(search_region)
            
            if result["detected"] and result["bbox"] is not None:
                # 将坐标转换回全图坐标
                bbox_x1, bbox_y1, bbox_x2, bbox_y2 = result["bbox"]
                global_bbox = (
                    bbox_x1 + search_x1,
                    bbox_y1 + search_y1,
                    bbox_x2 + search_x1,
                    bbox_y2 + search_y1
                )
                result["bbox"] = global_bbox
                
                # 提高置信度（因为是在预期区域检测到的）
                result["confidence"] = min(1.0, result["confidence"] + 0.1)
                result["region_enhanced"] = True
                
                return result
        
        # 如果区域检测失败，进行全图检测
        return detector.detect(image)
    
    def confidence_adaptive_threshold(
        self, 
        detection_result: Dict[str, Any], 
        frame_idx: int
    ) -> Dict[str, Any]:
        """
        自适应置信度阈值调整
        
        Args:
            detection_result: 检测结果
            frame_idx: 帧索引
            
        Returns:
            调整后的检测结果
        """
        # 记录检测历史
        self.detection_history.append(detection_result["detected"])
        self.confidence_history.append(detection_result["confidence"])
        if detection_result["bbox"] is not None:
            self.bbox_history.append(detection_result["bbox"])
        
        # 保持历史记录长度
        max_history = 10
        if len(self.detection_history) > max_history:
            self.detection_history = self.detection_history[-max_history:]
            self.confidence_history = self.confidence_history[-max_history:]
            self.bbox_history = self.bbox_history[-max_history:]
        
        # 计算动态阈值
        if len(self.confidence_history) >= 3:
            recent_confidences = self.confidence_history[-3:]
            avg_confidence = np.mean(recent_confidences)
            std_confidence = np.std(recent_confidences)
            
            # 动态调整阈值
            if avg_confidence > 0.5:
                # 如果最近检测置信度较高，降低阈值
                adaptive_threshold = max(DETECTION_MIN_CONFIDENCE - 0.05, 0.1)
            else:
                # 如果最近检测置信度较低，提高阈值
                adaptive_threshold = min(DETECTION_MIN_CONFIDENCE + 0.05, 0.4)
            
            # 应用自适应阈值
            if detection_result["detected"]:
                if detection_result["confidence"] >= adaptive_threshold:
                    detection_result["adaptive_threshold"] = adaptive_threshold
                    return detection_result
                else:
                    # 置信度不足，但检查是否应该保留
                    if self._should_retain_low_confidence_detection(detection_result):
                        detection_result["confidence"] = adaptive_threshold
                        detection_result["adaptive_threshold"] = adaptive_threshold
                        return detection_result
        
        return detection_result
    
    def _should_retain_low_confidence_detection(
        self, 
        detection_result: Dict[str, Any]
    ) -> bool:
        """
        判断是否应该保留低置信度检测
        
        Args:
            detection_result: 检测结果
            
        Returns:
            是否应该保留
        """
        if not detection_result["detected"] or detection_result["bbox"] is None:
            return False
        
        # 检查是否有稳定的检测历史
        if len(self.bbox_history) >= 2:
            current_bbox = detection_result["bbox"]
            last_bbox = self.bbox_history[-1]
            
            # 计算位置变化
            distance = self._calculate_bbox_distance(current_bbox, last_bbox)
            
            # 如果位置变化不大，可能是连续检测
            if distance < DETECTION_MAX_JUMP_DISTANCE * 0.5:
                return True
        
        # 检查检测率
        if len(self.detection_history) >= 5:
            recent_detection_rate = sum(self.detection_history[-5:]) / 5
            if recent_detection_rate > 0.6:  # 最近检测率较高
                return True
        
        return False
    
    def _calculate_bbox_distance(
        self, 
        bbox1: Tuple[int, int, int, int], 
        bbox2: Tuple[int, int, int, int]
    ) -> float:
        """计算两个边界框中心点之间的距离"""
        center1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)
        center2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)
        
        return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """获取检测统计信息"""
        if not self.detection_history:
            return {"detection_rate": 0, "avg_confidence": 0, "history_length": 0}
        
        return {
            "detection_rate": sum(self.detection_history) / len(self.detection_history),
            "avg_confidence": np.mean(self.confidence_history) if self.confidence_history else 0,
            "history_length": len(self.detection_history)
        }
