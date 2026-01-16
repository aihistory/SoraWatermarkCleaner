"""
性能基准测试工具
用于测试和对比优化前后的性能提升
"""

import time
import psutil
import torch
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import numpy as np
from loguru import logger

from sorawm.core import SoraWM
from sorawm.configs import BATCH_SIZE, ENABLE_BATCH_PROCESSING
from sorawm.utils.memory_utils import memory_manager


class PerformanceBenchmark:
    """性能基准测试类"""
    
    def __init__(self, test_video_path: Path, output_dir: Path):
        """
        初始化性能测试
        
        Args:
            test_video_path: 测试视频路径
            output_dir: 输出目录
        """
        self.test_video_path = test_video_path
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # 测试结果存储
        self.results = {
            "test_info": {
                "video_path": str(test_video_path),
                "timestamp": datetime.now().isoformat(),
                "system_info": self._get_system_info(),
            },
            "tests": []
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        info = {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "python_version": torch.__version__,
            "pytorch_version": torch.__version__,
        }
        
        if torch.cuda.is_available():
            info.update({
                "cuda_available": True,
                "cuda_version": torch.version.cuda,
                "gpu_count": torch.cuda.device_count(),
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_memory": torch.cuda.get_device_properties(0).total_memory,
            })
        else:
            info["cuda_available"] = False
        
        return info
    
    def run_single_test(
        self, 
        test_name: str, 
        use_batch_processing: bool = True,
        batch_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        运行单个性能测试
        
        Args:
            test_name: 测试名称
            use_batch_processing: 是否使用批处理
            batch_size: 批处理大小（None 表示使用默认值）
            
        Returns:
            测试结果字典
        """
        logger.info(f"Running test: {test_name}")
        
        # 设置测试参数
        original_batch_processing = ENABLE_BATCH_PROCESSING
        original_batch_size = BATCH_SIZE
        
        try:
            # 临时修改配置
            import sorawm.configs as configs
            configs.ENABLE_BATCH_PROCESSING = use_batch_processing
            if batch_size is not None:
                configs.BATCH_SIZE = batch_size
            
            # 准备输出路径
            output_path = self.output_dir / f"{test_name}_output.mp4"
            
            # 记录开始时间和内存
            start_time = time.time()
            start_memory = memory_manager.get_memory_info()
            
            # 创建 SoraWM 实例并运行
            sora_wm = SoraWM()
            
            # 运行处理
            sora_wm.run(self.test_video_path, output_path)
            
            # 记录结束时间和内存
            end_time = time.time()
            end_memory = memory_manager.get_memory_info()
            
            # 计算性能指标
            total_time = end_time - start_time
            
            # 获取视频信息
            from sorawm.utils.video_utils import VideoLoader
            video_loader = VideoLoader(self.test_video_path)
            total_frames = video_loader.total_frames
            fps = video_loader.fps
            duration = total_frames / fps
            
            # 计算处理速度
            processing_fps = total_frames / total_time
            speed_ratio = processing_fps / fps  # 相对于实时播放的速度
            
            # 内存使用情况
            memory_usage = {
                "start": start_memory,
                "end": end_memory,
                "peak_cpu_memory": max(start_memory["cpu_memory"]["used"], end_memory["cpu_memory"]["used"]),
            }
            
            if "gpu_memory" in start_memory:
                memory_usage["peak_gpu_memory"] = max(
                    start_memory["gpu_memory"]["allocated"], 
                    end_memory["gpu_memory"]["allocated"]
                )
            
            # 构建测试结果
            test_result = {
                "test_name": test_name,
                "config": {
                    "use_batch_processing": use_batch_processing,
                    "batch_size": batch_size or BATCH_SIZE,
                },
                "performance": {
                    "total_time": total_time,
                    "total_frames": total_frames,
                    "video_duration": duration,
                    "processing_fps": processing_fps,
                    "speed_ratio": speed_ratio,
                    "real_time_factor": speed_ratio,  # 实时因子
                },
                "memory": memory_usage,
                "output_file": str(output_path),
                "success": True,
            }
            
            logger.info(f"Test {test_name} completed: {processing_fps:.2f} FPS, {speed_ratio:.2f}x real-time")
            
        except Exception as e:
            logger.error(f"Test {test_name} failed: {e}")
            test_result = {
                "test_name": test_name,
                "config": {
                    "use_batch_processing": use_batch_processing,
                    "batch_size": batch_size or BATCH_SIZE,
                },
                "error": str(e),
                "success": False,
            }
        
        finally:
            # 恢复原始配置
            configs.ENABLE_BATCH_PROCESSING = original_batch_processing
            configs.BATCH_SIZE = original_batch_size
        
        # 添加到结果中
        self.results["tests"].append(test_result)
        return test_result
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """
        运行全面的性能基准测试
        
        Returns:
            完整的测试结果
        """
        logger.info("Starting comprehensive performance benchmark")
        
        # 测试配置
        test_configs = [
            {"name": "original_single_frame", "batch": False, "batch_size": None},
            {"name": "batch_processing_default", "batch": True, "batch_size": None},
            {"name": "batch_processing_small", "batch": True, "batch_size": 4},
            {"name": "batch_processing_medium", "batch": True, "batch_size": 8},
            {"name": "batch_processing_large", "batch": True, "batch_size": 16},
            {"name": "batch_processing_xlarge", "batch": True, "batch_size": 32},
        ]
        
        # 运行所有测试
        for config in test_configs:
            self.run_single_test(
                config["name"],
                config["batch"],
                config["batch_size"]
            )
        
        # 生成性能对比报告
        self._generate_performance_report()
        
        # 保存结果
        self._save_results()
        
        logger.info("Comprehensive benchmark completed")
        return self.results
    
    def _generate_performance_report(self):
        """生成性能对比报告"""
        successful_tests = [t for t in self.results["tests"] if t.get("success", False)]
        
        if not successful_tests:
            logger.warning("No successful tests to generate report")
            return
        
        # 找到基准测试（原始单帧处理）
        baseline_test = None
        for test in successful_tests:
            if test["test_name"] == "original_single_frame":
                baseline_test = test
                break
        
        if not baseline_test:
            logger.warning("No baseline test found")
            return
        
        baseline_fps = baseline_test["performance"]["processing_fps"]
        baseline_time = baseline_test["performance"]["total_time"]
        
        # 计算性能提升
        for test in successful_tests:
            if test["test_name"] != "original_single_frame":
                test_fps = test["performance"]["processing_fps"]
                test_time = test["performance"]["total_time"]
                
                speedup = test_fps / baseline_fps
                time_reduction = (baseline_time - test_time) / baseline_time * 100
                
                test["performance"]["speedup_vs_baseline"] = speedup
                test["performance"]["time_reduction_percent"] = time_reduction
        
        # 找出最佳配置
        best_test = max(successful_tests, key=lambda x: x["performance"]["processing_fps"])
        
        self.results["summary"] = {
            "baseline_fps": baseline_fps,
            "best_fps": best_test["performance"]["processing_fps"],
            "best_config": best_test["test_name"],
            "max_speedup": best_test["performance"]["speedup_vs_baseline"],
            "total_tests": len(self.results["tests"]),
            "successful_tests": len(successful_tests),
        }
    
    def _save_results(self):
        """保存测试结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_dir / f"benchmark_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Benchmark results saved to: {results_file}")
        
        # 生成简化的报告
        self._generate_summary_report(results_file)
    
    def _generate_summary_report(self, results_file: Path):
        """生成简化的性能报告"""
        summary_file = results_file.with_suffix('.txt')
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("SoraWatermarkCleaner 性能基准测试报告\n")
            f.write("=" * 50 + "\n\n")
            
            # 系统信息
            f.write("系统信息:\n")
            f.write(f"  CPU 核心数: {self.results['test_info']['system_info']['cpu_count']}\n")
            f.write(f"  总内存: {self.results['test_info']['system_info']['memory_total'] / 1024**3:.2f} GB\n")
            f.write(f"  PyTorch 版本: {self.results['test_info']['system_info']['pytorch_version']}\n")
            
            if self.results['test_info']['system_info']['cuda_available']:
                f.write(f"  GPU: {self.results['test_info']['system_info']['gpu_name']}\n")
                f.write(f"  GPU 内存: {self.results['test_info']['system_info']['gpu_memory'] / 1024**3:.2f} GB\n")
            else:
                f.write("  GPU: 不可用\n")
            
            f.write("\n")
            
            # 测试结果
            if "summary" in self.results:
                summary = self.results["summary"]
                f.write("性能总结:\n")
                f.write(f"  基准性能: {summary['baseline_fps']:.2f} FPS\n")
                f.write(f"  最佳性能: {summary['best_fps']:.2f} FPS\n")
                f.write(f"  最佳配置: {summary['best_config']}\n")
                f.write(f"  最大加速比: {summary['max_speedup']:.2f}x\n")
                f.write(f"  成功测试: {summary['successful_tests']}/{summary['total_tests']}\n")
                f.write("\n")
            
            # 详细结果
            f.write("详细测试结果:\n")
            for test in self.results["tests"]:
                if test.get("success", False):
                    perf = test["performance"]
                    f.write(f"  {test['test_name']}:\n")
                    f.write(f"    处理速度: {perf['processing_fps']:.2f} FPS\n")
                    f.write(f"    实时因子: {perf['speed_ratio']:.2f}x\n")
                    if "speedup_vs_baseline" in perf:
                        f.write(f"    相对加速: {perf['speedup_vs_baseline']:.2f}x\n")
                    f.write(f"    总耗时: {perf['total_time']:.2f} 秒\n")
                    f.write("\n")
                else:
                    f.write(f"  {test['test_name']}: 失败 - {test.get('error', 'Unknown error')}\n")
        
        logger.info(f"Summary report saved to: {summary_file}")


def main():
    """主函数，运行性能测试"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SoraWatermarkCleaner 性能基准测试")
    parser.add_argument("--video", required=True, help="测试视频路径")
    parser.add_argument("--output", default="benchmark_output", help="输出目录")
    parser.add_argument("--quick", action="store_true", help="快速测试（只测试关键配置）")
    
    args = parser.parse_args()
    
    test_video = Path(args.video)
    output_dir = Path(args.output)
    
    if not test_video.exists():
        logger.error(f"Test video not found: {test_video}")
        return
    
    # 创建基准测试实例
    benchmark = PerformanceBenchmark(test_video, output_dir)
    
    if args.quick:
        # 快速测试
        logger.info("Running quick benchmark")
        benchmark.run_single_test("original_single_frame", False)
        benchmark.run_single_test("batch_processing_default", True)
        benchmark._generate_performance_report()
        benchmark._save_results()
    else:
        # 全面测试
        benchmark.run_comprehensive_benchmark()
    
    logger.info("Benchmark completed!")


if __name__ == "__main__":
    main()
