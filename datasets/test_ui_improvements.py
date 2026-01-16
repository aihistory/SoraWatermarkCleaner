#!/usr/bin/env python3
"""
测试界面改进功能
"""

import requests
import time
from pathlib import Path

def test_ui_improvements():
    """测试界面改进功能"""
    print("🧪 测试界面改进功能")
    print("=" * 40)
    
    # 测试标准版本
    print("\n📋 测试标准版本 (端口 9090)")
    test_version("http://localhost:9090", "标准版本")
    
    # 测试高精度版本
    print("\n📋 测试高精度版本 (端口 9092)")
    test_version("http://localhost:9092", "高精度版本")

def test_version(base_url, version_name):
    """测试指定版本的界面改进"""
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
                
                # 测试界面功能
                test_interface_features(base_url, version_name, images[0])
            else:
                print(f"❌ {version_name} 没有找到图像")
        else:
            print(f"❌ {version_name} 获取图像列表失败")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {version_name} 连接失败: {e}")

def test_interface_features(base_url, version_name, image_name):
    """测试界面功能"""
    print(f"\n🖼️ 测试 {version_name} 界面功能")
    print("-" * 30)
    
    print(f"✅ 测试图像: {image_name}")
    print(f"✅ 预期路径: datasets/coco8/images/train/{image_name}")
    
    print(f"\n💡 手动测试步骤:")
    print(f"1. 访问 {base_url}")
    print(f"2. 检查界面布局:")
    print(f"   - '🔄 自动复制标注' 标签应该在开关按钮的左侧")
    print(f"   - 开关按钮应该在标签的右侧")
    print(f"   - 复制模式选择框应该在开关的右侧")
    print(f"3. 加载图像后检查信息显示:")
    print(f"   - '当前图像:' 应该显示图像文件名")
    print(f"   - '图像路径:' 应该显示完整路径")
    print(f"4. 测试自动复制功能:")
    print(f"   - 点击开关启用/禁用自动复制")
    print(f"   - 选择不同的复制模式")
    print(f"   - 创建标注后切换到下一张图像")

def create_ui_improvements_instructions():
    """创建界面改进说明"""
    instructions = """
# 界面改进功能说明

## 🎯 改进内容

### 1. 显示当前图像路径
- **位置**：信息区域中的"图像路径"字段
- **内容**：显示当前图像的完整路径
- **格式**：`目录路径/图像文件名`
- **示例**：`datasets/coco8/images/train/image_000000_frame_000001.jpg`

### 2. 调整自动复制标注布局
- **改进前**：标签在开关按钮的右侧
- **改进后**：标签在开关按钮的左侧
- **布局**：标签 → 开关 → 复制模式选择框

## 🛠️ 技术实现

### 1. HTML结构修改

**修改前**：
```html
<label class="copy-switch">
    <input type="checkbox" id="auto-copy-switch" onchange="toggleAutoCopy()">
    <span class="slider"></span>
    <span class="copy-label">🔄 自动复制标注</span>
</label>
```

**修改后**：
```html
<span class="copy-label">🔄 自动复制标注</span>
<label class="copy-switch">
    <input type="checkbox" id="auto-copy-switch" onchange="toggleAutoCopy()">
    <span class="slider"></span>
</label>
```

### 2. 图像路径显示

**新增HTML元素**：
```html
<p><strong>图像路径:</strong> <span id="current-image-path">未加载</span></p>
```

**JavaScript实现**：
```javascript
if (currentImagePathElement) {
    const fullPath = `${imagesDir}/${imageName}`;
    currentImagePathElement.textContent = fullPath;
} else {
    console.warn('current-image-path 元素未找到');
}
```

## 🎨 界面布局

### 自动复制控制区域
```
[🔄 自动复制标注] [开关] [复制模式选择框]
    标签           开关     下拉菜单
```

### 信息显示区域
```
当前图像: image_000000_frame_000001.jpg
图像路径: datasets/coco8/images/train/image_000000_frame_000001.jpg
```

## 🧪 测试验证

### 1. 布局测试
- [ ] 标签在开关左侧
- [ ] 开关在标签右侧
- [ ] 复制模式选择框在开关右侧
- [ ] 整体布局美观协调

### 2. 路径显示测试
- [ ] 图像路径正确显示
- [ ] 路径格式正确
- [ ] 切换图像时路径更新
- [ ] 路径信息准确无误

### 3. 功能测试
- [ ] 自动复制开关正常工作
- [ ] 复制模式选择正常工作
- [ ] 图像加载和切换正常
- [ ] 所有功能无异常

## 📋 使用说明

### 1. 查看图像路径
1. 加载图像后，在信息区域查看"图像路径"字段
2. 路径显示格式：`目录路径/图像文件名`
3. 切换图像时路径会自动更新

### 2. 使用自动复制功能
1. 在自动复制控制区域找到"🔄 自动复制标注"标签
2. 点击标签右侧的开关启用/禁用功能
3. 选择复制模式（所有标注/仅水印/仅Logo/仅文本）
4. 创建标注后点击"下一张"按钮自动复制

## 🎯 改进效果

### 1. 用户体验提升
- ✅ 更直观的界面布局
- ✅ 清晰的图像路径信息
- ✅ 更好的功能组织

### 2. 信息显示完善
- ✅ 显示完整的图像路径
- ✅ 便于文件管理和定位
- ✅ 提高工作效率

### 3. 界面美观性
- ✅ 标签和开关布局更合理
- ✅ 视觉层次更清晰
- ✅ 操作更直观

## 🚨 注意事项

1. 图像路径基于设置的图像目录
2. 路径显示为相对路径格式
3. 标签和开关的布局已优化
4. 所有功能保持向后兼容
"""
    
    with open("datasets/UI_IMPROVEMENTS_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📄 已创建界面改进说明文档: datasets/UI_IMPROVEMENTS_INSTRUCTIONS.md")

def main():
    print("🎯 界面改进功能测试")
    print("=" * 50)
    
    # 测试界面改进
    test_ui_improvements()
    
    # 创建说明文档
    create_ui_improvements_instructions()
    
    print("\n🎉 测试完成！")
    print("\n💡 使用建议:")
    print("1. 访问标注工具查看新的界面布局")
    print("2. 检查图像路径显示功能")
    print("3. 测试自动复制功能的布局改进")
    print("4. 验证所有功能正常工作")

if __name__ == '__main__':
    main()
