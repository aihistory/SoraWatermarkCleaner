#!/usr/bin/env python3
"""
标注编辑工具
用于查看、编辑和验证现有的标注文件
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

def view_annotations(images_dir: Path, labels_dir: Path, max_images: int = 10):
    """查看标注（无GUI版本）"""
    image_files = sorted(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
    
    if not image_files:
        print(f"❌ 在 {images_dir} 中没有找到图像文件")
        return
    
    print(f"📊 找到 {len(image_files)} 张图像，显示前 {min(max_images, len(image_files))} 张")
    
    for i, image_path in enumerate(image_files[:max_images]):
        label_path = labels_dir / f"{image_path.stem}.txt"
        
        # 加载图像和标注
        image = cv2.imread(str(image_path))
        if image is None:
            continue
        
        annotations = load_annotation(label_path)
        
        print(f"\n📷 {image_path.name}")
        print(f"   尺寸: {image.shape[1]}x{image.shape[0]}")
        print(f"   标注数量: {len(annotations)}")
        
        if annotations:
            for j, (class_id, center_x, center_y, width, height) in enumerate(annotations):
                # 转换为像素坐标显示
                x1, y1, x2, y2 = yolo_to_pixel(center_x, center_y, width, height, 
                                              image.shape[1], image.shape[0])
                print(f"   标注 {j+1}: YOLO=({center_x:.3f}, {center_y:.3f}, {width:.3f}, {height:.3f})")
                print(f"           像素=({x1}, {y1}) -> ({x2}, {y2})")
        
        # 保存可视化图像到临时文件
        if annotations:
            display_image = image.copy()
            display_image = draw_annotations(display_image, annotations)
            
            # 保存到临时目录
            temp_dir = Path("datasets/temp_visualizations")
            temp_dir.mkdir(exist_ok=True, parents=True)
            temp_path = temp_dir / f"vis_{image_path.name}"
            cv2.imwrite(str(temp_path), display_image)
            print(f"   💾 可视化图像已保存: {temp_path}")
        
        # 等待用户输入
        try:
            user_input = input("   按 Enter 继续，输入 'q' 退出查看: ").strip().lower()
            if user_input == 'q':
                break
        except KeyboardInterrupt:
            print("\n👋 退出查看")
            break

def edit_annotation_interactive(image_path: Path, label_path: Path):
    """交互式编辑单个图像的标注"""
    # 加载图像和标注
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ 无法加载图像: {image_path}")
        return
    
    annotations = load_annotation(label_path)
    
    print(f"\n📷 编辑图像: {image_path.name}")
    print(f"📊 当前标注数量: {len(annotations)}")
    
    if annotations:
        print("现有标注:")
        for i, (class_id, center_x, center_y, width, height) in enumerate(annotations):
            print(f"  {i+1}. center=({center_x:.3f}, {center_y:.3f}), size=({width:.3f}, {height:.3f})")
    
    while True:
        print("\n编辑选项:")
        print("1. 添加标注")
        print("2. 删除标注")
        print("3. 修改标注")
        print("4. 查看当前标注")
        print("5. 保存并退出")
        print("6. 退出不保存")
        
        choice = input("请选择 (1-6): ").strip()
        
        if choice == "1":
            # 添加新标注
            try:
                center_x = float(input("中心点X坐标 (0-1): "))
                center_y = float(input("中心点Y坐标 (0-1): "))
                width = float(input("宽度 (0-1): "))
                height = float(input("高度 (0-1): "))
                
                annotations.append((0, center_x, center_y, width, height))
                print("✅ 标注已添加")
            except ValueError:
                print("❌ 输入格式错误")
        
        elif choice == "2":
            # 删除标注
            if not annotations:
                print("❌ 没有标注可删除")
                continue
            
            try:
                index = int(input(f"删除第几个标注 (1-{len(annotations)}): ")) - 1
                if 0 <= index < len(annotations):
                    removed = annotations.pop(index)
                    print(f"✅ 已删除标注: {removed}")
                else:
                    print("❌ 无效索引")
            except ValueError:
                print("❌ 输入格式错误")
        
        elif choice == "3":
            # 修改标注
            if not annotations:
                print("❌ 没有标注可修改")
                continue
            
            try:
                index = int(input(f"修改第几个标注 (1-{len(annotations)}): ")) - 1
                if 0 <= index < len(annotations):
                    center_x = float(input("中心点X坐标 (0-1): "))
                    center_y = float(input("中心点Y坐标 (0-1): "))
                    width = float(input("宽度 (0-1): "))
                    height = float(input("高度 (0-1): "))
                    
                    annotations[index] = (0, center_x, center_y, width, height)
                    print("✅ 标注已修改")
                else:
                    print("❌ 无效索引")
            except ValueError:
                print("❌ 输入格式错误")
        
        elif choice == "4":
            # 查看当前标注
            if annotations:
                print("当前标注:")
                for i, (class_id, center_x, center_y, width, height) in enumerate(annotations):
                    print(f"  {i+1}. center=({center_x:.3f}, {center_y:.3f}), size=({width:.3f}, {height:.3f})")
            else:
                print("没有标注")
        
        elif choice == "5":
            # 保存并退出
            if save_annotation(label_path, annotations):
                print("✅ 标注已保存")
            break
        
        elif choice == "6":
            # 退出不保存
            print("❌ 未保存更改")
            break
        
        else:
            print("❌ 无效选择")

def main():
    """主函数"""
    print("🎯 标注编辑工具")
    print("=" * 50)
    
    # 检查数据集目录
    datasets_dir = Path("datasets/coco8")
    if not datasets_dir.exists():
        print("❌ 数据集目录不存在")
        return
    
    print("📁 选择数据集:")
    print("1. 训练集 (train)")
    print("2. 验证集 (val)")
    print("3. 测试集 (test)")
    
    while True:
        try:
            choice = input("请选择 (1-3): ").strip()
            
            if choice == "1":
                split = "train"
                break
            elif choice == "2":
                split = "val"
                break
            elif choice == "3":
                split = "test"
                break
            else:
                print("❌ 无效选择")
        
        except KeyboardInterrupt:
            print("\n👋 退出")
            return
    
    images_dir = datasets_dir / "images" / split
    labels_dir = datasets_dir / "labels" / split
    
    if not images_dir.exists():
        print(f"❌ 图像目录不存在: {images_dir}")
        return
    
    print(f"\n🛠️  选择操作:")
    print("1. 查看标注")
    print("2. 编辑标注")
    
    while True:
        try:
            op_choice = input("请选择 (1-2): ").strip()
            
            if op_choice == "1":
                view_annotations(images_dir, labels_dir)
                break
            elif op_choice == "2":
                # 选择要编辑的图像
                image_files = sorted(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
                if not image_files:
                    print("❌ 没有找到图像文件")
                    return
                
                print(f"\n📷 选择要编辑的图像 (1-{len(image_files)}):")
                for i, img_path in enumerate(image_files[:10]):  # 只显示前10个
                    print(f"  {i+1}. {img_path.name}")
                
                if len(image_files) > 10:
                    print(f"  ... 还有 {len(image_files) - 10} 个文件")
                
                try:
                    img_choice = int(input("请选择: ")) - 1
                    if 0 <= img_choice < len(image_files):
                        image_path = image_files[img_choice]
                        label_path = labels_dir / f"{image_path.stem}.txt"
                        edit_annotation_interactive(image_path, label_path)
                    else:
                        print("❌ 无效选择")
                except ValueError:
                    print("❌ 输入格式错误")
                break
            else:
                print("❌ 无效选择")
        
        except KeyboardInterrupt:
            print("\n👋 退出")
            break

if __name__ == "__main__":
    main()
