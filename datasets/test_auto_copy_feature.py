#!/usr/bin/env python3
"""
测试自动复制标注功能
"""

import json
import requests
import time
from pathlib import Path

def test_auto_copy_feature():
    """测试自动复制标注功能"""
    print("🧪 测试自动复制标注功能")
    print("=" * 50)
    
    # 测试标准版本 (端口 9090)
    print("\n📋 测试标准版本 (端口 9090)")
    test_version("http://localhost:9090", "标准版本")
    
    # 测试高精度版本 (端口 9092)
    print("\n📋 测试高精度版本 (端口 9092)")
    test_version("http://localhost:9092", "高精度版本")

def test_version(base_url, version_name):
    """测试指定版本的自动复制功能"""
    try:
        # 检查服务器是否运行
        response = requests.get(f"{base_url}/api/directories", timeout=5)
        if response.status_code != 200:
            print(f"❌ {version_name} 服务器未运行")
            return
        print(f"✅ {version_name} 服务器正在运行")
        
        # 设置目录
        setup_data = {
            "images_dir": "datasets/coco8/images/train",
            "labels_dir": "datasets/coco8/labels/train"
        }
        response = requests.post(f"{base_url}/api/set-directories", json=setup_data)
        if response.status_code == 200:
            print(f"✅ {version_name} 目录设置成功")
        else:
            print(f"❌ {version_name} 目录设置失败")
            return
        
        # 获取图像列表
        response = requests.get(f"{base_url}/api/images")
        if response.status_code == 200:
            images = response.json()
            if len(images) >= 2:
                print(f"✅ {version_name} 找到 {len(images)} 个图像")
                
                # 测试自动复制功能
                test_auto_copy_workflow(base_url, version_name, images[:2])
            else:
                print(f"❌ {version_name} 图像数量不足，需要至少2个图像")
        else:
            print(f"❌ {version_name} 获取图像列表失败")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {version_name} 连接失败: {e}")

def test_auto_copy_workflow(base_url, version_name, images):
    """测试自动复制工作流程"""
    print(f"\n🔄 测试 {version_name} 自动复制工作流程")
    print("-" * 40)
    
    # 第一张图像：创建测试标注
    first_image = images[0]
    test_annotations = [
        {"x": 0.1, "y": 0.1, "width": 0.2, "height": 0.15, "class": "watermark"},
        {"x": 0.6, "y": 0.3, "width": 0.25, "height": 0.2, "class": "logo"},
        {"x": 0.2, "y": 0.7, "width": 0.3, "height": 0.1, "class": "text"}
    ]
    
    print(f"📝 在第一张图像 {first_image} 上创建 {len(test_annotations)} 个标注")
    
    # 保存第一张图像的标注
    response = requests.post(f"{base_url}/api/save/{first_image}", json=test_annotations)
    if response.status_code == 200:
        print(f"✅ 第一张图像标注保存成功")
    else:
        print(f"❌ 第一张图像标注保存失败")
        return
    
    # 验证第一张图像的标注
    response = requests.get(f"{base_url}/api/labels/{first_image}")
    if response.status_code == 200:
        saved_annotations = response.json()
        print(f"✅ 第一张图像验证: 保存了 {len(saved_annotations)} 个标注")
    else:
        print(f"❌ 第一张图像验证失败")
        return
    
    # 第二张图像：测试自动复制
    second_image = images[1]
    print(f"\n🔄 切换到第二张图像 {second_image}")
    
    # 检查第二张图像的初始标注
    response = requests.get(f"{base_url}/api/labels/{second_image}")
    if response.status_code == 200:
        initial_annotations = response.json()
        print(f"📋 第二张图像初始标注数量: {len(initial_annotations)}")
    else:
        initial_annotations = []
        print(f"📋 第二张图像初始标注数量: 0 (新图像)")
    
    print(f"\n💡 手动测试步骤:")
    print(f"1. 访问 {base_url}")
    print(f"2. 在第一张图像上创建标注")
    print(f"3. 启用'自动复制标注'开关")
    print(f"4. 选择复制模式 (所有标注/仅水印/仅Logo/仅文本)")
    print(f"5. 点击'下一张'按钮")
    print(f"6. 观察标注是否自动复制到第二张图像")
    print(f"7. 检查控制台日志确认复制过程")
    
    print(f"\n🎯 预期结果:")
    print(f"- 启用自动复制后，切换到下一张图像时")
    print(f"- 上一张图像的标注应该自动复制到当前图像")
    print(f"- 复制的标注数量取决于选择的复制模式")
    print(f"- 控制台应该显示详细的复制日志")

