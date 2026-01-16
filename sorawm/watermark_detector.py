from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import torch
from loguru import logger
from ultralytics import YOLO

from sorawm.configs import (
    WATER_MARK_DETECT_YOLO_WEIGHTS, 
    BATCH_SIZE, 
    USE_FP16,
    DETECTION_MIN_CONFIDENCE,
    DETECTION_HIGH_CONFIDENCE,
    DETECTION_TEMPORAL_CONSISTENCY_WINDOW
)
from sorawm.utils.download_utils import download_detector_weights
from sorawm.utils.devices_utils import get_device
from sorawm.utils.video_utils import VideoLoader
from sorawm.utils.temporal_detector import TemporalConsistencyDetector
from sorawm.utils.advanced_detector import AdvancedDetectionStrategy
from sorawm.utils.missed_detection_handler import MissedDetectionHandler
from sorawm.utils.template_matching import WatermarkTemplateMatcher

# based on the sora tempalte to detect the whole, and then got the icon part area.


class SoraWaterMarkDetector:
    def __init__(self):
        download_detector_weights()
        logger.debug(f"Begin to load yolo water mark detet model.")
        self.model = YOLO(WATER_MARK_DETECT_YOLO_WEIGHTS)
        self.device = get_device()
        self.model.to(str(self.device))
        
        # 启用半精度推理（如果支持）
        if USE_FP16 and self.device.type == 'cuda':
            self.model.half()
            logger.debug("Enabled FP16 inference for YOLO model")
        
        # 模型编译优化（PyTorch 2.0+）
        self._compile_model()
        
        # 模型预热
        self._warmup_model()
        logger.debug(f"Yolo water mark detet model loaded.")

        # 初始化时序一致性检测器
        self.temporal_detector = TemporalConsistencyDetector()
        
        # 初始化高级检测策略
        self.advanced_strategy = AdvancedDetectionStrategy()
        
        # 初始化漏检处理系统
        self.missed_handler = MissedDetectionHandler()
        # 模板匹配辅助
        self.template_matcher = WatermarkTemplateMatcher()
        
        self.model.eval()

    def detect(self, input_image: np.array, frame_idx: int = 0, use_advanced: bool = True):
        """
        检测单帧图像中的水印
        
        Args:
            input_image: 输入图像
            frame_idx: 帧索引，用于时序一致性检查
            use_advanced: 是否使用高级检测策略
            
        Returns:
            检测结果字典
        """
        if use_advanced and frame_idx > 0:
            # 使用高级检测策略
            previous_bbox = None
            if hasattr(self, '_last_bbox') and self._last_bbox is not None:
                previous_bbox = self._last_bbox
            
            # 多尺度检测
            raw_result = self.advanced_strategy.multi_scale_detection(
                self, input_image, scales=[0.9, 1.0, 1.1]
            )
            
            # 如果多尺度检测失败，尝试区域增强检测
            if not raw_result["detected"] and previous_bbox is not None:
                raw_result = self.advanced_strategy.region_enhanced_detection(
                    self, input_image, previous_bbox
                )
        else:
            # 标准检测
            raw_result = self._standard_detection(input_image)
        
        raw_result = self._apply_template_assist(
            input_image, raw_result, getattr(self, "_last_bbox", None)
        )
        
        # 自适应置信度阈值调整
        if use_advanced:
            raw_result = self.advanced_strategy.confidence_adaptive_threshold(
                raw_result, frame_idx
            )
        
        # 应用时序一致性检查
        processed_result = self.temporal_detector.process_detection(raw_result, frame_idx)
        
        # 智能漏检处理
        if use_advanced:
            processed_result = self.missed_handler.process_frame(frame_idx, processed_result)
        
        # 记录最后的边界框
        if processed_result["detected"] and processed_result["bbox"] is not None:
            self._last_bbox = processed_result["bbox"]
        else:
            self._last_bbox = None
        
        return processed_result
    
    def _standard_detection(self, input_image: np.array) -> Dict[str, Any]:
        """标准检测方法"""
        # Run YOLO inference
        results = self.model(input_image, verbose=False)
        # Extract predictions from the first (and only) result
        result = results[0]

        # Check if any detections were made
        if len(result.boxes) == 0:
            return {"detected": False, "bbox": None, "confidence": 0.0, "center": None}
        else:
            # Get the first detection (highest confidence)
            box = result.boxes[0]

            # Extract bounding box coordinates (xyxy format)
            # Convert tensor to numpy, then to python float, finally to int
            xyxy = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])
            # Extract confidence score
            confidence = float(box.conf[0].cpu().numpy())
            # Calculate center point
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            return {
                "detected": True,
                "bbox": (int(x1), int(y1), int(x2), int(y2)),
                "confidence": confidence,
                "center": (int(center_x), int(center_y)),
            }

    def _compile_model(self):
        """模型编译优化（PyTorch 2.0+）"""
        try:
            if hasattr(torch, 'compile') and torch.__version__ >= "2.0":
                # 注意：YOLO 模型可能不支持直接编译，这里只是示例
                # 实际使用时需要根据具体模型结构调整
                logger.debug("PyTorch 2.0+ detected, model compilation available")
            else:
                logger.debug("PyTorch version < 2.0, skipping model compilation")
        except Exception as e:
            logger.warning(f"Model compilation failed: {e}")

    def _warmup_model(self):
        """模型预热，避免首次推理延迟"""
        try:
            dummy_input = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            with torch.no_grad():
                _ = self.model(dummy_input, verbose=False)
            logger.debug("Model warmup completed")
        except Exception as e:
            logger.warning(f"Model warmup failed: {e}")

    def detect_batch(self, input_images: List[np.ndarray], start_frame_idx: int = 0) -> List[Dict[str, Any]]:
        """
        批量检测水印，支持多帧同时推理
        
        Args:
            input_images: 输入图像列表
            start_frame_idx: 起始帧索引，用于时序一致性检查
            
        Returns:
            检测结果列表，每个元素对应一个输入图像
        """
        if not input_images:
            return []
        
        batch_size = len(input_images)
        results = []
        
        # 使用 torch.no_grad() 降低内存占用
        with torch.no_grad():
            # 批量推理
            batch_results = self.model(input_images, verbose=False)
            
            # 处理每个结果
            for i, result in enumerate(batch_results):
                frame_idx = start_frame_idx + i
                
                # 检查是否有检测结果
                if len(result.boxes) == 0:
                    raw_result = {
                        "detected": False, 
                        "bbox": None, 
                        "confidence": 0.0, 
                        "center": None
                    }
                else:
                    # 获取置信度最高的检测结果
                    box = result.boxes[0]
                    
                    # 提取边界框坐标
                    xyxy = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])
                    
                    # 提取置信度
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    # 计算中心点
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    
                    raw_result = {
                        "detected": True,
                        "bbox": (int(x1), int(y1), int(x2), int(y2)),
                        "confidence": confidence,
                        "center": (int(center_x), int(center_y)),
                    }
                
                raw_result = self._apply_template_assist(
                    input_images[i], raw_result, getattr(self, "_last_bbox", None)
                )
                
                # 应用时序一致性检查
                processed_result = self.temporal_detector.process_detection(raw_result, frame_idx)
                
                if processed_result["detected"] and processed_result["bbox"] is not None:
                    self._last_bbox = processed_result["bbox"]
                else:
                    self._last_bbox = None

                results.append(processed_result)
        
        logger.debug(f"Batch detection completed for {batch_size} images")
        return results

    def _apply_template_assist(
        self,
        frame: np.ndarray,
        detection_result: Dict[str, Any],
        previous_bbox: Optional[Tuple[int, int, int, int]] = None,
    ) -> Dict[str, Any]:
        """Augment YOLO detection with template matching when confidence is low."""
        if self.template_matcher is None:
            return detection_result

        template_result = self.template_matcher.match(frame, previous_bbox)
        if not template_result["detected"]:
            return detection_result

        if not detection_result.get("detected") or detection_result.get("bbox") is None:
            return template_result

        template_conf = float(template_result.get("confidence", 0.0))
        model_conf = float(detection_result.get("confidence", 0.0))

        # 如果模板结果明显更优，直接使用
        if template_conf - model_conf >= 0.15:
            fused = dict(template_result)
            fused["template_assisted"] = True
            return fused

        fused_bbox = self._fuse_bboxes(
            detection_result["bbox"],
            template_result["bbox"],
            model_conf,
            template_conf,
        )

        fused_confidence = max(model_conf, template_conf)
        fused = dict(detection_result)
        fused.update(
            {
                "detected": True,
                "bbox": fused_bbox,
                "confidence": fused_confidence,
                "center": (
                    int((fused_bbox[0] + fused_bbox[2]) / 2),
                    int((fused_bbox[1] + fused_bbox[3]) / 2),
                ),
                "template_score": template_conf,
                "template_assisted": True,
            }
        )
        return fused

    @staticmethod
    def _fuse_bboxes(
        bbox_a: Tuple[int, int, int, int],
        bbox_b: Tuple[int, int, int, int],
        weight_a: float,
        weight_b: float,
    ) -> Tuple[int, int, int, int]:
        """Weighted fusion of two bounding boxes."""
        total = max(weight_a + weight_b, 1e-6)
        wa = weight_a / total
        wb = weight_b / total
        fused = tuple(
            int(round(bbox_a[i] * wa + bbox_b[i] * wb))
            for i in range(4)
        )
        return fused


