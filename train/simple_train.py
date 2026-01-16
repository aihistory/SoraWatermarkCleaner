#!/usr/bin/env python3
"""
简化的训练脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    print("🚀 开始训练水印检测模型...")
    
    try:
        from ultralytics import YOLO
        
        # 加载预训练模型
        print("📥 加载预训练模型...")
        model = YOLO("yolo11s.pt")
        
        # 开始训练
        print("🏋️  开始训练...")
        results = model.train(
            data="train/coco8.yaml",
            epochs=50,  # 减少训练轮数用于测试
            imgsz=640,
            batch=8,    # 减少批大小
            device="cuda",
            project="runs/train",
            name="watermark_detector",
            save=True,
            verbose=True
        )
        
        print("✅ 训练完成!")
        print(f"📁 训练结果: {results.save_dir}")
        
        # 评估模型
        print("📊 评估模型...")
        metrics = model.val()
        print(f"mAP50: {metrics.box.map50:.3f}")
        print(f"mAP50-95: {metrics.box.map:.3f}")
        
    except Exception as e:
        print(f"❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
