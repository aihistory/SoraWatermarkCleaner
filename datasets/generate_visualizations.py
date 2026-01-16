#!/usr/bin/env python3
"""
生成可视化图像
创建带标注框的图像，用于查看标注效果
"""

import sys
from pathlib import Path
import cv2
import numpy as np

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_annotation(label_path: Path):
    """加载标注文件"""
    annotations = []
    if label_path.exists():
        try:
            with open(label_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) == 5:
                            class_id = int(parts[0])
                            center_x = float(parts[1])
                            center_y = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])
                            annotations.append((class_id, center_x, center_y, width, height))
        except Exception as e:
            print(f"❌ 加载标注失败 {label_path}: {e}")
    return annotations

def yolo_to_pixel(center_x, center_y, width, height, img_width, img_height):
    """YOLO格式转像素坐标"""
    center_x_px = int(center_x * img_width)
    center_y_px = int(center_y * img_height)
    width_px = int(width * img_width)
    height_px = int(height * img_height)
    
    x1 = center_x_px - width_px // 2
    y1 = center_y_px - height_px // 2
    x2 = center_x_px + width_px // 2
    y2 = center_y_px + height_px // 2
    
    return x1, y1, x2, y2

def draw_annotations(image, annotations):
    """在图像上绘制标注"""
    img_height, img_width = image.shape[:2]
    
    for i, (class_id, center_x, center_y, width, height) in enumerate(annotations):
        x1, y1, x2, y2 = yolo_to_pixel(center_x, center_y, width, height, img_width, img_height)
        
        # 绘制边界框
        color = (0, 255, 0)  # 绿色
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # 绘制标签
        label = f"watermark {i+1}"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return image

def generate_visualizations(images_dir: Path, labels_dir: Path, output_dir: Path, max_count: int = 20):
    """生成可视化图像"""
    image_files = sorted(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
    
    if not image_files:
        print(f"❌ 在 {images_dir} 中没有找到图像文件")
        return
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"📊 找到 {len(image_files)} 张图像，生成前 {min(max_count, len(image_files))} 张的可视化图像")
    
    success_count = 0
    
    for i, image_path in enumerate(image_files[:max_count]):
        label_path = labels_dir / f"{image_path.stem}.txt"
        
        # 加载图像和标注
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ 无法读取图像: {image_path}")
            continue
        
        annotations = load_annotation(label_path)
        
        if annotations:
            # 绘制标注
            display_image = image.copy()
            display_image = draw_annotations(display_image, annotations)
            
            # 保存可视化图像
            output_path = output_dir / f"vis_{image_path.name}"
            cv2.imwrite(str(output_path), display_image)
            success_count += 1
            
            if (i + 1) % 10 == 0:
                print(f"📝 已生成 {i + 1}/{min(max_count, len(image_files))} 张可视化图像")
        else:
            print(f"⚠️  {image_path.name}: 没有标注")
    
    print(f"✅ 可视化图像生成完成! 成功生成 {success_count} 张图像")
    print(f"📁 输出目录: {output_dir}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成标注可视化图像")
    parser.add_argument("--split", type=str, default="train",
                       choices=['train', 'val', 'test'],
                       help="数据集分割")
    parser.add_argument("--count", type=int, default=20,
                       help="生成数量")
    parser.add_argument("--output", type=str, default="datasets/visualizations",
                       help="输出目录")
    
    args = parser.parse_args()
    
    datasets_dir = Path("datasets/coco8")
    
    if not datasets_dir.exists():
        print("❌ 数据集目录不存在")
        return
    
    images_dir = datasets_dir / "images" / args.split
    labels_dir = datasets_dir / "labels" / args.split
    output_dir = Path(args.output) / args.split
    
    if not images_dir.exists():
        print(f"❌ 图像目录不存在: {images_dir}")
        return
    
    generate_visualizations(images_dir, labels_dir, output_dir, args.count)

if __name__ == "__main__":
    main()
