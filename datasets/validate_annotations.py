#!/usr/bin/env python3
"""
标注验证脚本
验证 YOLO 标注文件的格式和内容正确性
"""

import cv2
import numpy as np
import sys
from pathlib import Path
from typing import List, Tuple

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sorawm.configs import ROOT

def validate_yolo_annotation(image_path: Path, label_path: Path) -> List[str]:
    """
    验证单个图像的标注文件
    
    Args:
        image_path: 图像文件路径
        label_path: 标签文件路径
        
    Returns:
        错误信息列表
    """
    errors = []
    
    # 检查图像文件是否存在
    if not image_path.exists():
        errors.append(f"图像文件不存在: {image_path}")
        return errors
    
    # 检查标签文件是否存在
    if not label_path.exists():
        errors.append(f"标签文件不存在: {label_path}")
        return errors
    
    # 读取图像尺寸
    image = cv2.imread(str(image_path))
    if image is None:
        errors.append(f"无法读取图像: {image_path}")
        return errors
    
    img_height, img_width = image.shape[:2]
    
    # 读取标签文件
    try:
        with open(label_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        errors.append(f"无法读取标签文件 {label_path}: {e}")
        return errors
    
    # 验证每一行标注
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:  # 跳过空行
            continue
            
        parts = line.split()
        if len(parts) != 5:
            errors.append(f"第{line_num}行格式错误: 应为5个值，实际{len(parts)}个")
            continue
        
        try:
            class_id = int(parts[0])
            center_x = float(parts[1])
            center_y = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
        except ValueError as e:
            errors.append(f"第{line_num}行数值格式错误: {e}")
            continue
        
        # 验证类别ID
        if class_id != 0:  # 根据 coco8.yaml，只有类别0 (watermark)
            errors.append(f"第{line_num}行类别ID错误: 应为0，实际{class_id}")
        
        # 验证坐标范围 (YOLO格式使用相对坐标 0-1)
        if not (0 <= center_x <= 1):
            errors.append(f"第{line_num}行center_x超出范围: {center_x}")
        if not (0 <= center_y <= 1):
            errors.append(f"第{line_num}行center_y超出范围: {center_y}")
        if not (0 < width <= 1):
            errors.append(f"第{line_num}行width超出范围: {width}")
        if not (0 < height <= 1):
            errors.append(f"第{line_num}行height超出范围: {height}")
        
        # 验证边界框是否超出图像边界
        bbox_x1 = (center_x - width/2) * img_width
        bbox_y1 = (center_y - height/2) * img_height
        bbox_x2 = (center_x + width/2) * img_width
        bbox_y2 = (center_y + height/2) * img_height
        
        if bbox_x1 < 0 or bbox_y1 < 0 or bbox_x2 > img_width or bbox_y2 > img_height:
            errors.append(f"第{line_num}行边界框超出图像范围")
    
    return errors

def validate_dataset(dataset_dir: Path) -> dict:
    """
    验证整个数据集
    
    Args:
        dataset_dir: 数据集目录路径
        
    Returns:
        验证结果统计
    """
    results = {
        'total_images': 0,
        'total_labels': 0,
        'valid_annotations': 0,
        'invalid_annotations': 0,
        'errors': []
    }
    
    # 检查数据集目录结构
    images_dir = dataset_dir / "images"
    labels_dir = dataset_dir / "labels"
    
    if not images_dir.exists():
        results['errors'].append(f"图像目录不存在: {images_dir}")
        return results
    
    if not labels_dir.exists():
        results['errors'].append(f"标签目录不存在: {labels_dir}")
        return results
    
    # 遍历所有分割集
    for split in ['train', 'val', 'test']:
        split_images_dir = images_dir / split
        split_labels_dir = labels_dir / split
        
        if not split_images_dir.exists():
            continue
            
        print(f"🔍 验证 {split} 集...")
        
        # 获取所有图像文件
        image_files = list(split_images_dir.glob("*.jpg")) + list(split_images_dir.glob("*.png"))
        results['total_images'] += len(image_files)
        
        for image_file in image_files:
            # 对应的标签文件
            label_file = split_labels_dir / f"{image_file.stem}.txt"
            
            if label_file.exists():
                results['total_labels'] += 1
            
            # 验证标注
            errors = validate_yolo_annotation(image_file, label_file)
            
            if errors:
                results['invalid_annotations'] += 1
                results['errors'].extend([f"{image_file.name}: {error}" for error in errors])
            else:
                results['valid_annotations'] += 1
    
    return results

def print_validation_report(results: dict):
    """打印验证报告"""
    print("\n" + "="*50)
    print("📊 标注验证报告")
    print("="*50)
    
    print(f"📈 统计信息:")
    print(f"   总图像数: {results['total_images']}")
    print(f"   总标签数: {results['total_labels']}")
    print(f"   有效标注: {results['valid_annotations']}")
    print(f"   无效标注: {results['invalid_annotations']}")
    
    if results['total_images'] > 0:
        coverage = results['total_labels'] / results['total_images'] * 100
        print(f"   标注覆盖率: {coverage:.1f}%")
    
    if results['errors']:
        print(f"\n❌ 发现 {len(results['errors'])} 个错误:")
        for error in results['errors'][:10]:  # 只显示前10个错误
            print(f"   • {error}")
        
        if len(results['errors']) > 10:
            print(f"   ... 还有 {len(results['errors']) - 10} 个错误")
    else:
        print(f"\n✅ 所有标注都通过验证!")

def main():
    """主函数"""
    dataset_dir = ROOT / "datasets" / "coco8"
    
    if not dataset_dir.exists():
        print(f"❌ 数据集目录不存在: {dataset_dir}")
        print("请先运行 setup_yolo_dataset.py 和 split_dataset.py")
        return
    
    print("🔍 开始验证标注文件...")
    results = validate_dataset(dataset_dir)
    print_validation_report(results)

if __name__ == "__main__":
    main()
