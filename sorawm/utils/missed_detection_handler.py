"""
智能漏检处理系统
实现上下文感知的漏检检测和智能插值
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import deque
from loguru import logger

from sorawm.configs import (
    DETECTION_MAX_JUMP_DISTANCE,
    BBOX_PADDING_RATIO,
    BBOX_MIN_EDGE_PX
)


class MissedDetectionHandler:
    """智能漏检处理系统"""
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.detection_history = deque(maxlen=max_history)
        self.bbox_history = deque(maxlen=max_history)
        self.confidence_history = deque(maxlen=max_history)
        self.frame_indices = deque(maxlen=max_history)
        
        # 预测模型参数
        self.velocity_history = deque(maxlen=5)
        self.acceleration_history = deque(maxlen=3)
        
    def process_frame(
        self, 
        frame_idx: int, 
        detection_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理单帧检测结果，处理漏检情况
        
        Args:
            frame_idx: 帧索引
            detection_result: 检测结果
            
        Returns:
            处理后的检测结果
        """
        # 记录历史
        self.detection_history.append(detection_result["detected"])
        self.bbox_history.append(detection_result["bbox"])
        self.confidence_history.append(detection_result["confidence"])
        self.frame_indices.append(frame_idx)
        
        # 如果当前帧检测到水印，更新运动模型
        if detection_result["detected"] and detection_result["bbox"] is not None:
            self._update_motion_model(detection_result["bbox"])
            return detection_result
        
        # 如果当前帧未检测到，尝试智能插值
        interpolated_result = self._intelligent_interpolation(frame_idx)
        if interpolated_result is not None:
            logger.debug(f"Interpolated detection for frame {frame_idx}")
            return interpolated_result
        
        return detection_result
    
    def _update_motion_model(self, bbox: Tuple[int, int, int, int]):
        """更新运动模型"""
        if len(self.bbox_history) >= 2:
            current_bbox = bbox
            previous_bbox = self.bbox_history[-2]
            
            if previous_bbox is not None:
                # 计算速度（中心点位移）
                current_center = self._get_bbox_center(current_bbox)
                previous_center = self._get_bbox_center(previous_bbox)
                
                velocity = (
                    current_center[0] - previous_center[0],
                    current_center[1] - previous_center[1]
                )
                self.velocity_history.append(velocity)
                
                # 计算加速度
                if len(self.velocity_history) >= 2:
                    current_vel = self.velocity_history[-1]
                    previous_vel = self.velocity_history[-2]
                    
                    acceleration = (
                        current_vel[0] - previous_vel[0],
                        current_vel[1] - previous_vel[1]
                    )
                    self.acceleration_history.append(acceleration)
    
    def _intelligent_interpolation(self, frame_idx: int) -> Optional[Dict[str, Any]]:
        """
        智能插值处理漏检
        
        Args:
            frame_idx: 当前帧索引
            
        Returns:
            插值后的检测结果，如果无法插值则返回None
        """
        # 检查是否有足够的历史数据
        if len(self.detection_history) < 3:
            return None
        
        # 检查最近的检测情况
        recent_detections = list(self.detection_history)[-5:]
        detection_rate = sum(recent_detections) / len(recent_detections)
        
        # 如果最近检测率太低，不进行插值
        if detection_rate < 0.3:
            return None
        
        # 尝试多种插值策略
        interpolated_bbox = None
        
        # 策略1：基于运动模型的预测
        predicted_bbox = self._predict_bbox_by_motion()
        if predicted_bbox is not None:
            interpolated_bbox = predicted_bbox
        
        # 策略2：基于历史平均的插值
        if interpolated_bbox is None:
            interpolated_bbox = self._interpolate_by_average()
        
        # 策略3：基于最近检测的扩展
        if interpolated_bbox is None:
            interpolated_bbox = self._interpolate_by_recent()
        
        if interpolated_bbox is not None:
            # 计算插值置信度
            confidence = self._calculate_interpolation_confidence()
            
            return {
                "detected": True,
                "bbox": interpolated_bbox,
                "confidence": confidence,
                "center": self._get_bbox_center(interpolated_bbox),
                "interpolated": True,
                "interpolation_method": "intelligent"
            }
        
        return None
    
    def _predict_bbox_by_motion(self) -> Optional[Tuple[int, int, int, int]]:
        """基于运动模型预测边界框"""
        if len(self.bbox_history) < 2 or len(self.velocity_history) < 1:
            return None
        
        last_bbox = self.bbox_history[-1]
        if last_bbox is None:
            return None
        
        # 计算平均速度
        if len(self.velocity_history) >= 2:
            avg_velocity = (
                np.mean([v[0] for v in self.velocity_history]),
                np.mean([v[1] for v in self.velocity_history])
            )
        else:
            avg_velocity = self.velocity_history[-1]
        
        # 计算平均加速度
        avg_acceleration = (0, 0)
        if len(self.acceleration_history) >= 2:
            avg_acceleration = (
                np.mean([a[0] for a in self.acceleration_history]),
                np.mean([a[1] for a in self.acceleration_history])
            )
        
        # 预测下一个位置
        last_center = self._get_bbox_center(last_bbox)
        predicted_center = (
            int(last_center[0] + avg_velocity[0] + avg_acceleration[0] * 0.5),
            int(last_center[1] + avg_velocity[1] + avg_acceleration[1] * 0.5)
        )
        
        # 计算边界框尺寸
        bbox_w = last_bbox[2] - last_bbox[0]
        bbox_h = last_bbox[3] - last_bbox[1]
        
        # 生成预测边界框
        predicted_bbox = (
            predicted_center[0] - bbox_w // 2,
            predicted_center[1] - bbox_h // 2,
            predicted_center[0] + bbox_w // 2,
            predicted_center[1] + bbox_h // 2
        )
        
        # 验证预测的合理性
        if self._is_valid_prediction(predicted_bbox, last_bbox):
            return predicted_bbox
        
        return None
    
    def _interpolate_by_average(self) -> Optional[Tuple[int, int, int, int]]:
        """基于历史平均进行插值"""
        valid_bboxes = [bbox for bbox in self.bbox_history if bbox is not None]
        
        if len(valid_bboxes) < 2:
            return None
        
        # 使用最近的几个有效边界框进行平均
        recent_bboxes = valid_bboxes[-3:]
        
        # 计算加权平均（越近的权重越大）
        weights = [i + 1 for i in range(len(recent_bboxes))]
        total_weight = sum(weights)
        
        weighted_bbox = np.zeros(4)
        for bbox, weight in zip(recent_bboxes, weights):
            weighted_bbox += np.array(bbox) * weight
        
        weighted_bbox /= total_weight
        
        return (
            int(weighted_bbox[0]),
            int(weighted_bbox[1]),
            int(weighted_bbox[2]),
            int(weighted_bbox[3])
        )
    
    def _interpolate_by_recent(self) -> Optional[Tuple[int, int, int, int]]:
        """基于最近检测进行插值"""
        # 找到最近的检测
        for i in range(len(self.bbox_history) - 1, -1, -1):
            if self.bbox_history[i] is not None:
                return self.bbox_history[i]
        
        return None
    
    def _calculate_interpolation_confidence(self) -> float:
        """计算插值置信度"""
        # 基于历史检测率计算置信度
        if len(self.detection_history) < 3:
            return 0.3
        
        recent_detection_rate = sum(list(self.detection_history)[-5:]) / min(5, len(self.detection_history))
        
        # 基于历史置信度
        recent_confidences = [c for c in self.confidence_history if c > 0]
        avg_confidence = np.mean(recent_confidences) if recent_confidences else 0.5
        
        # 综合计算插值置信度
        interpolation_confidence = (recent_detection_rate * 0.6 + avg_confidence * 0.4) * 0.8
        
        return max(0.2, min(0.8, interpolation_confidence))
    
    def _is_valid_prediction(
        self, 
        predicted_bbox: Tuple[int, int, int, int], 
        last_bbox: Tuple[int, int, int, int]
    ) -> bool:
        """验证预测的合理性"""
        # 检查边界框尺寸是否合理
        pred_w = predicted_bbox[2] - predicted_bbox[0]
        pred_h = predicted_bbox[3] - predicted_bbox[1]
        last_w = last_bbox[2] - last_bbox[0]
        last_h = last_bbox[3] - last_bbox[1]
        
        # 尺寸变化不应过大
        size_ratio_w = pred_w / last_w if last_w > 0 else 1
        size_ratio_h = pred_h / last_h if last_h > 0 else 1
        
        if size_ratio_w < 0.5 or size_ratio_w > 2.0 or size_ratio_h < 0.5 or size_ratio_h > 2.0:
            return False
        
        # 检查位置变化是否合理
        pred_center = self._get_bbox_center(predicted_bbox)
        last_center = self._get_bbox_center(last_bbox)
        
        distance = np.sqrt((pred_center[0] - last_center[0])**2 + (pred_center[1] - last_center[1])**2)
        
        return distance <= DETECTION_MAX_JUMP_DISTANCE * 1.5
    
    def _get_bbox_center(self, bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """获取边界框中心点"""
        return ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        if not self.detection_history:
            return {"detection_rate": 0, "interpolation_count": 0}
        
        detection_rate = sum(self.detection_history) / len(self.detection_history)
        interpolation_count = sum(1 for i, detected in enumerate(self.detection_history) 
                                if not detected and i > 0 and self.detection_history[i-1])
        
        return {
            "detection_rate": detection_rate,
            "interpolation_count": interpolation_count,
            "history_length": len(self.detection_history),
            "motion_model_ready": len(self.velocity_history) >= 2
        }
