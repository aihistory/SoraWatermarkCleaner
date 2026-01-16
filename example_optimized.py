"""
优化后的 SoraWatermarkCleaner 使用示例
展示如何使用新的性能优化功能
"""

from pathlib import Path
from sorawm.core import SoraWM
from sorawm.configs import (
    BATCH_SIZE, 
    ENABLE_BATCH_PROCESSING, 
    ENCODING_PRESET,
    ENABLE_HW_ACCEL,
    USE_FP16
)


def main():
    """主函数，演示优化后的使用方式"""
    
    # 输入和输出路径
    input_video_path = Path("resources/dog_vs_sam.mp4")
    output_video_path = Path("outputs/sora_watermark_removed_optimized.mp4")
    
    # 确保输出目录存在
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("🚀 SoraWatermarkCleaner 性能优化版本")
    print("=" * 50)
    
    # 显示当前配置
    print(f"📊 当前配置:")
    print(f"  批处理: {'启用' if ENABLE_BATCH_PROCESSING else '禁用'}")
    print(f"  批处理大小: {BATCH_SIZE}")
    print(f"  编码预设: {ENCODING_PRESET}")
    print(f"  硬件加速: {'启用' if ENABLE_HW_ACCEL else '禁用'}")
    print(f"  半精度推理: {'启用' if USE_FP16 else '禁用'}")
    print()
    
    # 创建 SoraWM 实例
    print("🔧 初始化模型...")
    sora_wm = SoraWM()
    
    # 定义进度回调函数
    def progress_callback(percentage: int):
        """进度回调函数"""
        bar_length = 30
        filled_length = int(bar_length * percentage // 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f'\r进度: |{bar}| {percentage}%', end='', flush=True)
    
    try:
        print(f"🎬 开始处理视频: {input_video_path}")
        print("处理中...")
        
        # 运行水印移除处理
        sora_wm.run(input_video_path, output_video_path, progress_callback)
        
        print(f"\n✅ 处理完成!")
        print(f"📁 输出文件: {output_video_path}")
        
        # 显示文件大小信息
        if output_video_path.exists():
            file_size = output_video_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📊 输出文件大小: {file_size:.2f} MB")
        
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        return 1
    
    print("\n🎉 水印移除完成!")
    return 0


def benchmark_comparison():
    """性能对比示例"""
    print("\n" + "=" * 50)
    print("📈 性能对比测试")
    print("=" * 50)
    
    input_video = Path("resources/dog_vs_sam.mp4")
    if not input_video.exists():
        print(f"❌ 测试视频不存在: {input_video}")
        return
    
    # 测试原始方法
    print("🔄 测试原始单帧处理方法...")
    import sorawm.configs as configs
    original_batch = configs.ENABLE_BATCH_PROCESSING
    configs.ENABLE_BATCH_PROCESSING = False
    
    try:
        sora_wm = SoraWM()
        output_original = Path("outputs/comparison_original.mp4")
        sora_wm.run(input_video, output_original)
        print("✅ 原始方法完成")
    except Exception as e:
        print(f"❌ 原始方法失败: {e}")
    finally:
        configs.ENABLE_BATCH_PROCESSING = original_batch
    
    # 测试优化方法
    print("🚀 测试优化批处理方法...")
    configs.ENABLE_BATCH_PROCESSING = True
    
    try:
        sora_wm = SoraWM()
        output_optimized = Path("outputs/comparison_optimized.mp4")
        sora_wm.run(input_video, output_optimized)
        print("✅ 优化方法完成")
    except Exception as e:
        print(f"❌ 优化方法失败: {e}")
    finally:
        configs.ENABLE_BATCH_PROCESSING = original_batch
    
    print("\n📊 对比完成! 请查看输出文件以验证质量。")


if __name__ == "__main__":
    import sys
    
    # 运行主处理
    exit_code = main()
    
    # 可选：运行性能对比
    if len(sys.argv) > 1 and sys.argv[1] == "--benchmark":
        benchmark_comparison()
    
    sys.exit(exit_code)