if __name__ == "__main__":
    from pathlib import Path

    import cv2
    from tqdm import tqdm

    # ========= 配置 =========
    # video_path = Path("resources/puppies.mp4") # 19700121_1645_68e0a027836c8191a50bea3717ea7485.mp4
    video_path = Path("resources/19700121_1645_68e0a027836c8191a50bea3717ea7485.mp4")
    save_video = True
    out_path = Path("outputs/sora_watermark_yolo_detected.mp4")
    window = "Sora Watermark YOLO Detection"
    # =======================

    # 初始化检测器
    detector = SoraWaterMarkDetector()

    # 初始化视频加载器
    video_loader = VideoLoader(video_path)

    # 预取一帧确定尺寸/FPS
    first_frame = None
    for first_frame in video_loader:
        break
    assert first_frame is not None, "无法读取视频帧"

    H, W = first_frame.shape[:2]
    fps = getattr(video_loader, "fps", 30)

    # 输出视频设置
    writer = None
    if save_video:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        writer = cv2.VideoWriter(str(out_path), fourcc, fps, (W, H))
        if not writer.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(str(out_path), fourcc, fps, (W, H))
        assert writer.isOpened(), "无法创建输出视频文件"

    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    def visualize_detection(frame, detection_result, frame_idx):
        """在帧上可视化检测结果"""
        vis = frame.copy()

        if detection_result["detected"]:
            # 绘制边界框
            x1, y1, x2, y2 = detection_result["bbox"]
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 绘制中心点
            cx, cy = detection_result["center"]
            cv2.circle(vis, (cx, cy), 5, (0, 0, 255), -1)

            # 显示置信度
            conf = detection_result["confidence"]
            label = f"Watermark: {conf:.2f}"

            # 文本背景
            (text_w, text_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            cv2.rectangle(
                vis, (x1, y1 - text_h - 10), (x1 + text_w + 5, y1), (0, 255, 0), -1
            )

            # 绘制文本
            cv2.putText(
                vis,
                label,
                (x1 + 2, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2,
            )

            status = f"Frame {frame_idx} | DETECTED | Conf: {conf:.3f}"
            status_color = (0, 255, 0)
        else:
            status = f"Frame {frame_idx} | NO WATERMARK"
            status_color = (0, 0, 255)

        # 显示帧信息
        cv2.putText(
            vis, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2
        )

        return vis

    # 处理第一帧
    print("开始处理视频...")
    detection = detector.detect(first_frame)
    vis_frame = visualize_detection(first_frame, detection, 0)
    cv2.imshow(window, vis_frame)
    if writer is not None:
        writer.write(vis_frame)

    # 处理剩余帧
    total_frames = 0
    detected_frames = 0

    for idx, frame in enumerate(
        tqdm(video_loader, desc="Processing frames", initial=1, unit="f"), start=1
    ):
        # YOLO 检测
        detection = detector.detect(frame)

        # 可视化
        vis_frame = visualize_detection(frame, detection, idx)

        # 统计
        total_frames += 1
        if detection["detected"]:
            detected_frames += 1

        # 显示
        cv2.imshow(window, vis_frame)

        # 保存
        if writer is not None:
            writer.write(vis_frame)

        # 按键控制
        key = cv2.waitKey(max(1, int(1000 / max(1, int(fps))))) & 0xFF
        if key == ord("q"):
            break
        elif key == ord(" "):  # 空格暂停
            while True:
                k = cv2.waitKey(50) & 0xFF
                if k in (ord(" "), ord("q")):
                    if k == ord("q"):
                        idx = 10**9
                    break
            if idx >= 10**9:
                break

    # 清理
    if writer is not None:
        writer.release()
        print(f"\n[完成] 可视化视频已保存: {out_path}")

    # 打印统计信息
    total_frames += 1  # 包括第一帧
    if detection["detected"]:
        detected_frames += 1

    print(f"\n=== 检测统计 ===")
    print(f"总帧数: {total_frames}")
    print(f"检测到水印: {detected_frames} 帧")
    print(f"检测率: {detected_frames/total_frames*100:.2f}%")

    cv2.destroyAllWindows()
