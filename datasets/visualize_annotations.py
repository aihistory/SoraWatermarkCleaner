#!/usr/bin/env python3
"""
标注可视化脚本
在图像上绘制边界框，验证标注质量
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

def draw_yolo_bbox(image: np.ndarray, center_x: float, center_y: float, 
                   width: float, height: float, class_id: int = 0, 
                   color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    """
    在图像上绘制 YOLO 格式的边界框
    
    Args:
        image: 输入图像
        center_x: 中心点X坐标 (相对坐标 0-1)
        center_y: 中心点Y坐标 (相对坐标 0-1)
        width: 宽度 (相对坐标 0-1)
        height: 高度 (相对坐标 0-1)
        class_id: 类别ID
        color: 边界框颜色 (BGR格式)
        
    Returns:
        绘制了边界框的图像
    """
    img_height, img_width = image.shape[:2]
    
    # 转换为绝对坐标
    center_x_abs = int(center_x * img_width)
    center_y_abs = int(center_y * img_height)
    width_abs = int(width * img_width)
    height_abs = int(height * img_height)
    
    # 计算边界框坐标
    x1 = center_x_abs - width_abs // 2
    y1 = center_y_abs - height_abs // 2
    x2 = center_x_abs + width_abs // 2
    y2 = center_y_abs + height_abs // 2
    
    # 绘制边界框
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    
    # 绘制类别标签
    label = f"watermark (ID: {class_id})"
    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
    
    # 标签背景
    cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                  (x1 + label_size[0], y1), color, -1)
    
    # 标签文字
    cv2.putText(image, label, (x1, y1 - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return image

def visualize_annotations(image_path: Path, label_path: Path, 
                         output_path: Path = None) -> np.ndarray:
    """
    可视化单个图像的标注
    
    Args:
        image_path: 图像文件路径
        label_path: 标签文件路径
        output_path: 输出图像路径（可选）
        
    Returns:
        可视化后的图像
    """
    # 读取图像
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"无法读取图像: {image_path}")
    
    # 读取标签文件
    if not label_path.exists():
        print(f"⚠️  标签文件不存在: {label_path}")
        return image
    
    with open(label_path, 'r') as f:
        lines = f.readlines()
    
    # 绘制每个标注
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        parts = line.split()
        if len(parts) != 5:
            continue
            
        try:
            class_id = int(parts[0])
            center_x = float(parts[1])
            center_y = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            
            # 选择颜色
            color = colors[i % len(colors)]
            
            # 绘制边界框
            image = draw_yolo_bbox(image, center_x, center_y, width, height, 
                                 class_id, color)
        except ValueError:
            continue
    
    # 保存可视化结果
    if output_path:
        cv2.imwrite(str(output_path), image)
        print(f"💾 可视化结果已保存: {output_path}")
    
    return image

def visualize_dataset_sample(dataset_dir: Path, split: str = "train", 
                           num_samples: int = 5, output_dir: Path = None):
    """
    可视化数据集样本
    
    Args:
        dataset_dir: 数据集目录
        split: 数据集分割 (train/val/test)
        num_samples: 可视化样本数量
        output_dir: 输出目录
    """
    images_dir = dataset_dir / "images" / split
    labels_dir = dataset_dir / "labels" / split
    
    if not images_dir.exists():
        print(f"❌ 图像目录不存在: {images_dir}")
        return
    
    # 获取图像文件列表
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
    
    if not image_files:
        print(f"❌ 在 {images_dir} 中没有找到图像文件")
        return
    
    # 随机选择样本
    import random
    random.seed(42)
    sample_files = random.sample(image_files, min(num_samples, len(image_files)))
    
    print(f"🎨 可视化 {len(sample_files)} 个 {split} 集样本...")
    
    for i, image_file in enumerate(sample_files):
        label_file = labels_dir / f"{image_file.stem}.txt"
        
        # 设置输出路径
        if output_dir:
            output_path = output_dir / f"visualization_{i+1}_{image_file.name}"
            output_dir.mkdir(exist_ok=True, parents=True)
        else:
            output_path = None
        
        try:
            # 可视化标注
            vis_image = visualize_annotations(image_file, label_file, output_path)
            
            # 显示图像（如果可能）
            try:
                cv2.imshow(f"Annotation Visualization - {image_file.name}", vis_image)
                print(f"📷 显示图像: {image_file.name} (按任意键继续)")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            except:
                print(f"📷 无法显示图像: {image_file.name}")
                
        except Exception as e:
            print(f"❌ 处理图像失败 {image_file.name}: {e}")

def main():
    """主函数"""
    dataset_dir = ROOT / "datasets" / "coco8"
    
    if not dataset_dir.exists():
        print(f"❌ 数据集目录不存在: {dataset_dir}")
        print("请先运行 setup_yolo_dataset.py 和 split_dataset.py")
        return
    
    # 创建可视化输出目录
    output_dir = ROOT / "datasets" / "visualizations"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("🎨 开始可视化标注...")
    
    # 可视化各个分割集的样本
    for split in ['train', 'val', 'test']:
        print(f"\n📊 可视化 {split} 集样本:")
        visualize_dataset_sample(dataset_dir, split, num_samples=3, 
                               output_dir=output_dir / split)
    
    print(f"\n✅ 可视化完成! 结果保存在: {output_dir}")

if __name__ == "__main__":
    main()
