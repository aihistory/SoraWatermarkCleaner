#!/usr/bin/env python3
"""
训练总结脚本
生成训练完成后的总结报告
"""

import sys
from pathlib import Path
import yaml
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def generate_training_summary():
    """生成训练总结"""
    print("📊 生成训练总结报告")
    print("=" * 50)
    
    # 查找最新的训练实验
    runs_dir = Path("runs/train")
    if not runs_dir.exists():
        print("❌ 训练结果目录不存在")
        return
    
    experiments = list(runs_dir.glob("watermark_detector*"))
    if not experiments:
        print("❌ 未找到训练实验")
        return
    
    latest_experiment = max(experiments, key=lambda x: x.stat().st_mtime)
    print(f"📁 最新实验: {latest_experiment}")
    
    # 读取训练配置
    config_file = latest_experiment / "args.yaml"
    config = {}
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    
    # 读取训练结果
    results_file = latest_experiment / "results.csv"
    results = []
    if results_file.exists():
        import pandas as pd
        df = pd.read_csv(results_file)
        results = df.to_dict('records')
    
    # 检查模型文件
    weights_dir = latest_experiment / "weights"
    model_files = {}
    if weights_dir.exists():
        for model_file in ["best.pt", "last.pt"]:
            model_path = weights_dir / model_file
            if model_path.exists():
                size = model_path.stat().st_size / (1024 * 1024)  # MB
                model_files[model_file] = {
                    "path": str(model_path),
                    "size_mb": round(size, 1)
                }
    
    # 生成总结报告
    summary = {
        "experiment_name": latest_experiment.name,
        "experiment_path": str(latest_experiment),
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "model_files": model_files,
        "training_summary": {}
    }
    
    if results:
        # 获取最佳结果
        best_result = max(results, key=lambda x: x.get('metrics/mAP50(B)', 0))
        latest_result = results[-1]
        
        summary["training_summary"] = {
            "total_epochs": len(results),
            "best_epoch": int(best_result.get('epoch', 0)),
            "best_mAP50": round(best_result.get('metrics/mAP50(B)', 0), 4),
            "best_mAP50_95": round(best_result.get('metrics/mAP50-95(B)', 0), 4),
            "final_mAP50": round(latest_result.get('metrics/mAP50(B)', 0), 4),
            "final_mAP50_95": round(latest_result.get('metrics/mAP50-95(B)', 0), 4),
            "final_train_loss": round(latest_result.get('train/box_loss', 0), 4),
            "final_val_loss": round(latest_result.get('val/box_loss', 0), 4)
        }
    
    # 保存总结报告
    summary_file = latest_experiment / "training_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"📄 训练总结已保存: {summary_file}")
    
    # 打印总结
    print(f"\n📊 训练总结:")
    print(f"   实验名称: {summary['experiment_name']}")
    print(f"   训练轮数: {summary['training_summary'].get('total_epochs', 'N/A')}")
    print(f"   最佳轮数: {summary['training_summary'].get('best_epoch', 'N/A')}")
    print(f"   最佳 mAP50: {summary['training_summary'].get('best_mAP50', 'N/A')}")
    print(f"   最佳 mAP50-95: {summary['training_summary'].get('best_mAP50_95', 'N/A')}")
    print(f"   最终 mAP50: {summary['training_summary'].get('final_mAP50', 'N/A')}")
    print(f"   最终 mAP50-95: {summary['training_summary'].get('final_mAP50_95', 'N/A')}")
    
    print(f"\n📁 模型文件:")
    for model_name, model_info in model_files.items():
        print(f"   {model_name}: {model_info['size_mb']} MB")
    
    print(f"\n💡 下一步:")
    print(f"   1. 测试模型: uv run python train/test_model.py")
    print(f"   2. 查看训练曲线: {latest_experiment}/training_curves.png")
    print(f"   3. 使用最佳模型: {model_files.get('best.pt', {}).get('path', 'N/A')}")
    
    return summary

def create_deployment_guide():
    """创建部署指南"""
    print(f"\n📋 创建部署指南...")
    
    guide_content = """# 水印检测模型部署指南

## 模型文件
- **最佳模型**: `runs/train/watermark_detector3/weights/best.pt`
- **最新模型**: `runs/train/watermark_detector3/weights/last.pt`

## 使用方法

### 1. 基本使用
```python
from ultralytics import YOLO

# 加载模型
model = YOLO("runs/train/watermark_detector3/weights/best.pt")

# 检测图像
results = model("path/to/image.jpg")

# 显示结果
results[0].show()
```

### 2. 批量处理
```python
# 处理多个图像
results = model(["image1.jpg", "image2.jpg", "image3.jpg"])

# 处理视频
results = model("video.mp4")
```

### 3. 集成到 SoraWatermarkCleaner
```python
# 在 sorawm/watermark_detector.py 中使用
from ultralytics import YOLO

class WatermarkDetector:
    def __init__(self, model_path="runs/train/watermark_detector3/weights/best.pt"):
        self.model = YOLO(model_path)
    
    def detect(self, image):
        results = self.model(image)
        return results[0].boxes
```

## 性能指标
- **mAP50**: 检测精度指标
- **mAP50-95**: 综合精度指标
- **推理速度**: 在 GPU 上约 10-20ms/图像

## 注意事项
1. 模型需要 PyTorch 和 Ultralytics 环境
2. 建议使用 GPU 进行推理以获得最佳性能
3. 输入图像会自动调整到 640x640 尺寸
4. 检测结果包含边界框坐标和置信度

## 模型优化
- 可以导出为 ONNX 格式以提高部署效率
- 可以使用 TensorRT 进行 GPU 加速
- 可以量化模型以减少内存占用
"""
    
    guide_file = Path("TRAINING_DEPLOYMENT_GUIDE.md")
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"📄 部署指南已保存: {guide_file}")

def main():
    """主函数"""
    # 生成训练总结
    summary = generate_training_summary()
    
    # 创建部署指南
    create_deployment_guide()
    
    print(f"\n🎉 训练总结完成!")
    print(f"📁 所有文件已保存到 runs/train/ 目录")

if __name__ == "__main__":
    main()
