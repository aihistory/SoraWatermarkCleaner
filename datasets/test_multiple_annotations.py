#!/usr/bin/env python3
"""
测试多标注保存功能
验证修复后的多标注保存是否正常工作
"""

import json
import requests
import time
from pathlib import Path

def test_multiple_annotations():
    """测试多标注保存功能"""
    print("🧪 测试多标注保存功能")
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
    
    # 设置目录
    try:
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
    except Exception as e:
        print(f"❌ 目录设置失败: {e}")
        return
    
    # 获取图像列表
    try:
        response = requests.get("http://localhost:9090/api/images")
        if response.status_code == 200:
            images = response.json()
            print(f"📸 找到 {len(images)} 张图像")
            
            if images:
                test_image = images[0]
                print(f"🧪 测试图像: {test_image}")
                
                # 创建多个测试标注
                test_annotations = [
                    {
                        "x": 0.1,
                        "y": 0.1,
                        "width": 0.2,
                        "height": 0.15,
                        "class": "watermark"
                    },
                    {
                        "x": 0.6,
                        "y": 0.3,
                        "width": 0.25,
                        "height": 0.2,
                        "class": "logo"
                    },
                    {
                        "x": 0.2,
                        "y": 0.7,
                        "width": 0.3,
                        "height": 0.1,
                        "class": "text"
                    },
                    {
                        "x": 0.5,
                        "y": 0.5,
                        "width": 0.15,
                        "height": 0.15,
                        "class": "signature"
                    }
                ]
                
                print(f"📝 创建 {len(test_annotations)} 个测试标注")
                
                # 保存标注
                response = requests.post(f"http://localhost:9090/api/save/{test_image}", 
                                       json=test_annotations)
                
                if response.status_code == 200:
                    print("✅ 多标注保存成功")
                    
                    # 验证保存结果
                    response = requests.get(f"http://localhost:9090/api/labels/{test_image}")
                    if response.status_code == 200:
                        saved_annotations = response.json()
                        print(f"✅ 验证成功: 保存了 {len(saved_annotations)} 个标注")
                        
                        # 显示保存的标注详情
                        for i, annotation in enumerate(saved_annotations):
                            print(f"  标注 {i+1}: {annotation['class']} - "
                                  f"位置({annotation['x']:.3f}, {annotation['y']:.3f}) "
                                  f"大小({annotation['width']:.3f}, {annotation['height']:.3f})")
                        
                        if len(saved_annotations) == len(test_annotations):
                            print("🎉 多标注保存功能正常！")
                        else:
                            print(f"⚠️  标注数量不匹配: 期望 {len(test_annotations)}, 实际 {len(saved_annotations)}")
                    else:
                        print("❌ 验证保存结果失败")
                else:
                    print("❌ 多标注保存失败")
                    
        else:
            print("❌ 图像列表获取失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return

def check_saved_files():
    """检查保存的标注文件"""
    print("\n📁 检查保存的标注文件")
    print("=" * 30)
    
    labels_dir = Path("datasets/coco8/labels/train")
    if not labels_dir.exists():
        print("❌ 标签目录不存在")
        return
    
    label_files = list(labels_dir.glob("*.txt"))
    print(f"📁 找到 {len(label_files)} 个标注文件")
    
    for label_file in label_files:
        try:
            with open(label_file, 'r') as f:
                lines = f.readlines()
            
            valid_lines = [line.strip() for line in lines if line.strip()]
            if valid_lines:
                print(f"📄 {label_file.name}: {len(valid_lines)} 个标注")
                
                # 显示前几个标注的详情
                for i, line in enumerate(valid_lines[:3]):
                    parts = line.split()
                    if len(parts) >= 5:
                        print(f"   标注 {i+1}: 类别={parts[0]}, "
                              f"位置=({parts[1]}, {parts[2]}), "
                              f"大小=({parts[3]}, {parts[4]})")
                
                if len(valid_lines) > 3:
                    print(f"   ... 还有 {len(valid_lines) - 3} 个标注")
                    
        except Exception as e:
            print(f"❌ 读取文件 {label_file.name} 失败: {e}")

def main():
    print("🎯 多标注保存功能测试")
    print("=" * 50)
    
    # 测试多标注保存
    test_multiple_annotations()
    
    # 检查保存的文件
    check_saved_files()
    
    print("\n🎉 测试完成！")
    print("\n📋 修复内容:")
    print("✅ 1. 修复了标注数组被意外清空的问题")
    print("✅ 2. 改进了标注加载逻辑，避免覆盖新添加的标注")
    print("✅ 3. 添加了调试信息，显示保存的标注数量")
    print("✅ 4. 优化了图像切换时的标注处理")
    
    print("\n💡 使用建议:")
    print("1. 在同一图像上创建多个标注框")
    print("2. 点击'保存标注'按钮")
    print("3. 检查控制台日志确认标注数量")
    print("4. 验证标注文件是否正确保存")

if __name__ == '__main__':
    main()
