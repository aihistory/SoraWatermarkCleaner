"""
测试高级检测策略
验证多尺度检测、智能漏检处理、增强掩码生成的效果
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


def test_advanced_detection():
    """测试高级检测策略"""
    print("🚀 测试高级检测策略")
    print("=" * 60)
    
    # 测试视频路径
    test_video = Path("resources/dog_vs_sam.mp4")
    if not test_video.exists():
        print(f"❌ 测试视频不存在: {test_video}")
        return False
    
    # 输出路径
    output_path = Path("outputs/test_advanced_detection.mp4")
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    print("📊 高级检测策略配置:")
    print(f"  最低置信度阈值: {DETECTION_MIN_CONFIDENCE}")
    print(f"  高置信度阈值: {DETECTION_HIGH_CONFIDENCE}")
    print(f"  平滑窗口大小: {BBOX_SMOOTHING_WINDOW}")
    print(f"  稳定性阈值: {BBOX_STABILITY_THRESHOLD}")
    print()
    
    try:
        print("🔧 创建 SoraWM 实例（启用高级检测）...")
        sora_wm = SoraWM()
        
        # 进度回调
        def progress_callback(percentage: int):
            bar_length = 40
            filled_length = int(bar_length * percentage // 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f'\r处理进度: |{bar}| {percentage}%', end='', flush=True)
        
        print("🎬 开始处理视频（使用高级检测策略）...")
        sora_wm.run(test_video, output_path, progress_callback)
        
        print(f"\n✅ 处理完成!")
        print(f"📁 输出文件: {output_path}")
        
        if output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)
            print(f"📊 文件大小: {file_size:.2f} MB")
            
            # 获取各种统计信息
            temporal_stats = sora_wm.detector.temporal_detector.get_detection_statistics()
            advanced_stats = sora_wm.detector.advanced_strategy.get_detection_statistics()
            missed_stats = sora_wm.detector.missed_handler.get_statistics()
            
            print(f"\n📈 检测统计信息:")
            print(f"  时序一致性检测:")
            print(f"    检测率: {temporal_stats['detection_rate']:.2%}")
            print(f"    平均置信度: {temporal_stats['avg_confidence']:.3f}")
            print(f"    稳定检测次数: {temporal_stats['stable_detection_count']}")
            print(f"    有稳定检测: {'是' if temporal_stats['has_stable_detection'] else '否'}")
            
            print(f"  高级检测策略:")
            print(f"    检测率: {advanced_stats['detection_rate']:.2%}")
            print(f"    平均置信度: {advanced_stats['avg_confidence']:.3f}")
            print(f"    历史长度: {advanced_stats['history_length']}")
            
            print(f"  漏检处理:")
            print(f"    检测率: {missed_stats['detection_rate']:.2%}")
            print(f"    插值次数: {missed_stats['interpolation_count']}")
            print(f"    运动模型就绪: {'是' if missed_stats.get('motion_model_ready', False) else '否'}")
            
            return True
        else:
            print("❌ 输出文件未生成")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def compare_detection_strategies():
    """对比不同检测策略的效果"""
    print("\n" + "=" * 60)
    print("📊 检测策略对比测试")
    print("=" * 60)
    
    test_video = Path("resources/dog_vs_sam.mp4")
    if not test_video.exists():
        print(f"❌ 测试视频不存在: {test_video}")
        return
    
    import time
    
    # 测试基础检测策略
    print("🔄 测试基础检测策略...")
    
    try:
        sora_wm = SoraWM()
        output_basic = Path("outputs/comparison_basic_detection.mp4")
        start_time = time.time()
        sora_wm.run(test_video, output_basic)
        basic_time = time.time() - start_time
        
        basic_temporal_stats = sora_wm.detector.temporal_detector.get_detection_statistics()
        basic_missed_stats = sora_wm.detector.missed_handler.get_statistics()
        
        print(f"✅ 基础策略完成，耗时: {basic_time:.2f} 秒")
        print(f"   检测率: {basic_temporal_stats['detection_rate']:.2%}")
        print(f"   插值次数: {basic_missed_stats['interpolation_count']}")
        
    except Exception as e:
        print(f"❌ 基础策略失败: {e}")
        basic_time = None
        basic_temporal_stats = None
        basic_missed_stats = None
    
    # 测试高级检测策略
    print("🚀 测试高级检测策略...")
    
    try:
        sora_wm = SoraWM()
        output_advanced = Path("outputs/comparison_advanced_detection.mp4")
        start_time = time.time()
        sora_wm.run(test_video, output_advanced)
        advanced_time = time.time() - start_time
        
        advanced_temporal_stats = sora_wm.detector.temporal_detector.get_detection_statistics()
        advanced_advanced_stats = sora_wm.detector.advanced_strategy.get_detection_statistics()
        advanced_missed_stats = sora_wm.detector.missed_handler.get_statistics()
        
        print(f"✅ 高级策略完成，耗时: {advanced_time:.2f} 秒")
        print(f"   检测率: {advanced_temporal_stats['detection_rate']:.2%}")
        print(f"   插值次数: {advanced_missed_stats['interpolation_count']}")
        print(f"   运动模型就绪: {'是' if advanced_missed_stats['motion_model_ready'] else '否'}")
        
    except Exception as e:
        print(f"❌ 高级策略失败: {e}")
        advanced_time = None
        advanced_temporal_stats = None
        advanced_advanced_stats = None
        advanced_missed_stats = None
    
    # 对比结果
    if (basic_time and advanced_time and 
        basic_temporal_stats and advanced_temporal_stats and
        basic_missed_stats and advanced_missed_stats):
        
        print(f"\n📈 检测策略对比:")
        print(f"  基础策略:")
        print(f"    处理时间: {basic_time:.2f} 秒")
        print(f"    检测率: {basic_temporal_stats['detection_rate']:.2%}")
        print(f"    插值次数: {basic_missed_stats['interpolation_count']}")
        
        print(f"  高级策略:")
        print(f"    处理时间: {advanced_time:.2f} 秒")
        print(f"    检测率: {advanced_temporal_stats['detection_rate']:.2%}")
        print(f"    插值次数: {advanced_missed_stats['interpolation_count']}")
        print(f"    运动模型就绪: {'是' if advanced_missed_stats.get('motion_model_ready', False) else '否'}")
        
        # 计算改进指标
        detection_improvement = (advanced_temporal_stats['detection_rate'] - 
                               basic_temporal_stats['detection_rate'])
        interpolation_improvement = (advanced_missed_stats['interpolation_count'] - 
                                   basic_missed_stats['interpolation_count'])
        
        print(f"\n🎯 改进效果:")
        print(f"  检测率提升: {detection_improvement:+.2%}")
        print(f"  插值次数变化: {interpolation_improvement:+d}")
        print(f"  运动模型: {'启用' if advanced_missed_stats.get('motion_model_ready', False) else '未启用'}")
        
        if detection_improvement > 0:
            print("🎉 高级检测策略提升了检测精度!")
        else:
            print("⚠️  检测精度需要进一步调优")


def test_multi_scale_detection():
    """测试多尺度检测"""
    print("\n" + "=" * 60)
    print("🔍 多尺度检测测试")
    print("=" * 60)
    
    from sorawm.utils.advanced_detector import AdvancedDetectionStrategy
    from sorawm.watermark_detector import SoraWaterMarkDetector
    import cv2
    
    # 创建测试实例
    detector = SoraWaterMarkDetector()
    strategy = AdvancedDetectionStrategy()
    
    # 加载测试图像
    test_video = Path("resources/dog_vs_sam.mp4")
    if not test_video.exists():
        print(f"❌ 测试视频不存在: {test_video}")
        return
    
    # 读取第一帧作为测试
    cap = cv2.VideoCapture(str(test_video))
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ 无法读取测试帧")
        return
    
    print("🧪 测试多尺度检测...")
    
    # 测试不同尺度
    scales = [0.8, 0.9, 1.0, 1.1, 1.2]
    results = []
    
    for scale in scales:
        result = strategy.multi_scale_detection(detector, frame, [scale])
        results.append((scale, result))
        
        print(f"尺度 {scale}: 检测={result['detected']}, "
              f"置信度={result['confidence']:.3f}, "
              f"多尺度={result.get('multi_scale', False)}")
    
    # 测试融合检测
    print("\n🔗 测试多尺度融合检测...")
    fusion_result = strategy.multi_scale_detection(detector, frame, scales)
    
    print(f"融合结果: 检测={fusion_result['detected']}, "
          f"置信度={fusion_result['confidence']:.3f}, "
          f"多尺度={fusion_result.get('multi_scale', False)}")
    
    # 统计结果
    individual_detections = sum(1 for _, result in results if result['detected'])
    fusion_detection = 1 if fusion_result['detected'] else 0
    
    print(f"\n📊 多尺度检测统计:")
    print(f"  单尺度检测成功: {individual_detections}/{len(scales)}")
    print(f"  融合检测成功: {'是' if fusion_detection else '否'}")
    print(f"  融合置信度: {fusion_result['confidence']:.3f}")


if __name__ == "__main__":
    import sys
    
    # 基本高级检测测试
    success = test_advanced_detection()
    
    # 如果基本测试成功，进行对比测试
    if success and len(sys.argv) > 1:
        if sys.argv[1] == "--compare":
            compare_detection_strategies()
        elif sys.argv[1] == "--multiscale":
            test_multi_scale_detection()
        elif sys.argv[1] == "--all":
            compare_detection_strategies()
            test_multi_scale_detection()
    
    if success:
        print("\n🎉 高级检测策略测试完成!")
        print("💡 提示: 使用 --compare 进行策略对比，--multiscale 测试多尺度检测，--all 运行所有测试")
    else:
        print("\n❌ 高级检测策略测试失败，请检查错误信息")
