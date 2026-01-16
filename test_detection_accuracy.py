"""
测试水印检测精度改进
验证时序一致性检测和增强边界框平滑的效果
"""

from pathlib import Path
from sorawm.core import SoraWM
from sorawm.configs import (
    DETECTION_MIN_CONFIDENCE,
    DETECTION_HIGH_CONFIDENCE,
    BBOX_SMOOTHING_WINDOW,
    BBOX_STABILITY_THRESHOLD
)
import sorawm.configs as configs


def test_detection_accuracy():
    """测试检测精度改进"""
    print("🔍 测试水印检测精度改进")
    print("=" * 60)
    
    # 测试视频路径
    test_video = Path("resources/dog_vs_sam.mp4")
    if not test_video.exists():
        print(f"❌ 测试视频不存在: {test_video}")
        return False
    
    # 输出路径
    output_path = Path("outputs/test_detection_accuracy.mp4")
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    print("📊 当前检测精度配置:")
    print(f"  最低置信度阈值: {DETECTION_MIN_CONFIDENCE}")
    print(f"  高置信度阈值: {DETECTION_HIGH_CONFIDENCE}")
    print(f"  平滑窗口大小: {BBOX_SMOOTHING_WINDOW}")
    print(f"  稳定性阈值: {BBOX_STABILITY_THRESHOLD}")
    print()
    
    try:
        print("🔧 创建 SoraWM 实例...")
        sora_wm = SoraWM()
        
        # 进度回调
        def progress_callback(percentage: int):
            bar_length = 40
            filled_length = int(bar_length * percentage // 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f'\r处理进度: |{bar}| {percentage}%', end='', flush=True)
        
        print("🎬 开始处理视频（使用增强检测精度）...")
        sora_wm.run(test_video, output_path, progress_callback)
        
        print(f"\n✅ 处理完成!")
        print(f"📁 输出文件: {output_path}")
        
        if output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)
            print(f"📊 文件大小: {file_size:.2f} MB")
            
            # 获取检测统计信息
            detector_stats = sora_wm.detector.temporal_detector.get_detection_statistics()
            print(f"\n📈 检测统计信息:")
            print(f"  检测率: {detector_stats['detection_rate']:.2%}")
            print(f"  平均置信度: {detector_stats['avg_confidence']:.3f}")
            print(f"  稳定检测次数: {detector_stats['stable_detection_count']}")
            print(f"  有稳定检测: {'是' if detector_stats['has_stable_detection'] else '否'}")
            print(f"  历史长度: {detector_stats['history_length']}")
            
            return True
        else:
            print("❌ 输出文件未生成")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def compare_detection_methods():
    """对比不同检测方法的精度"""
    print("\n" + "=" * 60)
    print("📊 检测方法对比测试")
    print("=" * 60)
    
    test_video = Path("resources/dog_vs_sam.mp4")
    if not test_video.exists():
        print(f"❌ 测试视频不存在: {test_video}")
        return
    
    import time
    
    # 测试原始检测方法
    print("🔄 测试原始检测方法...")
    original_min_conf = configs.DETECTION_MIN_CONFIDENCE
    original_smoothing = configs.BBOX_SMOOTHING_WINDOW
    
    # 设置原始参数
    configs.DETECTION_MIN_CONFIDENCE = 0.15
    configs.BBOX_SMOOTHING_WINDOW = 5
    
    try:
        sora_wm = SoraWM()
        output_original = Path("outputs/comparison_original_detection.mp4")
        start_time = time.time()
        sora_wm.run(test_video, output_original)
        original_time = time.time() - start_time
        
        original_stats = sora_wm.detector.temporal_detector.get_detection_statistics()
        print(f"✅ 原始方法完成，耗时: {original_time:.2f} 秒")
        print(f"   检测率: {original_stats['detection_rate']:.2%}")
        print(f"   平均置信度: {original_stats['avg_confidence']:.3f}")
        
    except Exception as e:
        print(f"❌ 原始方法失败: {e}")
        original_time = None
        original_stats = None
    finally:
        # 恢复原始配置
        configs.DETECTION_MIN_CONFIDENCE = original_min_conf
        configs.BBOX_SMOOTHING_WINDOW = original_smoothing
    
    # 测试增强检测方法
    print("🚀 测试增强检测方法...")
    
    try:
        sora_wm = SoraWM()
        output_enhanced = Path("outputs/comparison_enhanced_detection.mp4")
        start_time = time.time()
        sora_wm.run(test_video, output_enhanced)
        enhanced_time = time.time() - start_time
        
        enhanced_stats = sora_wm.detector.temporal_detector.get_detection_statistics()
        print(f"✅ 增强方法完成，耗时: {enhanced_time:.2f} 秒")
        print(f"   检测率: {enhanced_stats['detection_rate']:.2%}")
        print(f"   平均置信度: {enhanced_stats['avg_confidence']:.3f}")
        print(f"   稳定检测次数: {enhanced_stats['stable_detection_count']}")
        
    except Exception as e:
        print(f"❌ 增强方法失败: {e}")
        enhanced_time = None
        enhanced_stats = None
    
    # 对比结果
    if original_time and enhanced_time and original_stats and enhanced_stats:
        print(f"\n📈 检测精度对比:")
        print(f"  原始方法:")
        print(f"    处理时间: {original_time:.2f} 秒")
        print(f"    检测率: {original_stats['detection_rate']:.2%}")
        print(f"    平均置信度: {original_stats['avg_confidence']:.3f}")
        print(f"  增强方法:")
        print(f"    处理时间: {enhanced_time:.2f} 秒")
        print(f"    检测率: {enhanced_stats['detection_rate']:.2%}")
        print(f"    平均置信度: {enhanced_stats['avg_confidence']:.3f}")
        print(f"    稳定检测次数: {enhanced_stats['stable_detection_count']}")
        
        # 计算改进指标
        detection_improvement = enhanced_stats['detection_rate'] - original_stats['detection_rate']
        confidence_improvement = enhanced_stats['avg_confidence'] - original_stats['avg_confidence']
        
        print(f"\n🎯 改进效果:")
        print(f"  检测率提升: {detection_improvement:+.2%}")
        print(f"  置信度提升: {confidence_improvement:+.3f}")
        print(f"  稳定性: {'有' if enhanced_stats['stable_detection_count'] > 0 else '无'}稳定检测")
        
        if detection_improvement > 0 or confidence_improvement > 0:
            print("🎉 检测精度有所提升!")
        else:
            print("⚠️  检测精度需要进一步调优")


