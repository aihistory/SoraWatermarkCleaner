#!/usr/bin/env python3
"""
测试页面位置保持功能
"""

import requests
import time
from pathlib import Path

def test_page_position_keep():
    """测试页面位置保持功能"""
    print("🧪 测试页面位置保持功能")
    print("=" * 50)
    
    # 测试标准版本
    print("\n📋 测试标准版本 (端口 9090)")
    test_version("http://localhost:9090", "标准版本")
    
    # 测试高精度版本
    print("\n📋 测试高精度版本 (端口 9092)")
    test_version("http://localhost:9092", "高精度版本")

def test_version(base_url, version_name):
    """测试指定版本的页面位置保持功能"""
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
                
                # 测试页面位置保持功能
                test_page_position_keep_features(base_url, version_name)
            else:
                print(f"❌ {version_name} 没有找到图像")
        else:
            print(f"❌ {version_name} 获取图像列表失败")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {version_name} 连接失败: {e}")

def test_page_position_keep_features(base_url, version_name):
    """测试页面位置保持功能"""
    print(f"\n🎯 测试 {version_name} 页面位置保持功能")
    print("-" * 40)
    
    print(f"💡 手动测试步骤:")
    print(f"1. 访问 {base_url}")
    print(f"2. 滚动页面到任意位置（比如页面中间或底部）")
    print(f"3. 测试以下按钮的页面位置保持功能:")
    print(f"   📋 加载图像按钮:")
    print(f"      - 点击后页面应该保持在原来的位置")
    print(f"      - 不应该自动滚动到顶部")
    print(f"   ⬅️ 上一张按钮:")
    print(f"      - 点击后页面应该保持在原来的位置")
    print(f"      - 不应该自动滚动到顶部")
    print(f"   ➡️ 下一张按钮:")
    print(f"      - 点击后页面应该保持在原来的位置")
    print(f"      - 不应该自动滚动到顶部")
    print(f"   💾 保存标注按钮:")
    print(f"      - 点击后页面应该保持在原来的位置")
    print(f"      - 不应该自动滚动到顶部")
    print(f"4. 验证功能效果:")
    print(f"   - 每次点击按钮后页面位置保持不变")
    print(f"   - 没有意外的页面滚动")
    print(f"   - 用户可以继续在当前位置工作")
    print(f"   - 操作体验自然流畅")

def create_page_position_keep_instructions():
    """创建页面位置保持功能说明"""
    instructions = """
# 页面位置保持功能说明

## 🎯 功能描述

移除标注工具主要操作按钮的自动滚动功能，确保在点击这些按钮时页面保持在原来的位置，提供更自然的用户体验。

## 🔧 实现方案

### 1. 移除自动滚动代码

从每个关键函数中移除：
```javascript
// 固定页面位置
window.scrollTo(0, 0);
```

### 2. 涉及的函数

#### 标准版本和高精度版本都包含以下函数：

1. **loadImages()** - 加载图像按钮
   - 功能：加载图像列表
   - 页面位置：保持不变

2. **prevImage()** - 上一张按钮
   - 功能：切换到上一张图像
   - 页面位置：保持不变

3. **nextImage()** - 下一张按钮
   - 功能：切换到下一张图像
   - 页面位置：保持不变

4. **saveAnnotations()** - 保存标注按钮
   - 功能：保存当前图像的标注
   - 页面位置：保持不变

## 🎨 用户体验改进

### 修复前的问题
- ❌ 点击按钮后页面自动滚动到顶部
- ❌ 用户需要重新滚动到工作位置
- ❌ 操作体验不够自然
- ❌ 打断了用户的工作流程

### 修复后的效果
- ✅ 点击按钮后页面保持在原位置
- ✅ 用户无需重新调整页面位置
- ✅ 操作体验自然流畅
- ✅ 保持用户的工作连续性

## 🧪 测试验证

### 1. 功能测试
- [ ] 加载图像按钮位置保持
- [ ] 上一张按钮位置保持
- [ ] 下一张按钮位置保持
- [ ] 保存标注按钮位置保持

### 2. 用户体验测试
- [ ] 页面位置保持不变
- [ ] 没有意外的页面滚动
- [ ] 用户可以继续在当前位置工作
- [ ] 操作体验自然流畅

### 3. 兼容性测试
- [ ] 标准版本功能正常
- [ ] 高精度版本功能正常
- [ ] 不同浏览器兼容性
- [ ] 不同屏幕尺寸适配

## 📋 实现细节

### JavaScript 代码修改
```javascript
// 移除以下代码
// window.scrollTo(0, 0);
```

### 函数修改列表
1. `loadImages()` - 移除页面位置固定
2. `prevImage()` - 移除页面位置固定
3. `nextImage()` - 移除页面位置固定
4. `saveAnnotations()` - 移除页面位置固定

### 版本同步
- 标准版本 (端口 9090) - 已修改
- 高精度版本 (端口 9092) - 已修改
- 两个版本功能保持一致

## 🎯 使用场景

### 适用场景
1. **连续标注**：在页面中间位置进行标注时保持位置
2. **图像浏览**：切换图像时保持当前查看位置
3. **批量操作**：连续操作时保持工作位置
4. **长时间工作**：避免频繁的页面位置调整

### 用户受益
1. **工作连续性**：保持当前工作位置
2. **操作效率**：无需重新调整页面位置
3. **使用便利**：操作更加自然流畅
4. **减少疲劳**：避免重复的滚动操作

## 🚨 注意事项

1. **用户体验**：确保页面位置保持不影响功能使用
2. **浏览器兼容**：所有现代浏览器都支持此行为
3. **功能完整性**：页面位置保持不影响其他功能
4. **用户习惯**：符合用户对Web应用的期望

## 📁 相关文件

### 修改的文件
- `datasets/web_annotation_tool.py` - 标准版本
- `datasets/web_annotation_tool_enhanced.py` - 高精度版本

### 测试文件
- `datasets/test_page_position_keep.py` - 页面位置保持测试脚本
- `datasets/PAGE_POSITION_KEEP_INSTRUCTIONS.md` - 本功能说明

## 🎉 总结

页面位置保持功能已成功实现，主要改进包括：

1. **用户体验优化**：点击按钮后页面保持在原位置
2. **操作连续性**：保持用户的工作流程不被中断
3. **自然交互**：符合用户对Web应用的期望
4. **功能完整性**：不影响原有功能，只优化用户体验

这个功能让标注工具的使用更加自然和舒适，特别适合需要长时间连续工作的场景。
"""
    
    with open("datasets/PAGE_POSITION_KEEP_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📄 已创建页面位置保持功能说明文档: datasets/PAGE_POSITION_KEEP_INSTRUCTIONS.md")

def main():
    print("🎯 页面位置保持功能测试")
    print("=" * 60)
    
    # 测试页面位置保持功能
    test_page_position_keep()
    
    # 创建功能说明
    create_page_position_keep_instructions()
    
    print("\n🎉 测试完成！")
    print("\n💡 使用建议:")
    print("1. 访问标注工具测试页面位置保持功能")
    print("2. 滚动页面到任意位置")
    print("3. 点击各个按钮验证页面是否保持在原位置")
    print("4. 确认操作体验自然流畅")

if __name__ == '__main__':
    main()
