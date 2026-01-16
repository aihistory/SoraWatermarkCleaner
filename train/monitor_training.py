#!/usr/bin/env python3
"""
训练监控脚本
监控训练进度和结果
"""

import sys
from pathlib import Path
import time
import json
import matplotlib.pyplot as plt
import pandas as pd

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_training_status():
    """检查训练状态"""
    print("🔍 检查训练状态...")
    
    # 查找训练结果目录
    runs_dir = Path("runs/train")
    if not runs_dir.exists():
        print("❌ 训练结果目录不存在")
        return None
    
    # 查找最新的训练实验
    experiments = list(runs_dir.glob("watermark_detector*"))
    if not experiments:
        print("❌ 未找到训练实验")
        return None
    
    # 按修改时间排序，获取最新的
    latest_experiment = max(experiments, key=lambda x: x.stat().st_mtime)
    print(f"📁 最新实验: {latest_experiment}")
    
    return latest_experiment

def monitor_training_progress(experiment_dir):
    """监控训练进度"""
    print(f"\n📊 监控训练进度: {experiment_dir}")
    
    # 检查结果文件
    results_csv = experiment_dir / "results.csv"
    if not results_csv.exists():
        print("❌ 训练结果文件不存在")
        return
    
    # 读取训练结果
    try:
        df = pd.read_csv(results_csv)
        print(f"✅ 已读取训练结果，共 {len(df)} 轮")
        
        # 显示最新结果
        if len(df) > 0:
            latest = df.iloc[-1]
            print(f"\n📈 最新训练结果 (第 {latest.get('epoch', 'N/A')} 轮):")
            print(f"   训练损失: {latest.get('train/box_loss', 'N/A'):.4f}")
            print(f"   验证损失: {latest.get('val/box_loss', 'N/A'):.4f}")
            print(f"   mAP50: {latest.get('metrics/mAP50(B)', 'N/A'):.4f}")
            print(f"   mAP50-95: {latest.get('metrics/mAP50-95(B)', 'N/A'):.4f}")
        
        # 绘制训练曲线
        plot_training_curves(df, experiment_dir)
        
    except Exception as e:
        print(f"❌ 读取训练结果失败: {e}")

def plot_training_curves(df, experiment_dir):
    """绘制训练曲线"""
    print("\n📊 生成训练曲线...")
    
    try:
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('水印检测模型训练曲线', fontsize=16)
        
        # 损失曲线
        if 'train/box_loss' in df.columns and 'val/box_loss' in df.columns:
            axes[0, 0].plot(df['epoch'], df['train/box_loss'], label='训练损失', color='blue')
            axes[0, 0].plot(df['epoch'], df['val/box_loss'], label='验证损失', color='red')
            axes[0, 0].set_title('边界框损失')
            axes[0, 0].set_xlabel('训练轮数')
            axes[0, 0].set_ylabel('损失值')
            axes[0, 0].legend()
            axes[0, 0].grid(True)
        
        # mAP 曲线
        if 'metrics/mAP50(B)' in df.columns:
            axes[0, 1].plot(df['epoch'], df['metrics/mAP50(B)'], label='mAP50', color='green')
            axes[0, 1].set_title('mAP50')
            axes[0, 1].set_xlabel('训练轮数')
            axes[0, 1].set_ylabel('mAP50')
            axes[0, 1].legend()
            axes[0, 1].grid(True)
        
        if 'metrics/mAP50-95(B)' in df.columns:
            axes[1, 0].plot(df['epoch'], df['metrics/mAP50-95(B)'], label='mAP50-95', color='orange')
            axes[1, 0].set_title('mAP50-95')
            axes[1, 0].set_xlabel('训练轮数')
            axes[1, 0].set_ylabel('mAP50-95')
            axes[1, 0].legend()
            axes[1, 0].grid(True)
        
        # 学习率曲线
        if 'lr/pg0' in df.columns:
            axes[1, 1].plot(df['epoch'], df['lr/pg0'], label='学习率', color='purple')
            axes[1, 1].set_title('学习率')
            axes[1, 1].set_xlabel('训练轮数')
            axes[1, 1].set_ylabel('学习率')
            axes[1, 1].legend()
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        # 保存图像
        plot_path = experiment_dir / "training_curves.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"📊 训练曲线已保存: {plot_path}")
        
        plt.close()
        
    except Exception as e:
        print(f"❌ 生成训练曲线失败: {e}")

def check_model_files(experiment_dir):
    """检查模型文件"""
    print(f"\n📁 检查模型文件: {experiment_dir}")
    
    weights_dir = experiment_dir / "weights"
    if not weights_dir.exists():
        print("❌ 权重目录不存在")
        return
    
    # 检查模型文件
    model_files = {
        "best.pt": "最佳模型",
        "last.pt": "最新模型",
        "epoch_*.pt": "检查点模型"
    }
    
    for pattern, description in model_files.items():
        if pattern == "epoch_*.pt":
            epoch_files = list(weights_dir.glob("epoch_*.pt"))
            if epoch_files:
                print(f"✅ {description}: {len(epoch_files)} 个文件")
                for f in epoch_files[-3:]:  # 显示最后3个
                    size = f.stat().st_size / (1024 * 1024)  # MB
                    print(f"   - {f.name} ({size:.1f} MB)")
        else:
            model_file = weights_dir / pattern
            if model_file.exists():
                size = model_file.stat().st_size / (1024 * 1024)  # MB
                print(f"✅ {description}: {model_file.name} ({size:.1f} MB)")
            else:
                print(f"❌ {description}: 不存在")

def show_training_summary(experiment_dir):
    """显示训练摘要"""
    print(f"\n📋 训练摘要: {experiment_dir}")
    
    # 读取配置文件
    config_file = experiment_dir / "args.yaml"
    if config_file.exists():
        try:
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            print("📋 训练配置:")
            print(f"   数据集: {config.get('data', 'N/A')}")
            print(f"   模型: {config.get('model', 'N/A')}")
            print(f"   训练轮数: {config.get('epochs', 'N/A')}")
            print(f"   图像尺寸: {config.get('imgsz', 'N/A')}")
            print(f"   批大小: {config.get('batch', 'N/A')}")
            print(f"   设备: {config.get('device', 'N/A')}")
            print(f"   学习率: {config.get('lr0', 'N/A')}")
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
    
    # 检查训练日志
    log_file = experiment_dir / "train.log"
    if log_file.exists():
        print(f"📝 训练日志: {log_file}")
        # 显示最后几行
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    print("📝 最新日志:")
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
        except Exception as e:
            print(f"❌ 读取日志失败: {e}")

def main():
    """主函数"""
    print("📊 训练监控工具")
    print("=" * 50)
    
    # 检查训练状态
    experiment_dir = check_training_status()
    if not experiment_dir:
        return
    
    # 监控训练进度
    monitor_training_progress(experiment_dir)
    
    # 检查模型文件
    check_model_files(experiment_dir)
    
    # 显示训练摘要
    show_training_summary(experiment_dir)
    
    print("\n💡 提示:")
    print("   - 训练结果保存在 runs/train/ 目录")
    print("   - 最佳模型: runs/train/watermark_detector/weights/best.pt")
    print("   - 训练曲线: runs/train/watermark_detector/training_curves.png")
    print("   - 可以随时运行此脚本监控训练进度")

if __name__ == "__main__":
    main()
