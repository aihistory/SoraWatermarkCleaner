#!/usr/bin/env python3
"""
自动标注工具
基于图像分析自动检测可能的水印位置
"""

import sys
from pathlib import Path
import cv2
import numpy as np

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class AutoAnnotator:
    """自动标注工具"""
    
    def __init__(self, images_dir: Path, labels_dir: Path):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.labels_dir.mkdir(exist_ok=True, parents=True)
        
        # 获取所有图像文件
        self.image_files = sorted(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
        
        print(f"📁 图像目录: {images_dir}")
        print(f"📁 标签目录: {labels_dir}")
        print(f"📊 总共 {len(self.image_files)} 张图像")
    
    def detect_watermark_candidates(self, image):
        """检测可能的水印位置"""
        height, width = image.shape[:2]
        candidates = []
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. 检测边缘
        edges = cv2.Canny(gray, 50, 150)
        
        # 2. 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 3. 分析轮廓
        for contour in contours:
            # 计算边界框
            x, y, w, h = cv2.boundingRect(contour)
            
            # 过滤条件
            if (w > width * 0.05 and h > height * 0.02 and  # 最小尺寸
                w < width * 0.3 and h < height * 0.2 and    # 最大尺寸
                w / h > 0.5 and w / h < 5):                 # 宽高比
            
                # 转换为YOLO格式
                center_x = (x + w / 2) / width
                center_y = (y + h / 2) / height
                bbox_width = w / width
                bbox_height = h / height
                
                # 计算置信度（基于位置和尺寸）
                confidence = self.calculate_confidence(center_x, center_y, bbox_width, bbox_height)
                
                candidates.append({
                    'center_x': center_x,
                    'center_y': center_y,
                    'width': bbox_width,
                    'height': bbox_height,
                    'confidence': confidence,
                    'pixel_bbox': (x, y, x + w, y + h)
                })
        
        # 按置信度排序
        candidates.sort(key=lambda x: x['confidence'], reverse=True)
        
        return candidates[:5]  # 返回前5个候选
    
    def calculate_confidence(self, center_x, center_y, width, height):
        """计算水印置信度"""
        confidence = 0.0
        
        # 位置权重：水印通常在角落或底部
        if center_y > 0.7:  # 底部区域
            confidence += 0.3
        if center_x < 0.2 or center_x > 0.8:  # 左右边缘
            confidence += 0.2
        if center_y < 0.2:  # 顶部区域
            confidence += 0.1
        
        # 尺寸权重：水印通常不会太大
        if 0.05 < width < 0.2 and 0.02 < height < 0.1:
            confidence += 0.3
        
        # 宽高比权重：水印通常是横向的
        aspect_ratio = width / height
        if 1.5 < aspect_ratio < 4:
            confidence += 0.2
        
        return confidence
    
    def create_template_annotations(self, image):
        """创建模板标注"""
        height, width = image.shape[:2]
        templates = []
        
        # 常见水印位置模板
        templates.append({
            'name': '右下角水印',
            'center_x': 0.85,
            'center_y': 0.9,
            'width': 0.15,
            'height': 0.1,
            'confidence': 0.8
        })
        
        templates.append({
            'name': '左下角水印',
            'center_x': 0.15,
            'center_y': 0.9,
            'width': 0.15,
            'height': 0.1,
            'confidence': 0.7
        })
        
        templates.append({
            'name': '右上角水印',
            'center_x': 0.85,
            'center_y': 0.1,
            'width': 0.15,
            'height': 0.1,
            'confidence': 0.6
        })
        
        templates.append({
            'name': '底部中央水印',
            'center_x': 0.5,
            'center_y': 0.9,
            'width': 0.2,
            'height': 0.08,
            'confidence': 0.5
        })
        
        return templates
    
    def auto_annotate_image(self, image_path: Path, method='template'):
        """自动标注单张图像"""
        # 读取图像
        image = cv2.imread(str(image_path))
        if image is None:
            return []
        
        if method == 'detection':
            # 基于检测的方法
            candidates = self.detect_watermark_candidates(image)
            annotations = []
            
            for candidate in candidates:
                if candidate['confidence'] > 0.3:  # 置信度阈值
                    annotations.append((
                        0,  # class_id
                        candidate['center_x'],
                        candidate['center_y'],
                        candidate['width'],
                        candidate['height']
                    ))
            
            return annotations
        
        elif method == 'template':
            # 基于模板的方法
            templates = self.create_template_annotations(image)
            annotations = []
            
            # 选择置信度最高的模板
            best_template = max(templates, key=lambda x: x['confidence'])
            annotations.append((
                0,  # class_id
                best_template['center_x'],
                best_template['center_y'],
                best_template['width'],
                best_template['height']
            ))
            
            return annotations
        
        return []
    
    def save_annotations(self, image_path: Path, annotations):
        """保存标注"""
        label_path = self.labels_dir / f"{image_path.stem}.txt"
        
        try:
            with open(label_path, 'w') as f:
                for class_id, center_x, center_y, width, height in annotations:
                    f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
            return True
        except Exception as e:
            print(f"❌ 保存标注失败 {label_path}: {e}")
            return False
    
    def run_auto_annotation(self, method='template', overwrite=False):
        """运行自动标注"""
        print(f"🤖 开始自动标注 (方法: {method})")
        
        if method not in ['template', 'detection']:
            print("❌ 无效的方法，请选择 'template' 或 'detection'")
            return
        
        success_count = 0
        skip_count = 0
        
        for i, image_path in enumerate(self.image_files):
            label_path = self.labels_dir / f"{image_path.stem}.txt"
            
            # 检查是否已存在标注
            if label_path.exists() and not overwrite:
                skip_count += 1
                continue
            
            # 自动标注
            annotations = self.auto_annotate_image(image_path, method)
            
            if annotations:
                if self.save_annotations(image_path, annotations):
                    success_count += 1
                    print(f"✅ {image_path.name}: {len(annotations)} 个标注")
                else:
                    print(f"❌ {image_path.name}: 保存失败")
            else:
                print(f"⚠️  {image_path.name}: 未检测到水印")
            
            # 显示进度
            if (i + 1) % 50 == 0:
                print(f"📊 进度: {i + 1}/{len(self.image_files)}")
        
        print(f"\n🎉 自动标注完成!")
        print(f"✅ 成功标注: {success_count} 张图像")
        print(f"⏭️  跳过: {skip_count} 张图像")
        print(f"📊 总计: {len(self.image_files)} 张图像")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自动水印标注工具")
    parser.add_argument("--images", type=str, default="datasets/coco8/images/train",
                       help="图像目录路径")
    parser.add_argument("--labels", type=str, default="datasets/coco8/labels/train",
                       help="标签目录路径")
    parser.add_argument("--method", type=str, default="template", 
                       choices=['template', 'detection'],
                       help="标注方法: template(模板) 或 detection(检测)")
    parser.add_argument("--overwrite", action="store_true",
                       help="覆盖现有标注文件")
    
    args = parser.parse_args()
    
    images_dir = Path(args.images)
    labels_dir = Path(args.labels)
    
    if not images_dir.exists():
        print(f"❌ 图像目录不存在: {images_dir}")
        return
    
    # 创建自动标注工具并运行
    annotator = AutoAnnotator(images_dir, labels_dir)
    annotator.run_auto_annotation(args.method, args.overwrite)

if __name__ == "__main__":
    main()
