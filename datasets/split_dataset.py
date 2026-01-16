#!/usr/bin/env python3
"""
数据集分割脚本
将提取的图像按比例分割为训练集、验证集和测试集
"""

import random
import shutil
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sorawm.configs import ROOT

def split_dataset(
    source_images_dir: Path,
    target_dir: Path,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42
):
    """
    将图像数据集分割为训练、验证和测试集
    
    Args:
        source_images_dir: 源图像目录
        target_dir: 目标数据集目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例  
        test_ratio: 测试集比例
        seed: 随机种子
    """
    
    # 设置随机种子确保可重现性
    random.seed(seed)
    
    # 获取所有图像文件
    image_files = list(source_images_dir.glob("*.jpg"))
    print(f"📊 找到 {len(image_files)} 张图像")
    
    # 随机打乱文件列表
    random.shuffle(image_files)
    
    # 计算分割点
    total_count = len(image_files)
    train_count = int(total_count * train_ratio)
    val_count = int(total_count * val_ratio)
    
    # 分割文件列表
    train_files = image_files[:train_count]
    val_files = image_files[train_count:train_count + val_count]
    test_files = image_files[train_count + val_count:]
    
    print(f"📈 数据集分割:")
    print(f"   训练集: {len(train_files)} 张 ({len(train_files)/total_count*100:.1f}%)")
    print(f"   验证集: {len(val_files)} 张 ({len(val_files)/total_count*100:.1f}%)")
    print(f"   测试集: {len(test_files)} 张 ({len(test_files)/total_count*100:.1f}%)")
    
    # 复制文件到对应目录
    def copy_files(files, split_name):
        target_images_dir = target_dir / "images" / split_name
        target_labels_dir = target_dir / "labels" / split_name
        
        for image_file in files:
            # 复制图像文件
            shutil.copy2(image_file, target_images_dir)
            
            # 创建对应的标签文件（空文件，等待标注）
            label_file = target_labels_dir / f"{image_file.stem}.txt"
            label_file.touch()
    
    # 执行文件复制
    copy_files(train_files, "train")
    copy_files(val_files, "val")
    copy_files(test_files, "test")
    
    print(f"\n✅ 数据集分割完成!")
    print(f"📁 目标目录: {target_dir}")

def main():
    """主函数"""
    # 源图像目录（make_yolo_images.py 的输出）
    source_dir = ROOT / "datasets" / "images"
    
    # 目标数据集目录
    target_dir = ROOT / "datasets" / "coco8"
    
    if not source_dir.exists():
        print(f"❌ 源图像目录不存在: {source_dir}")
        print("请先运行 make_yolo_images.py 提取视频帧")
        return
    
    if not target_dir.exists():
        print(f"❌ 目标目录不存在: {target_dir}")
        print("请先运行 setup_yolo_dataset.py 创建目录结构")
        return
    
    # 执行数据集分割
    split_dataset(source_dir, target_dir)

if __name__ == "__main__":
    main()
