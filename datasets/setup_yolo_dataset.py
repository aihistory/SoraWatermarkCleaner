#!/usr/bin/env python3
"""
YOLO 数据集目录结构创建脚本
为水印检测模型准备训练数据目录
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sorawm.configs import ROOT

def setup_yolo_dataset():
    """创建 YOLO 训练所需的目录结构"""
    
    # 数据集根目录
    datasets_dir = ROOT / "datasets"
    coco8_dir = datasets_dir / "coco8"
    
    # 创建目录结构
    directories = [
        coco8_dir / "images" / "train",
        coco8_dir / "images" / "val", 
        coco8_dir / "images" / "test",
        coco8_dir / "labels" / "train",
        coco8_dir / "labels" / "val",
        coco8_dir / "labels" / "test",
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True, parents=True)
        print(f"创建目录: {directory}")
    
    print(f"\n✅ YOLO 数据集目录结构已创建完成!")
    print(f"📁 数据集根目录: {coco8_dir}")
    print(f"🖼️  图像目录: {coco8_dir / 'images'}")
    print(f"🏷️  标签目录: {coco8_dir / 'labels'}")
    
    return coco8_dir

if __name__ == "__main__":
    setup_yolo_dataset()
