"""
测试修复后的批量处理功能
"""

from pathlib import Path
from sorawm.core import SoraWM
from sorawm.configs import ENABLE_BATCH_PROCESSING
import sorawm.configs as configs


def test_batch_processing():
    """测试批量处理功能"""
    print("🧪 测试批量处理修复")
    print("=" * 50)
    
    # 测试视频路径
    test_video = Path("resources/dog_vs_sam.mp4")
    if not test_video.exists():
        print(f"❌ 测试视频不存在: {test_video}")
        return False
    
    # 输出路径
    output_path = Path("outputs/test_batch_fix.mp4")
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    try:
        print("🔧 创建 SoraWM 实例...")
        sora_wm = SoraWM()
        
        print("📊 当前配置:")
        print(f"  批处理: {'启用' if ENABLE_BATCH_PROCESSING else '禁用'}")
        print(f"  批处理大小: {configs.BATCH_SIZE}")
        print(f"  半精度推理: {configs.USE_FP16}")
        print()
        
        # 进度回调
        def progress_callback(percentage: int):
            bar_length = 30
            filled_length = int(bar_length * percentage // 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f'\r进度: |{bar}| {percentage}%', end='', flush=True)
        
        print("🎬 开始处理视频...")
        sora_wm.run(test_video, output_path, progress_callback)
        
        print(f"\n✅ 处理完成!")
        print(f"📁 输出文件: {output_path}")
        
        if output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)
            print(f"📊 文件大小: {file_size:.2f} MB")
            return True
        else:
            print("❌ 输出文件未生成")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_vs_batch():
    """对比单帧处理和批量处理"""
    print("\n" + "=" * 50)
    print("📈 单帧 vs 批量处理对比")
    print("=" * 50)
    
    test_video = Path("resources/dog_vs_sam.mp4")
    if not test_video.exists():
        print(f"❌ 测试视频不存在: {test_video}")
        return
    
    import time
    
    # 测试单帧处理
    print("🔄 测试单帧处理...")
    configs.ENABLE_BATCH_PROCESSING = False
    
    try:
        sora_wm = SoraWM()
        output_single = Path("outputs/test_single.mp4")
        start_time = time.time()
        sora_wm.run(test_video, output_single)
        single_time = time.time() - start_time
        print(f"✅ 单帧处理完成，耗时: {single_time:.2f} 秒")
    except Exception as e:
        print(f"❌ 单帧处理失败: {e}")
        single_time = None
    
    # 测试批量处理
    print("🚀 测试批量处理...")
    configs.ENABLE_BATCH_PROCESSING = True
    
    try:
        sora_wm = SoraWM()
        output_batch = Path("outputs/test_batch.mp4")
        start_time = time.time()
        sora_wm.run(test_video, output_batch)
        batch_time = time.time() - start_time
        print(f"✅ 批量处理完成，耗时: {batch_time:.2f} 秒")
    except Exception as e:
        print(f"❌ 批量处理失败: {e}")
        batch_time = None
    
    # 对比结果
    if single_time and batch_time:
        speedup = single_time / batch_time
        print(f"\n📊 性能对比:")
        print(f"  单帧处理: {single_time:.2f} 秒")
        print(f"  批量处理: {batch_time:.2f} 秒")
        print(f"  加速比: {speedup:.2f}x")
        
        if speedup > 1:
            print("🎉 批量处理更快!")
        else:
            print("⚠️  批量处理较慢，可能需要调优")


if __name__ == "__main__":
    import sys
    
    # 基本测试
    success = test_batch_processing()
    
    # 如果基本测试成功，进行对比测试
    if success and len(sys.argv) > 1 and sys.argv[1] == "--compare":
        test_single_vs_batch()
    
    if success:
        print("\n🎉 所有测试通过!")
    else:
        print("\n❌ 测试失败，请检查错误信息")
