#!/usr/bin/env python3
"""
测试高精度 Web 标注工具的修复
"""

import json
import requests
import time
from pathlib import Path

def test_enhanced_annotation_flow():
    """测试高精度版本的标注流程"""
    print("🧪 测试高精度 Web 标注工具修复")
    print("=" * 50)
    
    # 测试服务器
    try:
        response = requests.get("http://localhost:9092/api/directories", timeout=5)
        if response.status_code == 200:
            print("✅ 高精度服务器正在运行 (端口 9092)")
        else:
            print("❌ 高精度服务器响应异常")
            return
    except requests.exceptions.RequestException:
        print("❌ 无法连接到高精度服务器")
        print("💡 请先启动高精度服务器: python3 datasets/web_annotation_tool_enhanced.py --port 9092")
        return
    
    # 设置目录
    try:
        setup_data = {
            "images_dir": "datasets/coco8/images/train",
            "labels_dir": "datasets/coco8/labels/train"
        }
        response = requests.post("http://localhost:9092/api/set-directories", 
                               json=setup_data)
        if response.status_code == 200:
            print("✅ 目录设置成功")
        else:
            print("❌ 目录设置失败")
            return
    except Exception as e:
        print(f"❌ 目录设置失败: {e}")
        return
    
    # 获取图像
    try:
        response = requests.get("http://localhost:9092/api/images")
        if response.status_code == 200:
            images = response.json()
            if images:
                test_image = images[0]
                print(f"🧪 测试图像: {test_image}")
                
                # 测试多个标注的保存
                test_annotations = [
                    {"x": 0.1, "y": 0.1, "width": 0.2, "height": 0.15, "class": "watermark"},
                    {"x": 0.6, "y": 0.3, "width": 0.25, "height": 0.2, "class": "logo"},
                    {"x": 0.2, "y": 0.7, "width": 0.3, "height": 0.1, "class": "text"}
                ]
                
                print(f"📝 准备保存 {len(test_annotations)} 个标注到高精度版本")
                
                # 保存标注
                response = requests.post(f"http://localhost:9092/api/save/{test_image}", 
                                       json=test_annotations)
                
                print(f"📡 保存响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 保存成功: {result}")
                    
                    # 验证保存结果
                    response = requests.get(f"http://localhost:9092/api/labels/{test_image}")
                    if response.status_code == 200:
                        saved_annotations = response.json()
                        print(f"📥 验证结果: 保存了 {len(saved_annotations)} 个标注")
                        
                        for i, annotation in enumerate(saved_annotations):
                            print(f"  标注 {i+1}: {annotation}")
                        
                        if len(saved_annotations) == len(test_annotations):
                            print("🎉 高精度版本多标注保存功能正常！")
                        else:
                            print(f"⚠️  标注数量不匹配: 期望 {len(test_annotations)}, 实际 {len(saved_annotations)}")
                    else:
                        print("❌ 验证保存结果失败")
                else:
                    print(f"❌ 保存失败: {response.status_code}")
                    print(f"响应内容: {response.text}")
                    
            else:
                print("❌ 没有找到图像")
        else:
            print("❌ 获取图像列表失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def check_enhanced_backend_logic():
    """检查高精度版本的后端保存逻辑"""
    print("\n🔍 检查高精度版本后端保存逻辑")
    print("=" * 40)
    
    # 检查保存的标注文件
    labels_dir = Path("datasets/coco8/labels/train")
    if labels_dir.exists():
        label_files = list(labels_dir.glob("*.txt"))
        print(f"📁 找到 {len(label_files)} 个标注文件")
        
        for label_file in label_files:
            try:
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                valid_lines = [line.strip() for line in lines if line.strip()]
                if valid_lines:
                    print(f"📄 {label_file.name}: {len(valid_lines)} 个标注")
                    
                    # 显示标注详情
                    for i, line in enumerate(valid_lines):
                        parts = line.split()
                        if len(parts) >= 5:
                            print(f"   标注 {i+1}: 类别={parts[0]}, "
                                  f"位置=({parts[1]}, {parts[2]}), "
                                  f"大小=({parts[3]}, {parts[4]})")
                            
            except Exception as e:
                print(f"❌ 读取文件 {label_file.name} 失败: {e}")

def main():
    print("🎯 高精度 Web 标注工具修复测试")
    print("=" * 60)
    
    # 测试标注流程
    test_enhanced_annotation_flow()
    
    # 检查后端逻辑
    check_enhanced_backend_logic()
    
    print("\n🎉 高精度版本测试完成！")
    print("\n💡 使用建议:")
    print("1. 访问 http://localhost:9092 使用高精度标注工具")
    print("2. 打开浏览器开发者工具查看控制台日志")
    print("3. 测试多标注创建和保存功能")
    print("4. 验证标注精度和保存结果")

if __name__ == '__main__':
    main()
