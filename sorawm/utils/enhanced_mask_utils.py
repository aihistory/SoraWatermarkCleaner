"""
增强的掩码生成工具
实现自适应膨胀、边缘优化、多级掩码等高级功能
"""

import numpy as np
import cv2
from typing import Tuple, Optional, List

from sorawm.configs import (
    MASK_DILATION_KERNEL_SIZE,
    MASK_DILATION_ITERATIONS,
)


class EnhancedMaskGenerator:
    """增强的掩码生成器"""
    
    def __init__(self):
        self.bbox_history: List[Tuple[int, int, int, int]] = []
        self.mask_history: List[Optional[np.ndarray]] = []
        self._frame_shape: Optional[Tuple[int, int]] = None
    
    def reset_state(self):
        """清空历史记录，通常在处理新视频时调用。"""
        self.bbox_history.clear()
        self.mask_history.clear()
        self._frame_shape = None
    
    def _ensure_shape(self, height: int, width: int):
        """当输入尺寸变化时重置历史，避免跨视频污染。"""
        shape = (height, width)
        if self._frame_shape != shape:
            self.reset_state()
            self._frame_shape = shape
    
    def has_history(self) -> bool:
        return len(self.bbox_history) > 0
        
    def generate_adaptive_mask(
        self,
        height: int,
        width: int,
        bbox: Tuple[int, int, int, int],
        confidence: float = 1.0,
        previous_bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> np.ndarray:
        """
        生成自适应掩码
        
        Args:
            height: 图像高度
            width: 图像宽度
            bbox: 边界框坐标
            confidence: 检测置信度
            previous_bbox: 前一帧的边界框
            
        Returns:
            生成的掩码
        """
        self._ensure_shape(height, width)

        # 基础掩码
        mask = self._create_base_mask(height, width, bbox)
        
        # 自适应膨胀
        mask = self._adaptive_dilation(mask, bbox, confidence, previous_bbox)
        
        # 边缘优化
        mask = self._optimize_edges(mask, bbox)
        
        # 多级掩码处理
        mask = self._multi_level_processing(mask, confidence)
        
        return mask
    
    def _create_base_mask(
        self, 
        height: int, 
        width: int, 
        bbox: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """创建基础掩码"""
        mask = np.zeros((height, width), dtype=np.uint8)
        x1, y1, x2, y2 = bbox
        
        # 确保坐标在有效范围内
        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(x1 + 1, min(x2, width))
        y2 = max(y1 + 1, min(y2, height))
        
        mask[y1:y2, x1:x2] = 255
        return mask
    
    def _adaptive_dilation(
        self, 
        mask: np.ndarray, 
        bbox: Tuple[int, int, int, int],
        confidence: float,
        previous_bbox: Optional[Tuple[int, int, int, int]]
    ) -> np.ndarray:
        """自适应膨胀处理"""
        # 根据置信度调整膨胀强度
        if confidence >= 0.8:
            # 高置信度，使用较小的膨胀
            kernel_size = max(3, MASK_DILATION_KERNEL_SIZE - 2)
            iterations = max(1, MASK_DILATION_ITERATIONS - 1)
        elif confidence >= 0.5:
            # 中等置信度，使用标准膨胀
            kernel_size = MASK_DILATION_KERNEL_SIZE
            iterations = MASK_DILATION_ITERATIONS
        else:
            # 低置信度，使用较大的膨胀以确保覆盖
            kernel_size = MASK_DILATION_KERNEL_SIZE + 2
            iterations = MASK_DILATION_ITERATIONS + 1
        
        # 根据边界框大小调整膨胀
        bbox_w = bbox[2] - bbox[0]
        bbox_h = bbox[3] - bbox[1]
        bbox_size = max(bbox_w, bbox_h)
        
        if bbox_size < 50:
            # 小边界框，增加膨胀
            kernel_size += 2
            iterations += 1
        elif bbox_size > 200:
            # 大边界框，减少膨胀
            kernel_size = max(3, kernel_size - 2)
            iterations = max(1, iterations - 1)
        
        # 根据前一帧的边界框调整
        if previous_bbox is not None:
            # 计算边界框变化
            bbox_change = self._calculate_bbox_change(bbox, previous_bbox)
            if bbox_change > 0.3:  # 变化较大
                kernel_size += 1
                iterations += 1
        
        # 执行膨胀
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        dilated_mask = cv2.dilate(mask, kernel, iterations=iterations)
        
        return dilated_mask
    
    def _optimize_edges(
        self, 
        mask: np.ndarray, 
        bbox: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """边缘优化处理"""
        # 边缘检测
        edges = cv2.Canny(mask, 50, 150)
        
        # 边缘平滑
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # 将边缘信息融合到掩码中
        optimized_mask = cv2.bitwise_or(mask, edges)
        
        # 填充内部空洞
        contours, _ = cv2.findContours(optimized_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # 找到最大的轮廓
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 创建填充掩码
            filled_mask = np.zeros_like(mask)
            cv2.fillPoly(filled_mask, [largest_contour], 255)
            
            return filled_mask
        
        return optimized_mask
    
    def _multi_level_processing(
        self, 
        mask: np.ndarray, 
        confidence: float
    ) -> np.ndarray:
        """多级掩码处理"""
        # 根据置信度创建不同级别的掩码
        if confidence >= 0.8:
            # 高置信度：精确掩码
            return self._create_precise_mask(mask)
        elif confidence >= 0.5:
            # 中等置信度：标准掩码
            return self._create_standard_mask(mask)
        else:
            # 低置信度：保守掩码
            return self._create_conservative_mask(mask)
    
    def _create_precise_mask(self, mask: np.ndarray) -> np.ndarray:
        """创建精确掩码"""
        # 轻微膨胀以覆盖边缘
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        precise_mask = cv2.dilate(mask, kernel, iterations=1)
        
        return precise_mask
    
    def _create_standard_mask(self, mask: np.ndarray) -> np.ndarray:
        """创建标准掩码"""
        # 标准膨胀处理
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        standard_mask = cv2.dilate(mask, kernel, iterations=2)
        
        return standard_mask
    
    def _create_conservative_mask(self, mask: np.ndarray) -> np.ndarray:
        """创建保守掩码"""
        # 较大膨胀以确保覆盖
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        conservative_mask = cv2.dilate(mask, kernel, iterations=3)
        
        # 添加额外的安全边界
        kernel_safe = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        conservative_mask = cv2.dilate(conservative_mask, kernel_safe, iterations=1)
        
        return conservative_mask
    
    def _calculate_bbox_change(
        self, 
        bbox1: Tuple[int, int, int, int], 
        bbox2: Tuple[int, int, int, int]
    ) -> float:
        """计算两个边界框的变化程度"""
        # 计算中心点距离
        center1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)
        center2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)
        
        center_distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        
        # 计算尺寸变化
        size1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        size2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        
        size_ratio = abs(size1 - size2) / max(size1, size2) if max(size1, size2) > 0 else 0
        
        # 综合变化程度
        change_ratio = (center_distance / 100) + size_ratio
        
        return min(1.0, change_ratio)
    
    def generate_temporal_consistent_mask(
        self,
        height: int,
        width: int,
        bbox: Tuple[int, int, int, int],
        confidence: float,
        frame_idx: int,
        previous_bbox: Optional[Tuple[int, int, int, int]] = None,
    ) -> np.ndarray:
        """
        生成时序一致的掩码
        
        Args:
            height: 图像高度
            width: 图像宽度
            bbox: 边界框坐标
            confidence: 检测置信度
            frame_idx: 帧索引
            
        Returns:
            时序一致的掩码
        """
        self._ensure_shape(height, width)

        # 记录历史
        self.bbox_history.append(bbox)
        self.mask_history.append(None)  # 将在生成后填充
        
        # 生成当前掩码
        current_mask = self.generate_adaptive_mask(height, width, bbox, confidence, previous_bbox)
        
        # 时序一致性处理
        if len(self.bbox_history) >= 3:
            # 使用历史信息进行平滑
            smoothed_mask = self._temporal_smoothing(current_mask, frame_idx)
            current_mask = smoothed_mask
        
        # 更新历史记录
        self.mask_history[-1] = current_mask
        
        # 保持历史记录长度
        max_history = 10
        if len(self.bbox_history) > max_history:
            self.bbox_history = self.bbox_history[-max_history:]
            self.mask_history = self.mask_history[-max_history:]
        
        return current_mask
    
    def _temporal_smoothing(
        self, 
        current_mask: np.ndarray, 
        frame_idx: int
    ) -> np.ndarray:
        """时序平滑处理"""
        if len(self.mask_history) < 2:
            return current_mask
        
        # 获取最近的掩码
        recent_masks = [mask for mask in self.mask_history[-3:] if mask is not None]
        
        if len(recent_masks) < 2:
            return current_mask
        
        # 计算掩码的加权平均
        weights = [0.3, 0.4, 0.3]  # 权重分布
        smoothed_mask = np.zeros_like(current_mask, dtype=np.float32)
        
        for i, mask in enumerate(recent_masks):
            weight = weights[i] if i < len(weights) else 0.1
            smoothed_mask += mask.astype(np.float32) * weight
        
        # 当前掩码权重
        smoothed_mask += current_mask.astype(np.float32) * 0.5
        
        # 归一化并转换回uint8
        smoothed_mask = np.clip(smoothed_mask, 0, 255).astype(np.uint8)
        
        return smoothed_mask


_GLOBAL_MASK_GENERATOR = EnhancedMaskGenerator()


def build_enhanced_dilated_mask(
    height: int,
    width: int,
    bbox: Tuple[int, int, int, int],
    confidence: float = 1.0,
    previous_bbox: Optional[Tuple[int, int, int, int]] = None,
    frame_idx: int = 0,
    generator: Optional[EnhancedMaskGenerator] = None,
) -> np.ndarray:
    """
    构建增强的膨胀掩码
    
    Args:
        height: 图像高度
        width: 图像宽度
        bbox: 边界框坐标
        confidence: 检测置信度
        previous_bbox: 前一帧的边界框
        frame_idx: 帧索引
        
    Returns:
        增强的掩码
    """
    generator = generator or _GLOBAL_MASK_GENERATOR
    use_temporal = frame_idx > 0 or generator.has_history()
    
    if use_temporal:
        return generator.generate_temporal_consistent_mask(
            height,
            width,
            bbox,
            confidence,
            frame_idx,
            previous_bbox,
        )
    return generator.generate_adaptive_mask(
        height, width, bbox, confidence, previous_bbox
    )
