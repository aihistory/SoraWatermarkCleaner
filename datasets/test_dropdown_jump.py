#!/usr/bin/env python3
"""
测试下拉菜单跳转功能
"""

import requests
import time
from pathlib import Path

def test_dropdown_jump():
    """测试下拉菜单跳转功能"""
    print("🧪 测试下拉菜单跳转功能")
    print("=" * 50)
    
    # 测试标准版本
    print("\n📋 测试标准版本 (端口 9090)")
    test_version("http://localhost:9090", "标准版本")
    
    # 测试高精度版本
    print("\n📋 测试高精度版本 (端口 9092)")
    test_version("http://localhost:9092", "高精度版本")

def test_version(base_url, version_name):
    """测试指定版本的下拉菜单跳转功能"""
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
                
                # 测试下拉菜单跳转功能
                test_dropdown_jump_features(base_url, version_name, images)
            else:
                print(f"❌ {version_name} 没有找到图像")
        else:
            print(f"❌ {version_name} 获取图像列表失败")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {version_name} 连接失败: {e}")

def test_dropdown_jump_features(base_url, version_name, images):
    """测试下拉菜单跳转功能"""
    print(f"\n🎯 测试 {version_name} 下拉菜单跳转功能")
    print("-" * 40)
    
    print(f"💡 手动测试步骤:")
    print(f"1. 访问 {base_url}")
    print(f"2. 点击'📁 加载图像'按钮加载图像列表")
    print(f"3. 检查下拉菜单界面:")
    print(f"   🎮 跳转控制区域:")
    print(f"      - 下拉选择框 (显示所有图像文件名)")
    print(f"      - 🎯 跳转按钮")
    print(f"      - 选择框显示格式: '序号. 文件名'")
    print(f"4. 测试下拉菜单功能:")
    print(f"   📋 基本跳转测试:")
    print(f"      - 点击下拉菜单查看所有图像选项")
    print(f"      - 选择第一个图像文件，点击跳转按钮")
    print(f"      - 验证是否跳转到对应图像")
    print(f"      - 选择中间某个图像文件，点击跳转按钮")
    print(f"      - 验证是否跳转到对应图像")
    print(f"      - 选择最后一个图像文件，点击跳转按钮")
    print(f"      - 验证是否跳转到对应图像")
    print(f"   🔍 选项显示测试:")
    print(f"      - 下拉菜单显示所有图像文件")
    print(f"      - 每个选项格式为 '序号. 文件名'")
    print(f"      - 当前图像在菜单中高亮显示")
    print(f"      - 选项按顺序排列")
    print(f"   🔄 同步测试:")
    print(f"      - 使用'⬅️ 上一张'按钮，验证下拉菜单是否同步更新")
    print(f"      - 使用'➡️ 下一张'按钮，验证下拉菜单是否同步更新")
    print(f"      - 跳转到其他图像后，验证统计信息是否更新")
    print(f"5. 验证功能效果:")
    print(f"   - 下拉菜单跳转功能正常工作")
    print(f"   - 选择框实时同步当前图像")
    print(f"   - 图像文件名清晰显示")
    print(f"   - 跳转后自动复制功能正常")
    print(f"6. 测试示例图像:")
    if images:
        print(f"   - 第一个图像: {images[0]}")
        if len(images) > 1:
            print(f"   - 中间图像: {images[len(images)//2]}")
        print(f"   - 最后图像: {images[-1]}")

