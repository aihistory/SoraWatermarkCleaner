#!/usr/bin/env python3
"""
水印检测模型训练脚本
基于 YOLOv11 训练水印检测模型
"""

import sys
from pathlib import Path
import torch
from ultralytics import YOLO
import yaml

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment():
    """检查训练环境"""
    print("🔍 检查训练环境...")
    
    # 检查 CUDA
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0)
        print(f"✅ GPU 可用: {gpu_name} (共 {gpu_count} 个)")
        return "cuda"
    else:
        print("⚠️  GPU 不可用，将使用 CPU 训练（速度较慢）")
        return "cpu"

def check_dataset():
    """检查数据集"""
    print("\n📊 检查数据集...")
    
    dataset_config = Path("train/coco8.yaml")
    if not dataset_config.exists():
        print(f"❌ 数据集配置文件不存在: {dataset_config}")
        return False
    
    # 读取配置文件
    with open(dataset_config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 检查路径（相对于训练脚本目录）
    script_dir = Path(__file__).parent
    base_path = script_dir / config['path']
    train_path = base_path / config['train']
    val_path = base_path / config['val']
    
    if not train_path.exists():
        print(f"❌ 训练集目录不存在: {train_path}")
        return False
    
    if not val_path.exists():
        print(f"❌ 验证集目录不存在: {val_path}")
        return False
    
    # 统计图像数量
    train_images = len(list(train_path.glob("*.jpg"))) + len(list(train_path.glob("*.png")))
    val_images = len(list(val_path.glob("*.jpg"))) + len(list(val_path.glob("*.png")))
    
    print(f"✅ 训练集: {train_images} 张图像")
    print(f"✅ 验证集: {val_images} 张图像")
    print(f"✅ 类别: {config['names']}")
    
    return True

def train_model(device="cuda", epochs=100, imgsz=640, batch_size=16):
    """训练模型"""
    print(f"\n🚀 开始训练水印检测模型...")
    print(f"📋 训练参数:")
    print(f"   设备: {device}")
    print(f"   训练轮数: {epochs}")
    print(f"   图像尺寸: {imgsz}")
    print(f"   批大小: {batch_size}")
    
    # 加载预训练模型
    print("\n📥 加载预训练模型...")
    model = YOLO("yolo11s.pt")  # 使用 YOLOv11s 模型
    
    # 开始训练
    print("\n🏋️  开始训练...")
    try:
        results = model.train(
            data="train/coco8.yaml",  # 数据集配置文件
            epochs=epochs,            # 训练轮数
            imgsz=imgsz,             # 图像尺寸
            batch=batch_size,        # 批大小
            device=device,           # 设备
            project="runs/train",    # 项目目录
            name="watermark_detector", # 实验名称
            save=True,               # 保存检查点
            save_period=10,          # 每10轮保存一次
            cache=True,              # 缓存图像
            workers=4,               # 数据加载线程数
            patience=20,             # 早停耐心值
            lr0=0.01,               # 初始学习率
            lrf=0.01,               # 最终学习率
            momentum=0.937,          # 动量
            weight_decay=0.0005,     # 权重衰减
            warmup_epochs=3,         # 预热轮数
            warmup_momentum=0.8,     # 预热动量
            warmup_bias_lr=0.1,      # 预热偏置学习率
            box=7.5,                # 边界框损失权重
            cls=0.5,                # 分类损失权重
            dfl=1.5,                # DFL损失权重
            val=True,               # 验证
            plots=True,             # 生成图表
            verbose=True,           # 详细输出
        )
        
        print("✅ 训练完成!")
        return results
        
    except Exception as e:
        print(f"❌ 训练失败: {e}")
        return None

def evaluate_model(model_path):
    """评估模型"""
    print(f"\n📊 评估模型: {model_path}")
    
    try:
        model = YOLO(model_path)
        metrics = model.val()
        
        print("✅ 模型评估完成!")
        print(f"📈 评估指标:")
        print(f"   mAP50: {metrics.box.map50:.3f}")
        print(f"   mAP50-95: {metrics.box.map:.3f}")
        
        return metrics
        
    except Exception as e:
        print(f"❌ 模型评估失败: {e}")
        return None

def test_model(model_path, test_image_path):
    """测试模型"""
    print(f"\n🧪 测试模型: {model_path}")
    
    if not Path(test_image_path).exists():
        print(f"⚠️  测试图像不存在: {test_image_path}")
        return None
    
    try:
        model = YOLO(model_path)
        results = model(test_image_path)
        
        print("✅ 模型测试完成!")
        
        # 保存结果
        output_dir = Path("runs/detect/test")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, result in enumerate(results):
            result.save(str(output_dir / f"test_result_{i}.jpg"))
        
        print(f"📁 测试结果已保存到: {output_dir}")
        
        return results
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return None

def export_model(model_path, formats=["onnx", "torchscript"]):
    """导出模型"""
    print(f"\n📦 导出模型: {model_path}")
    
    try:
        model = YOLO(model_path)
        exported_paths = []
        
        for format_type in formats:
            try:
                path = model.export(format=format_type)
                exported_paths.append(path)
                print(f"✅ 导出 {format_type.upper()} 格式: {path}")
            except Exception as e:
                print(f"❌ 导出 {format_type.upper()} 格式失败: {e}")
        
        return exported_paths
        
    except Exception as e:
        print(f"❌ 模型导出失败: {e}")
        return None

def main():
    """主函数"""
    print("🎯 水印检测模型训练")
    print("=" * 50)
    
    # 检查环境
    device = check_environment()
    
    # 检查数据集
    if not check_dataset():
        print("❌ 数据集检查失败，请检查数据集配置")
        return
    
    # 训练参数
    epochs = 100
    imgsz = 640
    batch_size = 16 if device == "cuda" else 8
    
    # 开始训练
    results = train_model(device=device, epochs=epochs, imgsz=imgsz, batch_size=batch_size)
    
    if results is None:
        print("❌ 训练失败")
        return
    
    # 获取最佳模型路径
    best_model_path = results.save_dir / "weights" / "best.pt"
    
    if not best_model_path.exists():
        print("❌ 未找到训练好的模型")
        return
    
    print(f"✅ 训练完成! 最佳模型: {best_model_path}")
    
    # 评估模型
    evaluate_model(best_model_path)
    
    # 测试模型
    test_image = "resources/dog_vs_sam.mp4"  # 使用示例视频的第一帧
    if Path(test_image).exists():
        test_model(best_model_path, test_image)
    
    # 导出模型
    export_model(best_model_path)
    
    print("\n🎉 训练流程完成!")
    print(f"📁 训练结果保存在: {results.save_dir}")
    print(f"🏆 最佳模型: {best_model_path}")

if __name__ == "__main__":
    main()