def create_test_instructions():
    """创建测试说明文档"""
    instructions = """
# 自动复制标注功能测试说明

## 🎯 功能描述

自动复制标注功能允许用户将上一张图像的标注信息自动复制到下一张图像中，特别适用于批量标注相似内容。

## 🛠️ 功能特性

### 1. 自动复制开关
- 位置：控制面板中的"🔄 自动复制标注"开关
- 功能：启用/禁用自动复制功能
- 状态：绿色表示启用，灰色表示禁用

### 2. 复制模式选择
- **复制所有标注**：复制上一张图像的所有标注
- **仅复制水印标注**：只复制类别为"watermark"的标注
- **仅复制Logo标注**：只复制类别为"logo"的标注
- **仅复制文本标注**：只复制类别为"text"的标注

### 3. 自动触发
- 当用户点击"➡️ 下一张"按钮时自动触发
- 只有在启用自动复制开关时才会执行
- 复制过程有详细的控制台日志

## 🧪 测试步骤

### 标准版本测试 (端口 9090)
1. 访问 http://localhost:9090
2. 设置图像和标注目录
3. 加载图像列表
4. 在第一张图像上创建多个不同类型的标注
5. 启用"自动复制标注"开关
6. 选择复制模式（建议先测试"复制所有标注"）
7. 点击"➡️ 下一张"按钮
8. 观察第二张图像是否自动出现复制的标注
9. 打开浏览器开发者工具查看控制台日志

### 高精度版本测试 (端口 9092)
1. 访问 http://localhost:9092
2. 重复上述步骤
3. 验证高精度版本的复制功能

## 📋 测试用例

### 用例1：复制所有标注
- 第一张图像：创建3个标注（watermark, logo, text）
- 复制模式：复制所有标注
- 预期结果：第二张图像出现3个标注

### 用例2：选择性复制
- 第一张图像：创建3个标注（watermark, logo, text）
- 复制模式：仅复制水印标注
- 预期结果：第二张图像只出现1个watermark标注

### 用例3：无标注复制
- 第一张图像：无标注
- 复制模式：任意
- 预期结果：第二张图像无复制标注

## 🔍 调试信息

### 控制台日志
启用自动复制功能后，控制台会显示以下日志：

```
🔄 自动复制功能: 已启用
💾 保存当前标注用于复制: 3 个标注
📋 复制 3 个标注到当前图像 (模式: all)
📋 复制的标注: [{...}, {...}, {...}]
已复制 3 个标注到当前图像
```

### 错误处理
- 如果复制模式没有匹配的标注，会显示"没有符合复制条件的标注"
- 如果自动复制功能未启用，不会执行复制操作
- 所有操作都有详细的日志记录

## ✅ 验证要点

1. **功能开关**：开关状态正确切换
2. **复制模式**：不同模式正确过滤标注
3. **自动触发**：点击"下一张"时正确触发
4. **标注复制**：标注正确复制到新图像
5. **界面更新**：标注框和列表正确更新
6. **日志记录**：控制台显示详细操作日志

## 🚨 注意事项

1. 复制的标注会添加到现有标注中，不会覆盖
2. 复制的是标注的位置和大小信息，不包含图像内容
3. 建议在相似内容的图像上使用此功能
4. 可以通过"清除当前"按钮清除不需要的复制标注
"""
    
    with open("datasets/AUTO_COPY_TEST_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📄 已创建测试说明文档: datasets/AUTO_COPY_TEST_INSTRUCTIONS.md")

def main():
    print("🎯 自动复制标注功能测试")
    print("=" * 60)
    
    # 测试自动复制功能
    test_auto_copy_feature()
    
    # 创建测试说明
    create_test_instructions()
    
    print("\n🎉 测试准备完成！")
    print("\n💡 使用建议:")
    print("1. 确保两个版本的服务器都在运行")
    print("2. 按照测试说明进行手动测试")
    print("3. 观察控制台日志验证功能")
    print("4. 测试不同的复制模式")

if __name__ == '__main__':
    main()
