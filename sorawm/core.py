from pathlib import Path
from typing import Callable, List, Dict, Any, Optional
from collections import deque

import ffmpeg
import numpy as np
import torch
from loguru import logger
from tqdm import tqdm

from sorawm.configs import (
    BBOX_MIN_EDGE_PX,
    BBOX_PADDING_RATIO,
    BBOX_SMOOTHING_WINDOW,
    DETECTION_MIN_CONFIDENCE,
    MASK_DILATION_ITERATIONS,
    MASK_DILATION_KERNEL_SIZE,
    BATCH_SIZE,
    ENABLE_BATCH_PROCESSING,
    FRAME_BUFFER_SIZE,
    ENCODING_PRESET,
    ENABLE_HW_ACCEL,
)
from sorawm.utils.bbox_utils import expand_and_clip_bbox, smooth_bbox_sequence
from sorawm.utils.enhanced_bbox_utils import enhanced_smooth_bbox_sequence
from sorawm.utils.mask_utils import build_dilated_mask
from sorawm.utils.enhanced_mask_utils import (
    build_enhanced_dilated_mask,
    EnhancedMaskGenerator,
)
from sorawm.utils.video_utils import VideoLoader
from sorawm.utils.memory_utils import memory_manager
from sorawm.watermark_cleaner import WaterMarkCleaner
from sorawm.watermark_detector import SoraWaterMarkDetector
from sorawm.utils.imputation_utils import (
    find_2d_data_bkps,
    get_interval_average_bbox,
    find_idxs_interval,
)


