#!/usr/bin/env python3
"""
简单的水印标注工具
基于 OpenCV 的轻量级标注工具，专门用于水印检测数据标注
"""

import cv2
import numpy as np
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class SimpleAnnotator:
    """简单的水印标注工具"""
    
    def __init__(self, images_dir: Path, labels_dir: Path):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.labels_dir.mkdir(exist_ok=True, parents=True)
        
        # 获取所有图像文件
        self.image_files = sorted(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
        self.current_index = 0
        
        # 标注状态
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.annotations = []  # 当前图像的标注列表
        
        # 图像显示参数
        self.window_name = "水印标注工具 - 按 'h' 查看帮助"
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        print(f"📁 图像目录: {images_dir}")
        print(f"📁 标签目录: {labels_dir}")
        print(f"📊 总共 {len(self.image_files)} 张图像")
        
    def load_annotations(self, image_path: Path) -> List[Tuple[float, float, float, float]]:
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
                                annotations.append((center_x, center_y, width, height))
            except Exception as e:
                print(f"⚠️  加载标注文件失败: {e}")
        
        return annotations
    
    def save_annotations(self, image_path: Path, annotations: List[Tuple[float, float, float, float]]):
        """保存标注到文件"""
        label_path = self.labels_dir / f"{image_path.stem}.txt"
        
        try:
            with open(label_path, 'w') as f:
                for center_x, center_y, width, height in annotations:
                    f.write(f"0 {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
            print(f"💾 已保存 {len(annotations)} 个标注到 {label_path}")
        except Exception as e:
            print(f"❌ 保存标注失败: {e}")
    
    def yolo_to_pixel(self, center_x: float, center_y: float, width: float, height: float, 
                     img_width: int, img_height: int) -> Tuple[int, int, int, int]:
        """将 YOLO 格式转换为像素坐标"""
        center_x_px = int(center_x * img_width)
        center_y_px = int(center_y * img_height)
        width_px = int(width * img_width)
        height_px = int(height * img_height)
        
        x1 = center_x_px - width_px // 2
        y1 = center_y_px - height_px // 2
        x2 = center_x_px + width_px // 2
        y2 = center_y_px + height_px // 2
        
        return x1, y1, x2, y2
    
    def pixel_to_yolo(self, x1: int, y1: int, x2: int, y2: int, 
                     img_width: int, img_height: int) -> Tuple[float, float, float, float]:
        """将像素坐标转换为 YOLO 格式"""
        center_x = (x1 + x2) / 2 / img_width
        center_y = (y1 + y2) / 2 / img_height
        width = abs(x2 - x1) / img_width
        height = abs(y2 - y1) / img_height
        
        return center_x, center_y, width, height
    
    def mouse_callback(self, event, x, y, flags, param):
        """鼠标回调函数"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.end_point = (x, y)
            
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            if self.start_point and self.end_point:
                # 添加标注
                x1, y1 = self.start_point
                x2, y2 = self.end_point
                
                # 确保坐标正确
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                
                # 转换为 YOLO 格式
                img_height, img_width = self.current_image.shape[:2]
                center_x, center_y, width, height = self.pixel_to_yolo(x1, y1, x2, y2, img_width, img_height)
                
                # 添加到标注列表
                self.annotations.append((center_x, center_y, width, height))
                print(f"✅ 添加标注: center=({center_x:.3f}, {center_y:.3f}), size=({width:.3f}, {height:.3f})")
    
    def draw_annotations(self, image: np.ndarray) -> np.ndarray:
        """在图像上绘制标注"""
        img_height, img_width = image.shape[:2]
        
        for i, (center_x, center_y, width, height) in enumerate(self.annotations):
            # 转换为像素坐标
            x1, y1, x2, y2 = self.yolo_to_pixel(center_x, center_y, width, height, img_width, img_height)
            
            # 绘制边界框
            color = (0, 255, 0) if i == len(self.annotations) - 1 else (255, 0, 0)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # 绘制标签
            label = f"watermark {i+1}"
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # 绘制当前正在绘制的框
        if self.drawing and self.start_point and self.end_point:
            cv2.rectangle(image, self.start_point, self.end_point, (0, 255, 255), 2)
        
        return image
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
🎯 水印标注工具使用说明:

鼠标操作:
  - 左键拖拽: 绘制水印边界框
  - 右键: 删除最后一个标注

键盘快捷键:
  - 'n' 或 '→': 下一张图像
  - 'p' 或 '←': 上一张图像
  - 's': 保存当前标注
  - 'd': 删除最后一个标注
  - 'r': 重置当前图像的所有标注
  - 'h': 显示此帮助信息
  - 'q' 或 ESC: 退出程序

标注格式: YOLO 格式 (相对坐标 0-1)
类别: watermark (ID: 0)
        """
        print(help_text)
    
    def run(self):
        """运行标注工具"""
        if not self.image_files:
            print("❌ 没有找到图像文件")
            return
        
        # 设置鼠标回调
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        self.show_help()
        
        while True:
            if self.current_index >= len(self.image_files):
                print("🎉 所有图像已标注完成!")
                break
            
            # 加载当前图像
            image_path = self.image_files[self.current_index]
            self.current_image = cv2.imread(str(image_path))
            
            if self.current_image is None:
                print(f"❌ 无法加载图像: {image_path}")
                self.current_index += 1
                continue
            
            # 加载现有标注
            self.annotations = self.load_annotations(image_path)
            
            print(f"\n📷 当前图像: {image_path.name} ({self.current_index + 1}/{len(self.image_files)})")
            print(f"📊 已有标注: {len(self.annotations)} 个")
            
            while True:
                # 绘制标注
                display_image = self.current_image.copy()
                display_image = self.draw_annotations(display_image)
                
                # 添加状态信息
                status_text = f"图像 {self.current_index + 1}/{len(self.image_files)} | 标注: {len(self.annotations)}"
                cv2.putText(display_image, status_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow(self.window_name, display_image)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # 'q' 或 ESC
                    cv2.destroyAllWindows()
                    return
                elif key == ord('n') or key == 13:  # 'n' 或 Enter
                    # 保存当前标注
                    self.save_annotations(image_path, self.annotations)
                    self.current_index += 1
                    break
                elif key == ord('p'):  # 'p'
                    if self.current_index > 0:
                        # 保存当前标注
                        self.save_annotations(image_path, self.annotations)
                        self.current_index -= 1
                        break
                elif key == ord('s'):  # 's'
                    self.save_annotations(image_path, self.annotations)
                elif key == ord('d') or key == 2:  # 'd' 或 右键
                    if self.annotations:
                        removed = self.annotations.pop()
                        print(f"🗑️  删除标注: {removed}")
                elif key == ord('r'):  # 'r'
                    self.annotations.clear()
                    print("🔄 重置所有标注")
                elif key == ord('h'):  # 'h'
                    self.show_help()
        
        cv2.destroyAllWindows()
        print("✅ 标注完成!")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="简单的水印标注工具")
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
    annotator = SimpleAnnotator(images_dir, labels_dir)
    annotator.run()

if __name__ == "__main__":
    main()
