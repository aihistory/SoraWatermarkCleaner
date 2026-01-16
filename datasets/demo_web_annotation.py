#!/usr/bin/env python3
"""
增强版 Web 标注工具演示脚本
展示新功能和特性
"""

import os
import json
from pathlib import Path

def create_demo_data():
    """创建演示数据"""
    print("🎬 创建演示数据...")
    
    # 创建演示目录结构
    demo_dirs = [
        "datasets/demo/images/train",
        "datasets/demo/labels/train",
        "datasets/demo/images/val",
        "datasets/demo/labels/val"
    ]
    
    for dir_path in demo_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # 创建一些示例标注文件
    sample_annotations = [
        "0 0.1 0.1 0.2 0.2",
        "0 0.6 0.3 0.3 0.4",
        "0 0.2 0.7 0.25 0.2"
    ]
    
    # 为每个演示图像创建对应的标注文件
    for i in range(5):
        image_name = f"demo_image_{i:03d}.jpg"
        label_name = f"demo_image_{i:03d}.txt"
        
        # 创建标注文件
        label_path = Path(f"datasets/demo/labels/train/{label_name}")
        with open(label_path, 'w') as f:
            for annotation in sample_annotations:
                f.write(annotation + "\n")
        
        print(f"  ✅ 创建标注文件: {label_name}")
    
    print("🎉 演示数据创建完成！")
    print("📁 演示目录: datasets/demo/")
    print("🖼️ 图像目录: datasets/demo/images/train/")
    print("🏷️ 标签目录: datasets/demo/labels/train/")

def show_features():
    """展示增强功能"""
    print("\n✨ 增强版 Web 标注工具功能展示")
    print("=" * 50)
    
    features = [
        ("📁 智能目录管理", [
            "自动扫描项目目录",
            "发现图像和标签目录",
            "下拉菜单选择目录",
            "运行时切换数据集"
        ]),
        ("🎯 可视化标注界面", [
            "拖拽创建边界框",
            "实时预览效果",
            "标注框高亮显示",
            "选中状态管理"
        ]),
        ("🗑️ 标注管理功能", [
            "编辑标注类别",
            "删除单个标注",
            "批量删除标注",
            "清除所有标注"
        ]),
        ("📊 统计信息面板", [
            "总图像数统计",
            "已标注图像数",
            "总标注框数量",
            "当前进度显示"
        ]),
        ("📤 数据导出功能", [
            "JSON 格式导出",
            "批量数据下载",
            "YOLO 格式兼容",
            "完整数据集备份"
        ]),
        ("⌨️ 键盘快捷键", [
            "W - 创建边界框",
            "A - 上一张图像",
            "D - 下一张图像",
            "Del - 删除标注"
        ]),
        ("🎨 界面特性", [
            "响应式设计",
            "现代 UI 风格",
            "实时操作反馈",
            "友好错误提示"
        ])
    ]
    
    for category, items in features:
        print(f"\n{category}")
        print("-" * len(category))
        for item in items:
            print(f"  • {item}")

def show_usage():
    """显示使用说明"""
    print("\n🚀 使用方法")
    print("=" * 30)
    
    print("\n1. 启动工具:")
    print("   bash datasets/start_web_annotation.sh")
    print("   或")
    print("   python3 datasets/web_annotation_tool.py")
    
    print("\n2. 访问界面:")
    print("   在浏览器中打开: http://localhost:8080")
    
    print("\n3. 开始标注:")
    print("   • 选择图像和标签目录")
    print("   • 点击'加载图像'")
    print("   • 在图像上拖拽创建边界框")
    print("   • 使用界面按钮管理标注")
    
    print("\n4. 保存和导出:")
    print("   • 点击'保存标注'保存当前图像")
    print("   • 点击'导出数据'下载完整数据集")

def main():
    print("🌐 增强版 Web 标注工具演示")
    print("=" * 40)
    
    # 创建演示数据
    create_demo_data()
    
    # 展示功能特性
    show_features()
    
    # 显示使用说明
    show_usage()
    
    print("\n🎯 快速开始:")
    print("1. 运行: bash datasets/start_web_annotation.sh")
    print("2. 访问: http://localhost:8080")
    print("3. 选择演示目录: datasets/demo/images/train")
    print("4. 开始体验增强功能！")
    
    print("\n💡 提示:")
    print("- 演示数据已创建在 datasets/demo/ 目录")
    print("- 支持多种图像格式: JPG, PNG, BMP, TIFF, WebP")
    print("- 标注格式兼容 YOLO 训练要求")
    print("- 支持跨平台使用（Windows, macOS, Linux）")

if __name__ == '__main__':
    main()
