#!/usr/bin/env python3
"""
无GUI标注工具
通过命令行交互进行水印标注，不依赖图形界面
"""

import sys
from pathlib import Path
import cv2
import numpy as np

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class HeadlessAnnotator:
    """无GUI标注工具"""
    
    def __init__(self, images_dir: Path, labels_dir: Path):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.labels_dir.mkdir(exist_ok=True, parents=True)
        
        # 获取所有图像文件
        self.image_files = sorted(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
        self.current_index = 0
        
        print(f"📁 图像目录: {images_dir}")
        print(f"📁 标签目录: {labels_dir}")
        print(f"📊 总共 {len(self.image_files)} 张图像")
        
    def get_image_info(self, image_path: Path):
        """获取图像信息"""
        try:
            # 使用 OpenCV 读取图像信息（不显示）
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            
            height, width = image.shape[:2]
            return {
                'width': width,
                'height': height,
                'channels': image.shape[2] if len(image.shape) > 2 else 1
            }
        except Exception as e:
            print(f"❌ 读取图像信息失败: {e}")
            return None
    
    def load_annotations(self, image_path: Path):
        """加载现有标注"""
        label_path = self.labels_dir / f"{image_path.stem}.txt"
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
                print(f"⚠️  加载标注文件失败: {e}")
        
        return annotations
    
    def save_annotations(self, image_path: Path, annotations):
        """保存标注到文件"""
        label_path = self.labels_dir / f"{image_path.stem}.txt"
        
        try:
            with open(label_path, 'w') as f:
                for class_id, center_x, center_y, width, height in annotations:
                    f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
            print(f"💾 已保存 {len(annotations)} 个标注到 {label_path}")
            return True
        except Exception as e:
            print(f"❌ 保存标注失败: {e}")
            return False
    
    def yolo_to_pixel(self, center_x, center_y, width, height, img_width, img_height):
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
    
    def pixel_to_yolo(self, x1, y1, x2, y2, img_width, img_height):
        """像素坐标转YOLO格式"""
        center_x = (x1 + x2) / 2 / img_width
        center_y = (y1 + y2) / 2 / img_height
        width = abs(x2 - x1) / img_width
        height = abs(y2 - y1) / img_height
        
        return center_x, center_y, width, height
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
🎯 无GUI水印标注工具使用说明:

标注方式:
  1. 手动输入坐标: 根据图像尺寸输入像素坐标
  2. 相对坐标: 直接输入YOLO格式的相对坐标 (0-1)
  3. 预设模板: 使用常见的水印位置模板

坐标系统:
  - 像素坐标: (0,0) 在左上角，向右向下递增
  - YOLO坐标: 相对坐标，范围 0-1，中心点格式

操作命令:
  - 'add': 添加新标注
  - 'del': 删除标注
  - 'list': 显示当前标注
  - 'save': 保存标注
  - 'next': 下一张图像
  - 'prev': 上一张图像
  - 'help': 显示帮助
  - 'quit': 退出
        """
        print(help_text)
    
    def add_annotation_manual(self, img_width, img_height):
        """手动添加标注"""
        print(f"\n📐 图像尺寸: {img_width} x {img_height}")
        print("选择输入方式:")
        print("1. 像素坐标 (x1, y1, x2, y2)")
        print("2. YOLO相对坐标 (center_x, center_y, width, height)")
        print("3. 预设模板")
        
        try:
            choice = input("请选择 (1-3): ").strip()
            
            if choice == "1":
                # 像素坐标输入
                print("输入边界框的像素坐标:")
                x1 = int(input("左上角X坐标: "))
                y1 = int(input("左上角Y坐标: "))
                x2 = int(input("右下角X坐标: "))
                y2 = int(input("右下角Y坐标: "))
                
                # 转换为YOLO格式
                center_x, center_y, width, height = self.pixel_to_yolo(x1, y1, x2, y2, img_width, img_height)
                
            elif choice == "2":
                # YOLO坐标输入
                print("输入YOLO格式的相对坐标 (0-1):")
                center_x = float(input("中心点X坐标 (0-1): "))
                center_y = float(input("中心点Y坐标 (0-1): "))
                width = float(input("宽度 (0-1): "))
                height = float(input("高度 (0-1): "))
                
            elif choice == "3":
                # 预设模板
                print("选择预设模板:")
                print("1. 右下角水印 (15% x 10%)")
                print("2. 左下角水印 (15% x 10%)")
                print("3. 右上角水印 (15% x 10%)")
                print("4. 左上角水印 (15% x 10%)")
                print("5. 底部中央水印 (20% x 8%)")
                
                template_choice = input("请选择模板 (1-5): ").strip()
                
                if template_choice == "1":
                    center_x, center_y, width, height = 0.85, 0.9, 0.15, 0.1
                elif template_choice == "2":
                    center_x, center_y, width, height = 0.15, 0.9, 0.15, 0.1
                elif template_choice == "3":
                    center_x, center_y, width, height = 0.85, 0.1, 0.15, 0.1
                elif template_choice == "4":
                    center_x, center_y, width, height = 0.15, 0.1, 0.15, 0.1
                elif template_choice == "5":
                    center_x, center_y, width, height = 0.5, 0.9, 0.2, 0.08
                else:
                    print("❌ 无效选择")
                    return None
            else:
                print("❌ 无效选择")
                return None
            
            # 验证坐标
            if not (0 <= center_x <= 1 and 0 <= center_y <= 1 and 0 < width <= 1 and 0 < height <= 1):
                print("❌ 坐标超出有效范围 (0-1)")
                return None
            
            # 显示转换后的像素坐标
            x1, y1, x2, y2 = self.yolo_to_pixel(center_x, center_y, width, height, img_width, img_height)
            print(f"✅ 标注坐标:")
            print(f"   YOLO格式: center=({center_x:.3f}, {center_y:.3f}), size=({width:.3f}, {height:.3f})")
            print(f"   像素格式: ({x1}, {y1}) -> ({x2}, {y2})")
            
            return (0, center_x, center_y, width, height)
            
        except ValueError:
            print("❌ 输入格式错误")
            return None
        except KeyboardInterrupt:
            print("\n❌ 操作已取消")
            return None
    
    def run(self):
        """运行标注工具"""
        if not self.image_files:
            print("❌ 没有找到图像文件")
            return
        
        self.show_help()
        
        while self.current_index < len(self.image_files):
            image_path = self.image_files[self.current_index]
            
            # 获取图像信息
            img_info = self.get_image_info(image_path)
            if img_info is None:
                print(f"❌ 无法读取图像: {image_path}")
                self.current_index += 1
                continue
            
            # 加载现有标注
            annotations = self.load_annotations(image_path)
            
            print(f"\n📷 当前图像: {image_path.name} ({self.current_index + 1}/{len(self.image_files)})")
            print(f"📐 图像尺寸: {img_info['width']} x {img_info['height']}")
            print(f"📊 已有标注: {len(annotations)} 个")
            
            if annotations:
                print("现有标注:")
                for i, (class_id, center_x, center_y, width, height) in enumerate(annotations):
                    x1, y1, x2, y2 = self.yolo_to_pixel(center_x, center_y, width, height, 
                                                       img_info['width'], img_info['height'])
                    print(f"  {i+1}. YOLO=({center_x:.3f}, {center_y:.3f}, {width:.3f}, {height:.3f}) "
                          f"像素=({x1}, {y1}, {x2}, {y2})")
            
            # 交互式标注
            while True:
                try:
                    command = input(f"\n[{image_path.name}] 请输入命令 (help查看帮助): ").strip().lower()
                    
                    if command == "help":
                        self.show_help()
                    
                    elif command == "add":
                        new_annotation = self.add_annotation_manual(img_info['width'], img_info['height'])
                        if new_annotation:
                            annotations.append(new_annotation)
                            print(f"✅ 已添加标注，当前共 {len(annotations)} 个")
                    
                    elif command == "del":
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
                    
                    elif command == "list":
                        if annotations:
                            print("当前标注:")
                            for i, (class_id, center_x, center_y, width, height) in enumerate(annotations):
                                x1, y1, x2, y2 = self.yolo_to_pixel(center_x, center_y, width, height, 
                                                                   img_info['width'], img_info['height'])
                                print(f"  {i+1}. YOLO=({center_x:.3f}, {center_y:.3f}, {width:.3f}, {height:.3f}) "
                                      f"像素=({x1}, {y1}, {x2}, {y2})")
                        else:
                            print("没有标注")
                    
                    elif command == "save":
                        if self.save_annotations(image_path, annotations):
                            print("✅ 标注已保存")
                    
                    elif command == "next" or command == "n":
                        # 保存当前标注
                        self.save_annotations(image_path, annotations)
                        self.current_index += 1
                        break
                    
                    elif command == "prev" or command == "p":
                        if self.current_index > 0:
                            # 保存当前标注
                            self.save_annotations(image_path, annotations)
                            self.current_index -= 1
                            break
                        else:
                            print("❌ 已经是第一张图像")
                    
                    elif command == "quit" or command == "q":
                        # 保存当前标注
                        self.save_annotations(image_path, annotations)
                        print("👋 退出标注工具")
                        return
                    
                    else:
                        print("❌ 未知命令，输入 'help' 查看帮助")
                
                except KeyboardInterrupt:
                    print("\n👋 退出标注工具")
                    return
                except Exception as e:
                    print(f"❌ 发生错误: {e}")
        
        print("🎉 所有图像已标注完成!")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="无GUI水印标注工具")
    parser.add_argument("--images", type=str, default="datasets/coco8/images/train",
                       help="图像目录路径")
    parser.add_argument("--labels", type=str, default="datasets/coco8/labels/train",
                       help="标签目录路径")
    
    args = parser.parse_args()
    
    images_dir = Path(args.images)
    labels_dir = Path(args.labels)
    
    if not images_dir.exists():
        print(f"❌ 图像目录不存在: {images_dir}")
        return
    
    # 创建标注工具并运行
    annotator = HeadlessAnnotator(images_dir, labels_dir)
    annotator.run()

if __name__ == "__main__":
    main()
