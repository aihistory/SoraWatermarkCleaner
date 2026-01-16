#!/usr/bin/env python3
"""
模型测试脚本
测试训练好的水印检测模型
"""

import sys
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_model_on_images(model_path, test_images_dir, output_dir):
    """在测试图像上测试模型"""
    print(f"🧪 测试模型: {model_path}")
    print(f"📁 测试图像目录: {test_images_dir}")
    print(f"📁 输出目录: {output_dir}")
    
    # 加载模型
    model = YOLO(model_path)
    
    # 创建输出目录
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取测试图像
    test_images = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))
    
    if not test_images:
        print("❌ 没有找到测试图像")
        return
    
    print(f"📊 找到 {len(test_images)} 张测试图像")
    
    # 测试每张图像
    results_summary = []
    
    for i, image_path in enumerate(test_images):
        print(f"\n🔍 测试图像 {i+1}/{len(test_images)}: {image_path.name}")
        
        # 进行预测
        results = model(str(image_path))
        
        # 获取预测结果
        result = results[0]
        
        # 统计检测结果
        detections = len(result.boxes) if result.boxes is not None else 0
        confidences = result.boxes.conf.cpu().numpy() if result.boxes is not None else []
        
        print(f"   检测到 {detections} 个水印")
        if detections > 0:
            avg_conf = np.mean(confidences)
            max_conf = np.max(confidences)
            print(f"   平均置信度: {avg_conf:.3f}")
            print(f"   最高置信度: {max_conf:.3f}")
        
        # 保存结果图像
        output_path = output_dir / f"result_{image_path.name}"
        result.save(str(output_path))
        print(f"   💾 结果已保存: {output_path}")
        
        # 记录结果
        results_summary.append({
            'image': image_path.name,
            'detections': detections,
            'avg_confidence': np.mean(confidences) if detections > 0 else 0,
            'max_confidence': np.max(confidences) if detections > 0 else 0
        })
    
    # 生成测试报告
    generate_test_report(results_summary, output_dir)
    
    return results_summary

def generate_test_report(results_summary, output_dir):
    """生成测试报告"""
    print(f"\n📊 生成测试报告...")
    
    # 统计信息
    total_images = len(results_summary)
    total_detections = sum(r['detections'] for r in results_summary)
    images_with_detections = sum(1 for r in results_summary if r['detections'] > 0)
    
    avg_detections_per_image = total_detections / total_images if total_images > 0 else 0
    detection_rate = images_with_detections / total_images if total_images > 0 else 0
    
    # 置信度统计
    all_confidences = [r['avg_confidence'] for r in results_summary if r['detections'] > 0]
    avg_confidence = np.mean(all_confidences) if all_confidences else 0
    max_confidence = max(r['max_confidence'] for r in results_summary) if results_summary else 0
    
    # 生成报告
    report_path = output_dir / "test_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("水印检测模型测试报告\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"测试图像总数: {total_images}\n")
        f.write(f"检测到水印的图像数: {images_with_detections}\n")
        f.write(f"检测率: {detection_rate:.2%}\n")
        f.write(f"总检测数: {total_detections}\n")
        f.write(f"平均每张图像检测数: {avg_detections_per_image:.2f}\n")
        f.write(f"平均置信度: {avg_confidence:.3f}\n")
        f.write(f"最高置信度: {max_confidence:.3f}\n\n")
        
        f.write("详细结果:\n")
        f.write("-" * 30 + "\n")
        for result in results_summary:
            f.write(f"{result['image']}: {result['detections']} 个检测, "
                   f"平均置信度 {result['avg_confidence']:.3f}\n")
    
    print(f"📄 测试报告已保存: {report_path}")
    
    # 打印摘要
    print(f"\n📊 测试摘要:")
    print(f"   测试图像: {total_images}")
    print(f"   检测率: {detection_rate:.2%}")
    print(f"   总检测数: {total_detections}")
    print(f"   平均置信度: {avg_confidence:.3f}")

def test_model_on_video(model_path, video_path, output_path):
    """在视频上测试模型"""
    print(f"🎥 在视频上测试模型: {video_path}")
    
    # 加载模型
    model = YOLO(model_path)
    
    # 打开视频
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"❌ 无法打开视频: {video_path}")
        return
    
    # 获取视频信息
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"📹 视频信息: {width}x{height}, {fps} FPS, {total_frames} 帧")
    
    # 设置输出视频
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    frame_count = 0
    detection_count = 0
    
    print("🎬 开始处理视频...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 进行预测
        results = model(frame)
        result = results[0]
        
        # 统计检测结果
        detections = len(result.boxes) if result.boxes is not None else 0
        if detections > 0:
            detection_count += 1
        
        # 保存带检测结果的帧
        annotated_frame = result.plot()
        out.write(annotated_frame)
        
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"   处理进度: {frame_count}/{total_frames} ({frame_count/total_frames:.1%})")
    
    # 释放资源
    cap.release()
    out.release()
    
    print(f"✅ 视频处理完成!")
    print(f"   处理帧数: {frame_count}")
    print(f"   检测到水印的帧数: {detection_count}")
    print(f"   检测率: {detection_count/frame_count:.2%}")
    print(f"   输出视频: {output_path}")

def main():
    """主函数"""
    print("🧪 水印检测模型测试")
    print("=" * 50)
    
    # 查找最新的训练模型
    runs_dir = Path("runs/train")
    if not runs_dir.exists():
        print("❌ 训练结果目录不存在")
        return
    
    # 查找最新的实验
    experiments = list(runs_dir.glob("watermark_detector*"))
    if not experiments:
        print("❌ 未找到训练实验")
        return
    
    latest_experiment = max(experiments, key=lambda x: x.stat().st_mtime)
    model_path = latest_experiment / "weights" / "best.pt"
    
    if not model_path.exists():
        print(f"❌ 模型文件不存在: {model_path}")
        return
    
    print(f"📁 使用模型: {model_path}")
    
    # 测试选项
    print("\n🔧 测试选项:")
    print("1. 在测试集图像上测试")
    print("2. 在示例视频上测试")
    print("3. 在自定义图像上测试")
    
    try:
        choice = input("\n请选择测试选项 (1-3): ").strip()
        
        if choice == "1":
            # 在测试集上测试
            test_images_dir = Path("datasets/coco8/images/test")
            output_dir = Path("runs/test/test_images")
            test_model_on_images(model_path, test_images_dir, output_dir)
            
        elif choice == "2":
            # 在示例视频上测试
            video_path = Path("resources/dog_vs_sam.mp4")
            if video_path.exists():
                output_path = Path("runs/test/test_video.mp4")
                test_model_on_video(model_path, video_path, output_path)
            else:
                print(f"❌ 示例视频不存在: {video_path}")
                
        elif choice == "3":
            # 在自定义图像上测试
            image_path = input("请输入图像路径: ").strip()
            if Path(image_path).exists():
                output_dir = Path("runs/test/custom")
                test_model_on_images(model_path, Path(image_path).parent, output_dir)
            else:
                print(f"❌ 图像不存在: {image_path}")
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n👋 测试已取消")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    main()
