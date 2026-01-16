#!/usr/bin/env python3
"""
批量标注脚本
为所有图像创建基础的水印标注模板
"""

import sys
from pathlib import Path
import cv2
import numpy as np

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_template_annotation(image_path: Path, label_path: Path):
    """
    为图像创建模板标注
    在图像中心创建一个示例水印标注
    """
    # 读取图像获取尺寸
    image = cv2.imread(str(image_path))
    if image is None:
        return False
    
    height, width = image.shape[:2]
    
    # 在图像中心创建一个示例水印标注
    # 假设水印在图像右下角，占图像的 10% x 5%
    center_x = 0.85  # 右下角
    center_y = 0.9   # 右下角
    bbox_width = 0.15   # 宽度占图像的 15%
    bbox_height = 0.1   # 高度占图像的 10%
    
    # 保存 YOLO 格式标注
    try:
        with open(label_path, 'w') as f:
            f.write(f"0 {center_x:.6f} {center_y:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")
        return True
    except Exception as e:
        print(f"❌ 保存标注失败 {label_path}: {e}")
        return False

def batch_create_annotations(images_dir: Path, labels_dir: Path):
    """批量创建标注文件"""
    labels_dir.mkdir(exist_ok=True, parents=True)
    
    # 获取所有图像文件
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
    
    if not image_files:
        print(f"❌ 在 {images_dir} 中没有找到图像文件")
        return
    
    print(f"📊 找到 {len(image_files)} 张图像")
    print("⚠️  注意: 这将为所有图像创建模板标注，您需要手动调整")
    
    # 确认操作
    confirm = input("是否继续? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作已取消")
        return
    
    success_count = 0
    for i, image_path in enumerate(image_files):
        label_path = labels_dir / f"{image_path.stem}.txt"
        
        if create_template_annotation(image_path, label_path):
            success_count += 1
        
        if (i + 1) % 50 == 0:
            print(f"📝 已处理 {i + 1}/{len(image_files)} 张图像")
    
    print(f"✅ 批量标注完成! 成功创建 {success_count}/{len(image_files)} 个标注文件")
    print(f"📁 标注文件保存在: {labels_dir}")

def main():
    """主函数"""
    print("🎯 批量水印标注工具")
    print("=" * 50)
    
    # 检查数据集目录
    datasets_dir = Path("datasets/coco8")
    if not datasets_dir.exists():
        print("❌ 数据集目录不存在，请先运行:")
        print("   uv run python datasets/setup_yolo_dataset.py")
        print("   uv run python datasets/split_dataset.py")
        return
    
    print("📁 数据集目录结构:")
    for split in ['train', 'val', 'test']:
        images_dir = datasets_dir / "images" / split
        labels_dir = datasets_dir / "labels" / split
        
        if images_dir.exists():
            image_count = len(list(images_dir.glob("*.jpg")))
            print(f"   {split}: {image_count} 张图像")
    
    print("\n🛠️  选择操作:")
    print("1. 为训练集创建模板标注")
    print("2. 为验证集创建模板标注")
    print("3. 为测试集创建模板标注")
    print("4. 为所有数据集创建模板标注")
    print("5. 退出")
    
    while True:
        try:
            choice = input("\n请选择操作 (1-5): ").strip()
            
            if choice == "1":
                images_dir = datasets_dir / "images" / "train"
                labels_dir = datasets_dir / "labels" / "train"
                batch_create_annotations(images_dir, labels_dir)
                break
                
            elif choice == "2":
                images_dir = datasets_dir / "images" / "val"
                labels_dir = datasets_dir / "labels" / "val"
                batch_create_annotations(images_dir, labels_dir)
                break
                
            elif choice == "3":
                images_dir = datasets_dir / "images" / "test"
                labels_dir = datasets_dir / "labels" / "test"
                batch_create_annotations(images_dir, labels_dir)
                break
                
            elif choice == "4":
                for split in ['train', 'val', 'test']:
                    print(f"\n📝 处理 {split} 集...")
                    images_dir = datasets_dir / "images" / split
                    labels_dir = datasets_dir / "labels" / split
                    batch_create_annotations(images_dir, labels_dir)
                break
                
            elif choice == "5":
                print("👋 退出")
                break
                
            else:
                print("❌ 无效选择，请输入 1-5")
                
        except KeyboardInterrupt:
            print("\n👋 退出")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()
