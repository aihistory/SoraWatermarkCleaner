# 🚀 快速开始训练指南

## 5分钟快速开始

### 1. 环境准备
```bash
# 安装依赖
uv sync

# 激活环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

### 2. 数据准备
```bash
# 提取视频帧 (如果有视频文件)
uv run python datasets/make_yolo_images.py

# 创建数据集结构
uv run python datasets/setup_yolo_dataset.py

# 分割数据集
uv run python datasets/split_dataset.py

# 自动标注 (推荐)
uv run python datasets/auto_annotate.py
```

### 3. 开始训练
```bash
# 启动训练
uv run python train/simple_train.py
```

### 4. 监控训练
```bash
# 在另一个终端监控训练进度
uv run python train/monitor_training.py
```

### 5. 测试模型
```bash
# 训练完成后测试模型
uv run python train/test_model.py
```

## 🎯 预期结果

- **训练时间**: 约 1-2 小时 (GPU)
- **检测率**: 100%
- **平均置信度**: >0.8
- **模型文件**: `runs/train/watermark_detector*/weights/best.pt`

## 📋 检查清单

- [ ] 环境安装完成
- [ ] 数据集准备完成
- [ ] 标注完成
- [ ] 训练开始
- [ ] 监控训练进度
- [ ] 测试模型性能
- [ ] 保存最佳模型

## 🆘 遇到问题？

1. **查看完整指南**: [COMPLETE_TRAINING_GUIDE.md](COMPLETE_TRAINING_GUIDE.md)
2. **检查故障排除**: 指南中的故障排除章节
3. **查看项目状态**: [PROJECT_STATUS.md](PROJECT_STATUS.md)

---

**开始您的训练之旅！** 🎉