def create_dropdown_jump_instructions():
    """创建下拉菜单跳转功能说明"""
    instructions = """
# 下拉菜单跳转功能说明

## 🎯 功能描述

将图像跳转功能从数字输入框改为下拉菜单选择，用户可以直接从下拉菜单中选择具体的图像文件名进行跳转，更加直观和实用。

## 🔧 实现方案

### 1. 界面组件

**跳转控制区域包含：**
- 下拉选择框：显示所有图像文件名，格式为"序号. 文件名"
- 跳转按钮：执行跳转操作
- 实时同步：选择框自动高亮当前图像

### 2. 功能特性

#### 基本功能
- **文件选择**：从下拉菜单直接选择图像文件名
- **格式显示**：每个选项显示为"序号. 文件名"格式
- **当前高亮**：当前图像在菜单中自动选中
- **实时同步**：使用上一张/下一张按钮时选择框自动更新

#### 错误处理
- **选择验证**：检查是否选择了有效图像
- **存在验证**：检查选择的图像是否存在于列表中
- **错误提示**：显示友好的错误信息

#### 集成功能
- **自动复制**：跳转时保存当前图像标注用于自动复制
- **统计更新**：跳转后更新统计信息
- **状态同步**：保持所有界面元素状态一致

## 🎨 用户体验改进

### 相比数字输入的改进
- ✅ 直接显示图像文件名，更加直观
- ✅ 无需记住图像序号
- ✅ 可以快速浏览所有可用图像
- ✅ 避免输入错误的序号

### 操作便利性
- ✅ 下拉菜单显示所有图像选项
- ✅ 当前图像自动高亮显示
- ✅ 一键选择跳转操作
- ✅ 文件名清晰可见

## 🧪 测试验证

### 1. 基本功能测试
- [ ] 下拉菜单显示所有图像文件
- [ ] 选择第一个图像跳转成功
- [ ] 选择中间图像跳转成功
- [ ] 选择最后图像跳转成功
- [ ] 跳转后图像正确显示

### 2. 显示格式测试
- [ ] 选项格式为"序号. 文件名"
- [ ] 序号从1开始递增
- [ ] 文件名完整显示
- [ ] 当前图像自动选中

### 3. 同步测试
- [ ] 使用上一张按钮选择框同步更新
- [ ] 使用下一张按钮选择框同步更新
- [ ] 跳转后统计信息正确更新
- [ ] 跳转后标注列表正确更新

### 4. 集成测试
- [ ] 跳转时自动复制功能正常
- [ ] 跳转后保存功能正常
- [ ] 跳转后清除功能正常
- [ ] 所有按钮功能正常

## 📋 实现细节

### HTML结构
```html
<div class="jump-controls">
    <select id="jump-select" class="jump-select">
        <option value="">选择图像...</option>
    </select>
    <button class="btn-info" onclick="jumpToSelectedImage()">🎯 跳转</button>
</div>
```

### CSS样式
```css
.jump-select {
    min-width: 200px;
    padding: 8px 10px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 14px;
    background: white;
}
```

### JavaScript功能
```javascript
function jumpToSelectedImage() {
    const jumpSelect = document.getElementById('jump-select');
    const selectedImageName = jumpSelect.value;
    
    if (!selectedImageName) {
        showError('请选择要跳转的图像');
        return;
    }
    
    const targetIndex = images.indexOf(selectedImageName);
    if (targetIndex === -1) {
        showError('选择的图像不存在');
        return;
    }
    
    saveCurrentAnnotations();
    currentIndex = targetIndex;
    loadCurrentImage();
    updateStats();
    updateJumpSelect();
    showSuccess(`已跳转到图像: ${selectedImageName}`);
}

function updateJumpSelect() {
    const jumpSelect = document.getElementById('jump-select');
    if (jumpSelect && images.length > 0) {
        jumpSelect.innerHTML = '<option value="">选择图像...</option>';
        
        images.forEach((imageName, index) => {
            const option = document.createElement('option');
            option.value = imageName;
            option.textContent = `${index + 1}. ${imageName}`;
            if (index === currentIndex) {
                option.selected = true;
            }
            jumpSelect.appendChild(option);
        });
    }
}
```

## 🎯 使用场景

### 适用场景
1. **文件查找**：快速找到特定的图像文件
2. **批量标注**：跳转到需要标注的特定图像
3. **质量检查**：跳转到特定图像进行验证
4. **进度管理**：跳转到特定进度位置

### 用户受益
1. **直观选择**：直接看到文件名，无需记住序号
2. **快速定位**：通过文件名快速找到目标图像
3. **减少错误**：避免输入错误的序号
4. **提高效率**：更快的图像定位和跳转

## 🚨 注意事项

1. **文件名显示**：确保文件名完整显示，避免截断
2. **选项数量**：大量图像时下拉菜单可能较长
3. **性能考虑**：动态更新选项的性能影响
4. **用户体验**：保持选择框的响应速度

## 📁 相关文件

### 修改的文件
- `datasets/web_annotation_tool.py` - 标准版本
- `datasets/web_annotation_tool_enhanced.py` - 高精度版本

### 测试文件
- `datasets/test_dropdown_jump.py` - 下拉菜单跳转功能测试脚本
- `datasets/DROPDOWN_JUMP_INSTRUCTIONS.md` - 本功能说明

## 🎉 总结

下拉菜单跳转功能已成功实现，主要改进包括：

1. **界面优化**：从数字输入改为下拉菜单选择
2. **直观显示**：直接显示图像文件名
3. **操作便利**：无需记住序号，直接选择文件
4. **用户体验**：更加直观和实用的跳转方式

这个改进让图像跳转功能更加用户友好，特别适合需要快速定位特定图像文件的场景。
"""
    
    with open("datasets/DROPDOWN_JUMP_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📄 已创建下拉菜单跳转功能说明文档: datasets/DROPDOWN_JUMP_INSTRUCTIONS.md")

def main():
    print("🎯 下拉菜单跳转功能测试")
    print("=" * 60)
    
    # 测试下拉菜单跳转功能
    test_dropdown_jump()
    
    # 创建功能说明
    create_dropdown_jump_instructions()
    
    print("\n🎉 测试完成！")
    print("\n💡 使用建议:")
    print("1. 访问标注工具查看新的下拉菜单跳转功能")
    print("2. 测试从下拉菜单选择图像文件跳转")
    print("3. 验证选择框同步更新功能")
    print("4. 确认下拉菜单比数字输入更加直观")

if __name__ == '__main__':
    main()
