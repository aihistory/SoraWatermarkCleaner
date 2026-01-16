"""
内存管理工具模块
提供 GPU 内存监控、清理和自动调整功能
"""

import gc
import psutil
from typing import Optional, Dict, Any
import torch
from loguru import logger


class MemoryManager:
    """内存管理器，负责监控和优化内存使用"""
    
    def __init__(self, max_gpu_memory_ratio: float = 0.8, max_cpu_memory_ratio: float = 0.9):
        """
        初始化内存管理器
        
        Args:
            max_gpu_memory_ratio: GPU 内存使用率阈值
            max_cpu_memory_ratio: CPU 内存使用率阈值
        """
        self.max_gpu_memory_ratio = max_gpu_memory_ratio
        self.max_cpu_memory_ratio = max_cpu_memory_ratio
        self.gpu_available = torch.cuda.is_available()
        
        if self.gpu_available:
            self.gpu_memory_total = torch.cuda.get_device_properties(0).total_memory
            logger.info(f"GPU memory total: {self.gpu_memory_total / 1024**3:.2f} GB")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        获取当前内存使用情况
        
        Returns:
            内存信息字典
        """
        info = {
            "cpu_memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used,
                "percent": psutil.virtual_memory().percent,
            }
        }
        
        if self.gpu_available:
            gpu_memory_allocated = torch.cuda.memory_allocated()
            gpu_memory_reserved = torch.cuda.memory_reserved()
            
            info["gpu_memory"] = {
                "total": self.gpu_memory_total,
                "allocated": gpu_memory_allocated,
                "reserved": gpu_memory_reserved,
                "free": self.gpu_memory_total - gpu_memory_reserved,
                "allocated_percent": (gpu_memory_allocated / self.gpu_memory_total) * 100,
                "reserved_percent": (gpu_memory_reserved / self.gpu_memory_total) * 100,
            }
        
        return info
    
    def is_memory_pressure_high(self) -> bool:
        """
        检查是否存在内存压力
        
        Returns:
            如果内存使用率过高返回 True
        """
        # 检查 CPU 内存
        cpu_memory_percent = psutil.virtual_memory().percent / 100
        if cpu_memory_percent > self.max_cpu_memory_ratio:
            logger.warning(f"High CPU memory usage: {cpu_memory_percent:.1%}")
            return True
        
        # 检查 GPU 内存
        if self.gpu_available:
            gpu_memory_reserved = torch.cuda.memory_reserved()
            gpu_memory_percent = gpu_memory_reserved / self.gpu_memory_total
            if gpu_memory_percent > self.max_gpu_memory_ratio:
                logger.warning(f"High GPU memory usage: {gpu_memory_percent:.1%}")
                return True
        
        return False
    
    def cleanup_memory(self, force_gc: bool = True):
        """
        清理内存
        
        Args:
            force_gc: 是否强制垃圾回收
        """
        if force_gc:
            gc.collect()
        
        if self.gpu_available:
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            logger.debug("GPU memory cleaned")
        
        logger.debug("Memory cleanup completed")
    
    def get_optimal_batch_size(self, base_batch_size: int, frame_size: tuple) -> int:
        """
        根据内存情况动态调整批处理大小
        
        Args:
            base_batch_size: 基础批处理大小
            frame_size: 帧尺寸 (height, width, channels)
            
        Returns:
            优化后的批处理大小
        """
        if self.is_memory_pressure_high():
            # 内存压力高时，减少批处理大小
            optimal_size = max(1, base_batch_size // 2)
            logger.info(f"Memory pressure detected, reducing batch size to {optimal_size}")
            return optimal_size
        
        # 根据可用内存动态调整
        if self.gpu_available:
            gpu_memory_free = self.gpu_memory_total - torch.cuda.memory_reserved()
            # 估算每帧所需内存（粗略估算）
            estimated_memory_per_frame = frame_size[0] * frame_size[1] * frame_size[2] * 4  # 4 bytes per pixel
            max_batch_size = int(gpu_memory_free * 0.5 / estimated_memory_per_frame)  # 使用 50% 的可用内存
            
            optimal_size = min(base_batch_size, max_batch_size)
            if optimal_size != base_batch_size:
                logger.info(f"Adjusted batch size from {base_batch_size} to {optimal_size} based on available memory")
        else:
            # CPU 模式下，根据系统内存调整
            cpu_memory_available = psutil.virtual_memory().available
            estimated_memory_per_frame = frame_size[0] * frame_size[1] * frame_size[2] * 4
            max_batch_size = int(cpu_memory_available * 0.3 / estimated_memory_per_frame)  # 使用 30% 的可用内存
            
            optimal_size = min(base_batch_size, max_batch_size)
            if optimal_size != base_batch_size:
                logger.info(f"Adjusted batch size from {base_batch_size} to {optimal_size} based on available CPU memory")
        
        return max(1, optimal_size)
    
    def log_memory_usage(self, stage: str = ""):
        """
        记录内存使用情况
        
        Args:
            stage: 当前处理阶段名称
        """
        info = self.get_memory_info()
        
        cpu_info = info["cpu_memory"]
        logger.info(f"Memory usage {stage}: CPU {cpu_info['percent']:.1f}% "
                   f"({cpu_info['used']/1024**3:.2f}GB/{cpu_info['total']/1024**3:.2f}GB)")
        
        if "gpu_memory" in info:
            gpu_info = info["gpu_memory"]
            logger.info(f"GPU memory usage {stage}: "
                       f"Allocated {gpu_info['allocated_percent']:.1f}% "
                       f"({gpu_info['allocated']/1024**3:.2f}GB), "
                       f"Reserved {gpu_info['reserved_percent']:.1f}% "
                       f"({gpu_info['reserved']/1024**3:.2f}GB)")


# 全局内存管理器实例
memory_manager = MemoryManager()