def test_temporal_consistency():
    """测试时序一致性检测"""
    print("\n" + "=" * 60)
    print("⏰ 时序一致性检测测试")
    print("=" * 60)
    
    from sorawm.utils.temporal_detector import TemporalConsistencyDetector
    import numpy as np
    
    # 创建测试数据
    detector = TemporalConsistencyDetector()
    
    # 模拟检测序列：前几帧检测到，中间几帧漏检，后面又检测到
    test_sequence = [
        # 稳定的检测序列
        {"detected": True, "bbox": (100, 100, 200, 200), "confidence": 0.8, "center": (150, 150)},
        {"detected": True, "bbox": (102, 102, 202, 202), "confidence": 0.75, "center": (152, 152)},
        {"detected": True, "bbox": (104, 104, 204, 204), "confidence": 0.7, "center": (154, 154)},
        
        # 漏检序列
        {"detected": False, "bbox": None, "confidence": 0.0, "center": None},
        {"detected": False, "bbox": None, "confidence": 0.0, "center": None},
        
        # 跳跃检测（应该被过滤）
        {"detected": True, "bbox": (300, 300, 400, 400), "confidence": 0.6, "center": (350, 350)},
        
        # 恢复正常检测
        {"detected": True, "bbox": (106, 106, 206, 206), "confidence": 0.8, "center": (156, 156)},
    ]
    
    print("🧪 测试时序一致性检测...")
    results = []
    
    for i, detection in enumerate(test_sequence):
        result = detector.process_detection(detection, i)
        results.append(result)
        
        print(f"帧 {i}: 原始={detection['detected']}, 处理后={result['detected']}, "
              f"稳定={result.get('stable', False)}, 插值={result.get('interpolated', False)}")
    
    # 分析结果
    original_detections = sum(1 for d in test_sequence if d['detected'])
    processed_detections = sum(1 for r in results if r['detected'])
    stable_detections = sum(1 for r in results if r.get('stable', False))
    interpolated_detections = sum(1 for r in results if r.get('interpolated', False))
    
    print(f"\n📊 时序一致性分析:")
    print(f"  原始检测数: {original_detections}")
    print(f"  处理后检测数: {processed_detections}")
    print(f"  稳定检测数: {stable_detections}")
    print(f"  插值检测数: {interpolated_detections}")
    
    # 获取统计信息
    stats = detector.get_detection_statistics()
    print(f"  最终检测率: {stats['detection_rate']:.2%}")
    print(f"  平均置信度: {stats['avg_confidence']:.3f}")
    print(f"  稳定检测次数: {stats['stable_detection_count']}")


if __name__ == "__main__":
    import sys
    
    # 基本精度测试
    success = test_detection_accuracy()
    
    # 如果基本测试成功，进行对比测试
    if success and len(sys.argv) > 1:
        if sys.argv[1] == "--compare":
            compare_detection_methods()
        elif sys.argv[1] == "--temporal":
            test_temporal_consistency()
        elif sys.argv[1] == "--all":
            compare_detection_methods()
            test_temporal_consistency()
    
    if success:
        print("\n🎉 检测精度测试完成!")
        print("💡 提示: 使用 --compare 进行方法对比，--temporal 测试时序一致性，--all 运行所有测试")
    else:
        print("\n❌ 检测精度测试失败，请检查错误信息")
