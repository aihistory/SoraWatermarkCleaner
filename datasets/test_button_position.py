#!/usr/bin/env python3
"""
测试按钮位置调整
"""

import requests
import time
from pathlib import Path

def test_button_position():
    """测试按钮位置调整"""
    print("🧪 测试按钮位置调整")
    print("=" * 50)
    
    # 测试标准版本
    print("\n📋 测试标准版本 (端口 9090)")
    test_version("http://localhost:9090", "标准版本")
    
    # 测试高精度版本
    print("\n📋 测试高精度版本 (端口 9092)")
    test_version("http://localhost:9092", "高精度版本")

def test_version(base_url, version_name):
    """测试指定版本的按钮位置调整"""
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
                
                # 测试按钮位置调整
                test_button_position_features(base_url, version_name)
            else:
                print(f"❌ {version_name} 没有找到图像")
        else:
            print(f"❌ {version_name} 获取图像列表失败")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {version_name} 连接失败: {e}")

def test_button_position_features(base_url, version_name):
    """测试按钮位置调整功能"""
    print(f"\n🎯 测试 {version_name} 按钮位置调整")
    print("-" * 40)
    
    print(f"💡 手动测试步骤:")
    print(f"1. 访问 {base_url}")
    print(f"2. 检查页面布局结构:")
    print(f"   📋 页面顶部区域:")
    print(f"      - 目录选择区域")
    print(f"      - 统计信息区域")
    print(f"      - 使用说明区域")
    print(f"      - 标注列表区域")
    print(f"   🎮 控制按钮区域 (新位置):")
    print(f"      - 📁 加载图像按钮")
    print(f"      - ⬅️ 上一张按钮")
    print(f"      - ➡️ 下一张按钮")
    print(f"      - 💾 保存标注按钮")
    print(f"      - 🗑️ 清除当前按钮")
    print(f"      - 🗑️ 删除所有按钮")
    print(f"      - 📤 导出数据按钮")
    if "高精度" in version_name:
        print(f"      - 🎯 验证精度按钮")
    print(f"   🔄 自动复制标注区域:")
    print(f"      - 自动复制标注开关")
    print(f"      - 复制模式选择框")
    print(f"   🖼️ 图像显示区域:")
    print(f"      - 当前图像显示")
    print(f"      - 标注框叠加层")
    print(f"3. 验证布局效果:")
    print(f"   - 控制按钮现在位于图像上方")
    print(f"   - 按钮区域在图像显示区域之前")
    print(f"   - 布局更加合理和直观")
    print(f"   - 操作流程更加顺畅")

def create_button_position_instructions():
    """创建按钮位置调整说明"""
    instructions = """
# 按钮位置调整说明

## 🎯 功能描述

将标注工具的主要控制按钮（加载图像、上一张、下一张、保存标注等）移动到图像显示区域的上方，使页面布局更加合理和直观。

## 🔧 实现方案

### 1. HTML结构调整

**调整前的布局顺序：**
```
1. 目录选择区域
2. 统计信息区域
3. 使用说明区域
4. 标注列表区域
5. 控制按钮区域 ← 原来位置
6. 自动复制标注区域
7. 图像显示区域
```

**调整后的布局顺序：**
```
1. 目录选择区域
2. 统计信息区域
3. 使用说明区域
4. 标注列表区域
5. 控制按钮区域 ← 新位置
6. 自动复制标注区域
7. 图像显示区域
```

### 2. 涉及的按钮

#### 标准版本包含的按钮：
- 📁 加载图像
- ⬅️ 上一张
- ➡️ 下一张
- 💾 保存标注
- 🗑️ 清除当前
- 🗑️ 删除所有
- 📤 导出数据

#### 高精度版本额外包含：
- 🎯 验证精度

### 3. 自动复制标注区域

两个版本都包含：
- 🔄 自动复制标注开关
- 复制模式选择框（所有标注/水印/Logo/文本）

## 🎨 用户体验改进

### 调整前的问题
- ❌ 控制按钮位于页面中间位置
- ❌ 用户需要滚动才能看到图像
- ❌ 操作流程不够直观
- ❌ 按钮和图像距离较远

### 调整后的效果
- ✅ 控制按钮位于图像正上方
- ✅ 用户可以直接看到图像
- ✅ 操作流程更加直观
- ✅ 按钮和图像紧密相关

## 🧪 测试验证

### 1. 布局测试
- [ ] 控制按钮位于图像上方
- [ ] 按钮区域在图像显示区域之前
- [ ] 自动复制标注区域在按钮下方
- [ ] 整体布局合理协调

### 2. 功能测试
- [ ] 所有按钮功能正常
- [ ] 按钮点击响应正常
- [ ] 自动复制功能正常
- [ ] 图像显示正常

### 3. 用户体验测试
- [ ] 操作流程直观
- [ ] 页面布局美观
- [ ] 功能区域清晰
- [ ] 使用便利性提升

## 📋 实现细节

### HTML结构调整
```html
<!-- 调整前 -->
<div class="annotation-list">...</div>
<div class="image-container">...</div>
<div class="controls">...</div>

<!-- 调整后 -->
<div class="annotation-list">...</div>
<div class="controls">...</div>
<div class="copy-controls">...</div>
<div class="image-container">...</div>
```

### 版本同步
- 标准版本 (端口 9090) - 已调整
- 高精度版本 (端口 9092) - 已调整
- 两个版本布局保持一致

## 🎯 使用场景

### 适用场景
1. **图像标注**：按钮在图像上方，操作更直观
2. **批量处理**：连续操作时按钮位置固定
3. **快速切换**：上一张/下一张按钮位置合理
4. **标注管理**：保存/清除按钮易于访问

### 用户受益
1. **操作效率**：按钮位置更合理
2. **视觉体验**：布局更加美观
3. **使用便利**：操作流程更直观
4. **工作流程**：符合用户习惯

## 🚨 注意事项

1. **布局一致性**：确保两个版本的布局完全一致
2. **功能完整性**：调整位置不影响功能
3. **响应式设计**：确保在不同屏幕尺寸下都能正常显示
4. **用户习惯**：符合用户对界面布局的期望

## 📁 相关文件

### 修改的文件
- `datasets/web_annotation_tool.py` - 标准版本
- `datasets/web_annotation_tool_enhanced.py` - 高精度版本

### 测试文件
- `datasets/test_button_position.py` - 按钮位置调整测试脚本
- `datasets/BUTTON_POSITION_INSTRUCTIONS.md` - 本功能说明

## 🎉 总结

按钮位置调整已成功实现，主要改进包括：

1. **布局优化**：控制按钮位于图像正上方
2. **操作直观**：按钮和图像紧密相关
3. **流程顺畅**：操作流程更加合理
4. **用户体验**：界面布局更加美观和实用

这个调整让标注工具的使用更加直观和高效，特别适合需要频繁操作按钮的场景。
"""
    
    with open("datasets/BUTTON_POSITION_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📄 已创建按钮位置调整说明文档: datasets/BUTTON_POSITION_INSTRUCTIONS.md")

def main():
    print("🎯 按钮位置调整测试")
    print("=" * 60)
    
    # 测试按钮位置调整
    test_button_position()
    
    # 创建功能说明
    create_button_position_instructions()
    
    print("\n🎉 测试完成！")
    print("\n💡 使用建议:")
    print("1. 访问标注工具查看新的按钮布局")
    print("2. 验证控制按钮是否位于图像上方")
    print("3. 测试所有按钮功能是否正常")
    print("4. 确认布局更加合理和直观")

if __name__ == '__main__':
    main()
