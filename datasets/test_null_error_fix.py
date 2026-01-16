#!/usr/bin/env python3
"""
测试前端null错误修复
"""

import requests
import time
from pathlib import Path

def test_null_error_fix():
    """测试前端null错误修复"""
    print("🧪 测试前端null错误修复")
    print("=" * 40)
    
    # 测试标准版本
    print("\n📋 测试标准版本 (端口 9090)")
    test_version("http://localhost:9090", "标准版本")
    
    # 测试高精度版本
    print("\n📋 测试高精度版本 (端口 9092)")
    test_version("http://localhost:9092", "高精度版本")

def test_version(base_url, version_name):
    """测试指定版本的null错误修复"""
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
            if images:
                print(f"✅ {version_name} 找到 {len(images)} 个图像")
                
                # 测试图像加载
                test_image_loading(base_url, version_name, images[0])
            else:
                print(f"❌ {version_name} 没有找到图像")
        else:
            print(f"❌ {version_name} 获取图像列表失败")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {version_name} 连接失败: {e}")

def test_image_loading(base_url, version_name, image_name):
    """测试图像加载功能"""
    print(f"\n🖼️ 测试 {version_name} 图像加载")
    print("-" * 30)
    
    # 测试图像API
    try:
        response = requests.get(f"{base_url}/api/image/{image_name}")
        if response.status_code == 200:
            print(f"✅ 图像API响应正常: {image_name}")
        else:
            print(f"❌ 图像API响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 图像API请求失败: {e}")
    
    # 测试统计API
    try:
        response = requests.get(f"{base_url}/api/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 统计API响应正常: {stats}")
        else:
            print(f"❌ 统计API响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 统计API请求失败: {e}")
    
    print(f"\n💡 手动测试步骤:")
    print(f"1. 访问 {base_url}")
    print(f"2. 打开浏览器开发者工具 (F12)")
    print(f"3. 查看 Console 标签页")
    print(f"4. 加载图像并观察是否有null错误")
    print(f"5. 检查是否出现 'current-image 元素未找到' 或 'current-index 元素未找到' 警告")

def create_debug_instructions():
    """创建调试说明"""
    instructions = """
# 前端null错误修复说明

## 🐛 问题描述

前端出现错误："Cannot set properties of null (setting 'textContent')"

这个错误通常发生在JavaScript试图设置一个不存在的DOM元素的textContent属性时。

## 🔍 问题原因

1. **DOM元素未找到**：JavaScript试图访问的DOM元素可能还没有被创建
2. **时序问题**：在DOM完全加载之前就执行了JavaScript代码
3. **元素被意外删除**：某些操作可能意外删除了DOM元素

## 🛠️ 修复方案

### 1. 添加空值检查

**修复前**：
```javascript
document.getElementById('current-image').textContent = imageName;
```

**修复后**：
```javascript
const currentImageElement = document.getElementById('current-image');
if (currentImageElement) {
    currentImageElement.textContent = imageName;
} else {
    console.warn('current-image 元素未找到');
}
```

### 2. 修复的函数

- `loadCurrentImage()` - 加载当前图像时设置显示信息
- `updateStats()` - 更新统计信息时设置数值

### 3. 修复的元素

- `current-image` - 显示当前图像名称
- `current-index` - 显示当前图像索引
- `total-images` - 显示总图像数
- `annotated-images` - 显示已标注图像数
- `total-annotations` - 显示总标注数

## 🧪 测试验证

### 1. 自动测试
运行测试脚本：
```bash
python3 datasets/test_null_error_fix.py
```

### 2. 手动测试
1. 访问标注工具
2. 打开浏览器开发者工具
3. 查看Console标签页
4. 加载图像并观察错误信息
5. 确认不再出现null错误

### 3. 预期结果
- ✅ 不再出现 "Cannot set properties of null" 错误
- ✅ 如果元素未找到，会显示警告信息而不是错误
- ✅ 图像加载和统计更新正常工作

## 🔍 调试信息

### 正常情况
- 图像正常加载
- 统计信息正常更新
- 控制台无错误信息

### 异常情况
- 如果元素未找到，会显示警告：
  ```
  current-image 元素未找到
  current-index 元素未找到
  ```
- 这些是警告而不是错误，不会影响功能

## 📋 检查清单

- [ ] 标准版本 (端口 9090) 无null错误
- [ ] 高精度版本 (端口 9092) 无null错误
- [ ] 图像加载正常
- [ ] 统计信息更新正常
- [ ] 控制台无错误信息
- [ ] 所有功能正常工作

## 🚨 注意事项

1. 如果仍然出现null错误，可能是其他地方的代码问题
2. 警告信息是正常的，表示某些元素可能暂时不可用
3. 修复后的代码更加健壮，能够处理DOM元素不存在的情况
"""
    
    with open("datasets/NULL_ERROR_FIX_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📄 已创建调试说明文档: datasets/NULL_ERROR_FIX_INSTRUCTIONS.md")

def main():
    print("🎯 前端null错误修复测试")
    print("=" * 50)
    
    # 测试修复效果
    test_null_error_fix()
    
    # 创建调试说明
    create_debug_instructions()
    
    print("\n🎉 测试完成！")
    print("\n💡 使用建议:")
    print("1. 确保两个版本的服务器都在运行")
    print("2. 访问标注工具并打开开发者工具")
    print("3. 观察控制台是否还有null错误")
    print("4. 如果仍有问题，请查看详细的调试说明")

if __name__ == '__main__':
    main()
