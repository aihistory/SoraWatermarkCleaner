#!/usr/bin/env python3
"""
测试标注显示功能的脚本
"""

import json
import requests
from pathlib import Path

def test_annotation_api():
    """测试标注 API"""
    print("🧪 测试标注显示功能")
    print("=" * 40)
    
    # 测试服务器是否运行
    try:
        response = requests.get("http://localhost:9090/api/directories", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器正在运行")
        else:
            print("❌ 服务器响应异常")
            return
    except requests.exceptions.RequestException:
        print("❌ 无法连接到服务器")
        print("💡 请先启动服务器: bash datasets/start_web_annotation.sh")
        return
    
    # 测试目录 API
    try:
        response = requests.get("http://localhost:9090/api/directories")
        directories = response.json()
        print(f"📁 发现的图像目录: {len(directories['images'])}")
        print(f"📁 发现的标签目录: {len(directories['labels'])}")
        
        if directories['images']:
            print("图像目录:")
            for img_dir in directories['images']:
                # 显示目录层级
                level = img_dir.count('/')
                indent = "  " * (level + 1)
                print(f"{indent}- {img_dir}")
        if directories['labels']:
            print("标签目录:")
            for label_dir in directories['labels']:
                # 显示目录层级
                level = label_dir.count('/')
                indent = "  " * (level + 1)
                print(f"{indent}- {label_dir}")
                
        # 验证只显示 datasets 目录
        all_dirs = directories['images'] + directories['labels']
        non_datasets_dirs = [d for d in all_dirs if not d.startswith('datasets/')]
        if non_datasets_dirs:
            print(f"⚠️  警告: 发现非 datasets 目录: {non_datasets_dirs}")
        else:
            print("✅ 确认: 只显示 datasets 目录下的子目录")
            
        # 检查多级目录
        multi_level_dirs = [d for d in all_dirs if d.count('/') > 1]
        if multi_level_dirs:
            print(f"📁 发现 {len(multi_level_dirs)} 个多级子目录:")
            for dir_path in multi_level_dirs:
                print(f"  - {dir_path}")
        else:
            print("📁 未发现多级子目录")
            
    except Exception as e:
        print(f"❌ 目录 API 测试失败: {e}")
        return
    
    # 测试图像 API
    try:
        # 设置目录
        setup_data = {
            "images_dir": "datasets/coco8/images/train",
            "labels_dir": "datasets/coco8/labels/train"
        }
        response = requests.post("http://localhost:9090/api/set-directories", 
                               json=setup_data)
        if response.status_code == 200:
            print("✅ 目录设置成功")
        else:
            print("❌ 目录设置失败")
            return
            
        # 获取图像列表
        response = requests.get("http://localhost:9090/api/images")
        if response.status_code == 200:
            images = response.json()
            print(f"📸 找到 {len(images)} 张图像")
            
            if images:
                test_image = images[0]
                print(f"🧪 测试图像: {test_image}")
                
                # 测试图像加载
                response = requests.get(f"http://localhost:9090/api/image/{test_image}")
                if response.status_code == 200:
                    print("✅ 图像加载成功")
                else:
                    print("❌ 图像加载失败")
                
                # 测试标注加载
                response = requests.get(f"http://localhost:9090/api/labels/{test_image}")
                if response.status_code == 200:
                    annotations = response.json()
                    print(f"✅ 标注加载成功，找到 {len(annotations)} 个标注")
                    for i, ann in enumerate(annotations):
                        print(f"  标注 {i}: {ann}")
                else:
                    print("❌ 标注加载失败")
                    
        else:
            print("❌ 图像列表获取失败")
            
    except Exception as e:
        print(f"❌ 图像 API 测试失败: {e}")
        return
    
    print("\n🎯 测试完成！")
    print("💡 如果所有测试都通过，请在浏览器中访问 http://localhost:9090 查看标注")

def check_annotation_files():
    """检查标注文件"""
    print("\n📋 检查标注文件")
    print("=" * 30)
    
    labels_dir = Path("datasets/coco8/labels/train")
    if not labels_dir.exists():
        print("❌ 标签目录不存在")
        return
    
    label_files = list(labels_dir.glob("*.txt"))
    print(f"📁 找到 {len(label_files)} 个标注文件")
    
    if label_files:
        # 检查第一个文件
        first_file = label_files[0]
        print(f"📄 检查文件: {first_file.name}")
        
        with open(first_file, 'r') as f:
            lines = f.readlines()
        
        print(f"📝 文件内容 ({len(lines)} 行):")
        for i, line in enumerate(lines):
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 5:
                    print(f"  行 {i+1}: 类别={parts[0]}, 位置=({parts[1]}, {parts[2]}), 大小=({parts[3]}, {parts[4]})")
                else:
                    print(f"  行 {i+1}: 格式错误 - {line.strip()}")

if __name__ == '__main__':
    check_annotation_files()
    test_annotation_api()
