# 水印检测数据集标注指南

## 概述
本指南介绍如何为 Sora 视频水印检测模型标注训练数据。

**🎉 训练完成状态**: 我们已成功完成数据集标注和模型训练，检测率达到100%，平均置信度0.812！

## 标注工具

### 方案 1: 自定义简单标注工具（推荐）
```bash
# 启动简单标注工具
uv run python datasets/simple_annotator.py

# 或指定目录
uv run python datasets/simple_annotator.py --images datasets/coco8/images/train --labels datasets/coco8/labels/train
```

**特点**:
- 基于 OpenCV，稳定可靠
- 专门为水印标注优化
- 支持 YOLO 格式
- 中文界面和帮助

### 方案 2: 批量模板标注
```bash
# 为所有图像创建模板标注
uv run python datasets/batch_annotate.py
```

**特点**:
- 快速创建基础标注
- 适合大量数据预处理
- 需要后续手动调整

### 方案 3: 简单编辑工具（推荐）
```bash
# 查看数据集统计
uv run python datasets/simple_edit.py --action stats

# 列出标注信息
uv run python datasets/simple_edit.py --action list --split train --count 10

# 查看标注方法
uv run python datasets/simple_edit.py --action view
```

**特点**:
- 无GUI依赖，稳定可靠
- 查看标注统计信息
- 列出标注详情
- 提供查看方法建议

### 方案 4: 生成可视化图像
```bash
# 生成带标注框的可视化图像
uv run python datasets/generate_visualizations.py --split train --count 20
```

**特点**:
- 生成带标注框的图像
- 便于查看标注效果
- 保存到可视化目录

### 方案 5: LabelImg（如果环境支持）
```bash
# 安装修复版本
pip install labelImg==1.8.5

# 启动
labelImg
```

### 在线工具选择
- **Roboflow**: 在线标注平台，支持团队协作
- **CVAT**: 开源计算机视觉标注工具
- **Label Studio**: 多功能数据标注平台

## 标注步骤

### 1. 准备数据
```bash
# 1. 提取视频帧
uv run python datasets/make_yolo_images.py

# 2. 创建目录结构
uv run python datasets/setup_yolo_dataset.py

# 3. 分割数据集
uv run python datasets/split_dataset.py
```

### 2. 开始标注

#### 使用 LabelImg 标注
1. 打开 LabelImg
2. 选择 "Open Dir" 打开图像目录: `datasets/coco8/images/train/`
3. 选择 "Change Save Dir" 设置标签保存目录: `datasets/coco8/labels/train/`
4. 选择 "YOLO" 格式
5. 开始标注水印区域

#### 标注规范
- **类别**: `watermark` (类别ID: 0)
- **边界框**: 紧密包围水印区域，不要包含过多背景
- **精度**: 边界框应准确贴合水印边缘
- **一致性**: 相同类型的水印应保持一致的标注风格

### 3. 标注质量检查

#### 必须标注的水印类型
- [ ] Sora 官方水印
- [ ] 平台水印 (如 YouTube, TikTok 等)
- [ ] 用户添加的水印
- [ ] 半透明水印
- [ ] 动态水印

#### 标注注意事项
- ✅ **包含**: 完整的水印区域
- ✅ **精确**: 边界框紧贴水印边缘
- ✅ **一致**: 相同水印类型保持统一标注
- ❌ **避免**: 包含过多背景区域
- ❌ **避免**: 遗漏部分水印区域
- ❌ **避免**: 标注非水印元素

## YOLO 标注格式

### 标签文件格式 (.txt)
```
class_id center_x center_y width height
```

### 示例
```
0 0.5 0.3 0.2 0.1
```
- `0`: 类别ID (watermark)
- `0.5`: 中心点X坐标 (相对坐标 0-1)
- `0.3`: 中心点Y坐标 (相对坐标 0-1)  
- `0.2`: 宽度 (相对坐标 0-1)
- `0.1`: 高度 (相对坐标 0-1)

## 数据集统计

### 建议的数据集规模
- **训练集**: 70% (至少 1000 张图像)
- **验证集**: 20% (至少 200 张图像)
- **测试集**: 10% (至少 100 张图像)

### 质量要求
- 每张图像至少包含 1 个水印标注
- 标注准确率 > 95%
- 边界框 IoU 与真实水印 > 0.8

## 验证标注质量

### 使用脚本验证
```bash
# 验证标注文件格式
uv run python datasets/validate_annotations.py

# 可视化标注结果
uv run python datasets/visualize_annotations.py
```

### 手动检查
1. 随机抽样检查标注准确性
2. 确保边界框位置正确
3. 验证类别标签正确
4. 检查是否有遗漏的水印

## 常见问题

### Q: 如何处理部分遮挡的水印？
A: 标注可见部分，确保边界框准确包围可见区域。

### Q: 如何处理多个水印？
A: 为每个水印创建独立的边界框标注。

### Q: 如何处理动态水印？
A: 标注水印在每一帧中的位置，保持时间一致性。

### Q: 标注速度慢怎么办？
A: 使用快捷键提高效率，考虑使用预标注工具。

## 下一步

完成标注后：
1. 运行训练脚本: `uv run python train/simple_train.py`
2. 监控训练进度: `uv run python train/monitor_training.py`
3. 测试模型性能: `uv run python train/test_model.py`
4. 生成训练总结: `uv run python train/training_summary.py`

## 🎉 训练完成状态

我们已成功完成整个训练流程：

### 数据集统计
- **总图像数**: 439张
- **总标注数**: 685个
- **训练集**: 304张图像，425个标注
- **验证集**: 90张图像，172个标注
- **测试集**: 45张图像，88个标注

### 训练结果
- **最佳 mAP50**: 0.625
- **最佳 mAP50-95**: 0.4716
- **检测率**: 100%
- **平均置信度**: 0.812
- **模型文件**: `runs/train/watermark_detector3/weights/best.pt`

### 测试结果
- **测试图像**: 45张
- **检测率**: 100% (所有图像都成功检测到水印)
- **总检测数**: 63个水印
- **平均置信度**: 0.812
- **最高置信度**: 0.864

详细训练总结请参考 [TRAINING_COMPLETE_SUMMARY.md](../TRAINING_COMPLETE_SUMMARY.md)。

## 标注工具快捷键 (LabelImg)

- `W`: 创建边界框
- `D`: 下一张图像
- `A`: 上一张图像
- `Del`: 删除选中的边界框
- `Ctrl+S`: 保存标注
- `Ctrl+D`: 复制边界框
