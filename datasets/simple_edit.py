#!/usr/bin/env python3
"""
简单标注编辑工具
命令行版本，无GUI依赖
"""

import sys
from pathlib import Path

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

def save_annotation(label_path: Path, annotations):
    """保存标注文件"""
    try:
        with open(label_path, 'w') as f:
            for class_id, center_x, center_y, width, height in annotations:
                f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
        return True
    except Exception as e:
        print(f"❌ 保存标注失败 {label_path}: {e}")
        return False

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

def list_annotations(images_dir: Path, labels_dir: Path, max_count: int = 10):
    """列出标注信息"""
    image_files = sorted(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
    
    if not image_files:
        print(f"❌ 在 {images_dir} 中没有找到图像文件")
        return
    
    print(f"📊 找到 {len(image_files)} 张图像，显示前 {min(max_count, len(image_files))} 张")
    
    for i, image_path in enumerate(image_files[:max_count]):
        label_path = labels_dir / f"{image_path.stem}.txt"
        annotations = load_annotation(label_path)
        
        print(f"\n📷 {image_path.name}")
        print(f"   标注数量: {len(annotations)}")
        
        if annotations:
            for j, (class_id, center_x, center_y, width, height) in enumerate(annotations):
                print(f"   标注 {j+1}: center=({center_x:.3f}, {center_y:.3f}), size=({width:.3f}, {height:.3f})")

def show_dataset_stats():
    """显示数据集统计信息"""
    datasets_dir = Path("datasets/coco8")
    
    if not datasets_dir.exists():
        print("❌ 数据集目录不存在")
        return
    
    print("📊 数据集统计信息:")
    print("=" * 50)
    
    total_images = 0
    total_annotations = 0
    
    for split in ['train', 'val', 'test']:
        images_dir = datasets_dir / "images" / split
        labels_dir = datasets_dir / "labels" / split
        
        if images_dir.exists():
            image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
            image_count = len(image_files)
            total_images += image_count
            
            # 统计标注
            annotation_count = 0
            for image_path in image_files:
                label_path = labels_dir / f"{image_path.stem}.txt"
                annotations = load_annotation(label_path)
                annotation_count += len(annotations)
            
            total_annotations += annotation_count
            
            print(f"{split:>5}: {image_count:>3} 张图像, {annotation_count:>3} 个标注")
    
    print("=" * 50)
    print(f"总计: {total_images} 张图像, {total_annotations} 个标注")
    
    if total_images > 0:
        avg_annotations = total_annotations / total_images
        print(f"平均每张图像: {avg_annotations:.2f} 个标注")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="简单标注编辑工具")
    parser.add_argument("--action", type=str, default="stats",
                       choices=['stats', 'list', 'view'],
                       help="操作类型: stats(统计), list(列出), view(查看)")
    parser.add_argument("--split", type=str, default="train",
                       choices=['train', 'val', 'test'],
                       help="数据集分割")
    parser.add_argument("--count", type=int, default=10,
                       help="显示数量")
    
    args = parser.parse_args()
    
    datasets_dir = Path("datasets/coco8")
    
    if not datasets_dir.exists():
        print("❌ 数据集目录不存在")
        return
    
    if args.action == "stats":
        show_dataset_stats()
    
    elif args.action == "list":
        images_dir = datasets_dir / "images" / args.split
        labels_dir = datasets_dir / "labels" / args.split
        
        if not images_dir.exists():
            print(f"❌ 图像目录不存在: {images_dir}")
            return
        
        list_annotations(images_dir, labels_dir, args.count)
    
    elif args.action == "view":
        print("📋 查看标注的几种方法:")
        print("1. 使用文件管理器打开图像文件")
        print("2. 使用图像查看器查看 datasets/coco8/images/ 目录下的图像")
        print("3. 使用命令行工具:")
        print("   - feh datasets/coco8/images/train/")
        print("   - eog datasets/coco8/images/train/")
        print("   - gthumb datasets/coco8/images/train/")
        print("\n💡 标注位置信息:")
        print("   - 右下角水印: center=(0.85, 0.9), size=(0.15, 0.1)")
        print("   - 像素坐标: 根据图像尺寸计算")

if __name__ == "__main__":
    main()