class SoraWM:
    def __init__(self):
        self.detector = SoraWaterMarkDetector()
        self.cleaner = WaterMarkCleaner()
        self.mask_generator = EnhancedMaskGenerator()
        
        # 批处理相关属性
        self.frame_buffer = deque(maxlen=FRAME_BUFFER_SIZE)
        self.bbox_history = deque(maxlen=FRAME_BUFFER_SIZE)

    def run(
        self,
        input_video_path: Path,
        output_video_path: Path,
        progress_callback: Callable[[int], None] | None = None,
    ):
        """
        主处理方法，根据配置选择使用批处理或原始方法
        """
        if ENABLE_BATCH_PROCESSING:
            return self.run_batch(input_video_path, output_video_path, progress_callback)
        else:
            return self._run_original(input_video_path, output_video_path, progress_callback)

    def _run_original(
        self,
        input_video_path: Path,
        output_video_path: Path,
        progress_callback: Callable[[int], None] | None = None,
    ):
        input_video_loader = VideoLoader(input_video_path)
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        width = input_video_loader.width
        height = input_video_loader.height
        fps = input_video_loader.fps
        total_frames = input_video_loader.total_frames
        self.mask_generator.reset_state()

        temp_output_path = output_video_path.parent / f"temp_{output_video_path.name}"
        output_options = {
            "pix_fmt": "yuv420p",
            "vcodec": "libx264",
            "preset": ENCODING_PRESET,  # 使用配置的编码预设
        }
        
        # 硬件加速支持
        if ENABLE_HW_ACCEL:
            # 检测可用的硬件编码器
            hw_accel = self._detect_hw_encoder()
            if hw_accel:
                output_options.update(hw_accel)
                logger.info(f"Using hardware acceleration: {hw_accel}")

        if input_video_loader.original_bitrate:
            output_options["video_bitrate"] = str(
                int(int(input_video_loader.original_bitrate) * 1.2)
            )
        else:
            output_options["crf"] = "18"

        process_out = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="bgr24",
                s=f"{width}x{height}",
                r=fps,
            )
            .output(str(temp_output_path), **output_options)
            .overwrite_output()
            .global_args("-loglevel", "error")
            .run_async(pipe_stdin=True)
        )

        frame_and_mask = {}
        detect_missed = []
        bbox_centers = []
        bboxes = []

        logger.debug(
            f"total frames: {total_frames}, fps: {fps}, width: {width}, height: {height}"
        )
        for idx, frame in enumerate(
            tqdm(input_video_loader, total=total_frames, desc="Detect watermarks")
        ):
            detection_result = self.detector.detect(frame, idx)
            bbox = None
            if detection_result["detected"]:
                confidence = detection_result.get("confidence")
                if confidence is None or confidence >= DETECTION_MIN_CONFIDENCE:
                    bbox = expand_and_clip_bbox(
                        detection_result["bbox"],
                        width,
                        height,
                        padding_ratio=BBOX_PADDING_RATIO,
                        min_edge=BBOX_MIN_EDGE_PX,
                    )

            frame_and_mask[idx] = {
                "frame": frame, 
                "bbox": bbox, 
                "confidence": detection_result.get("confidence", 0.0)
            }

            if bbox is not None:
                x1, y1, x2, y2 = bbox
                bbox_centers.append((int((x1 + x2) / 2), int((y1 + y2) / 2)))
                bboxes.append((x1, y1, x2, y2))
            else:
                detect_missed.append(idx)
                bbox_centers.append(None)
                bboxes.append(None)
            # 10% - 50%
            if progress_callback and idx % 10 == 0:
                progress = 10 + int((idx / total_frames) * 40)
                progress_callback(progress)

        logger.debug(f"detect missed frames: {detect_missed}")
        # logger.debug(f"bbox centers: \n{bbox_centers}")
        if detect_missed:
            # 1. find the bkps of the bbox centers
            bkps = find_2d_data_bkps(bbox_centers)
            # add the start and end position, to form the complete interval boundaries
            bkps_full = [0] + bkps + [total_frames]
            # logger.debug(f"bkps intervals: {bkps_full}")

            # 2. calculate the average bbox of each interval
            interval_bboxes = get_interval_average_bbox(bboxes, bkps_full)
            # logger.debug(f"interval average bboxes: {interval_bboxes}")

            # 3. find the interval index of each missed frame
            missed_intervals = find_idxs_interval(detect_missed, bkps_full)
            # logger.debug(
            #     f"missed frame intervals: {list(zip(detect_missed, missed_intervals))}"
            # )

            # 4. fill the missed frames with the average bbox of the corresponding interval
            for missed_idx, interval_idx in zip(detect_missed, missed_intervals):
                if (
                    interval_idx < len(interval_bboxes)
                    and interval_bboxes[interval_idx] is not None
                ):
                    frame_and_mask[missed_idx]["bbox"] = interval_bboxes[interval_idx]
                    logger.debug(f"Filled missed frame {missed_idx} with bbox:\n"
                    f" {interval_bboxes[interval_idx]}")
                else:
                    # if the interval has no valid bbox, use the previous and next frame to complete (fallback strategy)
                    before = max(missed_idx - 1, 0)
                    after = min(missed_idx + 1, total_frames - 1)
                    before_box = frame_and_mask[before]["bbox"]
                    after_box = frame_and_mask[after]["bbox"]
                    if before_box:
                        frame_and_mask[missed_idx]["bbox"] = before_box
                    elif after_box:
                        frame_and_mask[missed_idx]["bbox"] = after_box
        else:
            del bboxes
            del bbox_centers
            del detect_missed

        # 使用增强的边界框平滑算法
        bbox_sequence = [frame_and_mask[idx]["bbox"] for idx in range(total_frames)]
        confidence_sequence = [frame_and_mask[idx].get("confidence", 0.0) for idx in range(total_frames)]
        
        smoothed_bboxes = enhanced_smooth_bbox_sequence(
            bbox_sequence,
            confidence_sequence,
            width=width,
            height=height
        )
        for idx, bbox in enumerate(smoothed_bboxes):
            frame_and_mask[idx]["bbox"] = bbox

        for idx in tqdm(range(total_frames), desc="Remove watermarks"):
            frame_info = frame_and_mask[idx]
            frame = frame_info["frame"]
            bbox = frame_info["bbox"]
            if bbox is not None:
                # 使用增强的掩码生成器
                confidence = frame_info.get("confidence", 1.0)
                previous_bbox = None
                if idx > 0:
                    previous_bbox = frame_and_mask[idx-1].get("bbox")
                
                mask = build_enhanced_dilated_mask(
                    height,
                    width,
                    bbox,
                    confidence=confidence,
                    previous_bbox=previous_bbox,
                    frame_idx=idx,
                    generator=self.mask_generator,
                )
                cleaned_frame = self.cleaner.clean(frame, mask)
            else:
                cleaned_frame = frame
            process_out.stdin.write(cleaned_frame.tobytes())

            # 50% - 95%
            if progress_callback and idx % 10 == 0:
                progress = 50 + int((idx / total_frames) * 45)
                progress_callback(progress)

        process_out.stdin.close()
        process_out.wait()

        # 95% - 99%
        if progress_callback:
            progress_callback(95)

        self.merge_audio_track(input_video_path, temp_output_path, output_video_path)

        if progress_callback:
            progress_callback(99)

    def merge_audio_track(
        self, input_video_path: Path, temp_output_path: Path, output_video_path: Path
    ):
        logger.info("Merging audio track...")
        video_stream = ffmpeg.input(str(temp_output_path))
        audio_stream = ffmpeg.input(str(input_video_path)).audio

        (
            ffmpeg.output(
                video_stream,
                audio_stream,
                str(output_video_path),
                vcodec="copy",
                acodec="aac",
            )
            .overwrite_output()
            .run(quiet=True)
        )
        # Clean up temporary file
        temp_output_path.unlink()
        logger.info(f"Saved no watermark video with audio at: {output_video_path}")

    def _detect_hw_encoder(self) -> Optional[Dict[str, str]]:
        """
        检测可用的硬件编码器
        
        Returns:
            硬件编码器配置字典，如果不可用则返回 None
        """
        try:
            # 检测 NVIDIA NVENC
            if torch.cuda.is_available():
                try:
                    # 测试 NVENC 是否可用
                    test_cmd = ffmpeg.input("testsrc=duration=1:size=320x240:rate=1", f="lavfi")
                    test_cmd.output("pipe:", vcodec="h264_nvenc", f="null").run(quiet=True, overwrite_output=True)
                    return {"vcodec": "h264_nvenc", "preset": "fast"}
                except:
                    pass
            
            # 检测 Intel QuickSync
            try:
                test_cmd = ffmpeg.input("testsrc=duration=1:size=320x240:rate=1", f="lavfi")
                test_cmd.output("pipe:", vcodec="h264_qsv", f="null").run(quiet=True, overwrite_output=True)
                return {"vcodec": "h264_qsv", "preset": "fast"}
            except:
                pass
                
            # 检测 AMD AMF
            try:
                test_cmd = ffmpeg.input("testsrc=duration=1:size=320x240:rate=1", f="lavfi")
                test_cmd.output("pipe:", vcodec="h264_amf", f="null").run(quiet=True, overwrite_output=True)
                return {"vcodec": "h264_amf", "preset": "speed"}
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Hardware encoder detection failed: {e}")
        
        return None

    def run_batch(
        self,
        input_video_path: Path,
        output_video_path: Path,
        progress_callback: Callable[[int], None] | None = None,
    ):
        """
        使用批处理流水线处理视频，显著提升性能
        
        Args:
            input_video_path: 输入视频路径
            output_video_path: 输出视频路径
            progress_callback: 进度回调函数
        """
        if not ENABLE_BATCH_PROCESSING:
            logger.info("Batch processing disabled, falling back to original method")
            return self.run(input_video_path, output_video_path, progress_callback)
        
        logger.info("Starting batch processing pipeline")
        input_video_loader = VideoLoader(input_video_path)
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        
        width = input_video_loader.width
        height = input_video_loader.height
        fps = input_video_loader.fps
        total_frames = input_video_loader.total_frames
        self.mask_generator.reset_state()
        
        # 设置输出编码参数
        temp_output_path = output_video_path.parent / f"temp_{output_video_path.name}"
        output_options = {
            "pix_fmt": "yuv420p",
            "vcodec": "libx264",
            "preset": ENCODING_PRESET,
        }
        
        # 硬件加速支持
        if ENABLE_HW_ACCEL:
            hw_accel = self._detect_hw_encoder()
            if hw_accel:
                output_options.update(hw_accel)
                logger.info(f"Using hardware acceleration: {hw_accel}")
        
        if input_video_loader.original_bitrate:
            output_options["video_bitrate"] = str(
                int(int(input_video_loader.original_bitrate) * 1.2)
            )
        else:
            output_options["crf"] = "18"
        
        # 启动 FFmpeg 输出进程
        process_out = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="bgr24",
                s=f"{width}x{height}",
                r=fps,
            )
            .output(str(temp_output_path), **output_options)
            .overwrite_output()
            .global_args("-loglevel", "error")
            .run_async(pipe_stdin=True)
        )
        
        # 记录初始内存使用情况
        memory_manager.log_memory_usage("before processing")
        
        # 动态调整批处理大小
        optimal_batch_size = memory_manager.get_optimal_batch_size(BATCH_SIZE, (height, width, 3))
        
        # 批处理流水线
        frame_batch = []
        frame_indices = []
        processed_frames = 0
        
        try:
            for idx, frame in enumerate(tqdm(input_video_loader, total=total_frames, desc="Batch processing")):
                frame_batch.append(frame)
                frame_indices.append(idx)
                
                # 当批次满了或者是最后一帧时，处理批次
                if len(frame_batch) >= optimal_batch_size or idx == total_frames - 1:
                    # 批量检测（传递起始帧索引）
                    start_frame_idx = frame_indices[0] if frame_indices else 0
                    detection_results = self.detector.detect_batch(frame_batch, start_frame_idx)
                    
                    # 批量清理
                    cleaned_frames = self._process_batch_cleaning(
                        frame_batch,
                        detection_results,
                        width,
                        height,
                        frame_indices=list(frame_indices),
                        generator=self.mask_generator,
                    )
                    
                    # 写入输出
                    for cleaned_frame in cleaned_frames:
                        process_out.stdin.write(cleaned_frame.tobytes())
                    
                    processed_frames += len(frame_batch)
                    
                    # 更新进度
                    if progress_callback:
                        progress = int((processed_frames / total_frames) * 90)  # 90% 用于处理
                        progress_callback(progress)
                    
                    # 定期清理内存
                    if processed_frames % (optimal_batch_size * 5) == 0:  # 每处理 5 个批次清理一次
                        memory_manager.cleanup_memory()
                        # 重新评估批处理大小
                        optimal_batch_size = memory_manager.get_optimal_batch_size(BATCH_SIZE, (height, width, 3))
                    
                    # 重置批次
                    frame_batch = []
                    frame_indices = []
        
        finally:
            process_out.stdin.close()
            process_out.wait()
        
        # 合并音频轨道
        if progress_callback:
            progress_callback(95)
        
        self.merge_audio_track(input_video_path, temp_output_path, output_video_path)
        
        if progress_callback:
            progress_callback(100)
        
        # 最终内存清理
        memory_manager.cleanup_memory()
        memory_manager.log_memory_usage("after processing")
        
        logger.info(f"Batch processing completed. Processed {processed_frames} frames")

    def _process_batch_cleaning(
        self, 
        frames: List[np.ndarray], 
        detection_results: List[Dict[str, Any]], 
        width: int, 
        height: int,
        frame_indices: Optional[List[int]] = None,
        generator: Optional[EnhancedMaskGenerator] = None,
    ) -> List[np.ndarray]:
        """
        批量处理帧的清理工作
        
        Args:
            frames: 输入帧列表
            detection_results: 检测结果列表
            width: 视频宽度
            height: 视频高度
            frame_indices: 每帧对应的全局索引
            generator: 可复用的掩码生成器
            
        Returns:
            清理后的帧列表
        """
        cleaned_frames = []
        masks = []
        generator = generator or self.mask_generator
        
        # 为每帧生成增强掩码
        for i, detection_result in enumerate(detection_results):
            if detection_result["detected"]:
                bbox = expand_and_clip_bbox(
                    detection_result["bbox"],
                    width,
                    height,
                    padding_ratio=BBOX_PADDING_RATIO,
                    min_edge=BBOX_MIN_EDGE_PX,
                )
                
                # 使用增强的掩码生成器
                confidence = detection_result.get("confidence", 1.0)
                previous_bbox = None
                if i > 0 and detection_results[i-1]["detected"]:
                    previous_bbox = detection_results[i-1]["bbox"]
                
                global_idx = (
                    frame_indices[i]
                    if frame_indices and i < len(frame_indices)
                    else i
                )

                mask = build_enhanced_dilated_mask(
                    height,
                    width,
                    bbox,
                    confidence=confidence,
                    previous_bbox=previous_bbox,
                    frame_idx=global_idx,
                    generator=generator,
                )
            else:
                mask = np.zeros((height, width), dtype=np.uint8)
            masks.append(mask)
        
        # 批量清理
        try:
            cleaned_frames = self.cleaner.clean_batch(frames, masks)
        except Exception as e:
            logger.error(f"Batch cleaning failed, falling back to single frame processing: {e}")
            # 回退到单帧处理
            cleaned_frames = []
            for i, (frame, mask) in enumerate(zip(frames, masks)):
                try:
                    if np.any(mask > 0):
                        cleaned_frame = self.cleaner.clean(frame, mask)
                    else:
                        cleaned_frame = frame
                    cleaned_frames.append(cleaned_frame)
                except Exception as frame_error:
                    logger.error(f"Single frame processing failed for frame {i}: {frame_error}")
                    cleaned_frames.append(frame)  # 使用原始帧作为后备
        
        return cleaned_frames


if __name__ == "__main__":
    from pathlib import Path

    input_video_path = Path(
        "resources/19700121_1645_68e0a027836c8191a50bea3717ea7485.mp4"
    )
    output_video_path = Path("outputs/sora_watermark_removed.mp4")
    sora_wm = SoraWM()
    sora_wm.run(input_video_path, output_video_path)
