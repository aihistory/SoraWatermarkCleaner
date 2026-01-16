# SoraWatermarkCleaner 项目规则

## 项目状态

### ✅ 已完成功能
- **水印检测模型训练**: 完成自定义YOLOv11s模型训练
- **数据集准备**: 439张图像，685个标注
- **模型性能**: 检测率100%，平均置信度0.812
- **训练工具**: 完整的训练、监控、测试工具链
- **标注工具**: 多种标注工具和验证脚本

### 📊 训练成果
- **最佳 mAP50**: 0.625
- **最佳 mAP50-95**: 0.4716
- **模型文件**: `runs/train/watermark_detector3/weights/best.pt`
- **测试结果**: 45张测试图像，100%检测率

## 项目结构

### 核心模块
- `sorawm/core.py` - 主要的水印移除处理逻辑
- `sorawm/watermark_detector.py` - 基于 YOLOv11s 的水印检测
- `sorawm/watermark_cleaner.py` - 基于 LAMA 模型的水印移除
- `sorawm/server/app.py` - FastAPI 微服务端点
- `app.py` - Streamlit 交互式 Web 界面

### 训练模块
- `train/simple_train.py` - 简化训练脚本
- `train/train_watermark_detector.py` - 完整训练脚本
- `train/monitor_training.py` - 训练监控工具
- `train/test_model.py` - 模型测试脚本
- `train/training_summary.py` - 训练总结工具
- `train/coco8.yaml` - 数据集配置文件

### 数据集工具
- `datasets/make_yolo_images.py` - 视频帧提取
- `datasets/setup_yolo_dataset.py` - 数据集结构创建
- `datasets/split_dataset.py` - 数据集分割
- `datasets/auto_annotate.py` - 自动标注工具
- `datasets/validate_annotations.py` - 标注验证
- `datasets/visualize_annotations.py` - 标注可视化

### 工具模块
- `sorawm/utils/video_utils.py` - 视频加载和处理
- `sorawm/utils/devices_utils.py` - GPU/CPU 设备管理
- `sorawm/utils/download_utils.py` - 模型下载
- `sorawm/utils/imputation_utils.py` - 缺失帧插值

## 开发约定

### 代码风格
- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 变量名使用 snake_case
- 类名使用 UpperCamelCase
- 保持现有的类型提示和日志记录

### 模块导入
- 所有数据集脚本需要添加项目根目录到 Python 路径
- 使用 `sys.path.insert(0, str(project_root))` 解决模块导入问题

### 训练相关
- 使用 `uv run python` 运行训练脚本
- 训练结果保存在 `runs/train/` 目录
- 测试结果保存在 `runs/test/` 目录
- 模型文件保存在 `runs/train/*/weights/` 目录

## 测试指南

### 训练测试
```bash
# 开始训练
uv run python train/simple_train.py

# 监控训练进度
uv run python train/monitor_training.py

# 测试模型
uv run python train/test_model.py

# 生成训练总结
uv run python train/training_summary.py
```

### 数据集验证
```bash
# 验证标注格式
uv run python datasets/validate_annotations.py

# 可视化标注
uv run python datasets/visualize_annotations.py

# 查看数据集统计
uv run python datasets/simple_edit.py --action stats
```

## 部署指南

### 模型使用
```python
from ultralytics import YOLO

# 加载训练好的模型
model = YOLO("runs/train/watermark_detector3/weights/best.pt")

# 检测图像中的水印
results = model("path/to/image.jpg")
results[0].show()
```

### 集成到项目
```python
# 在 sorawm/watermark_detector.py 中使用
from ultralytics import YOLO

class WatermarkDetector:
    def __init__(self, model_path="runs/train/watermark_detector3/weights/best.pt"):
        self.model = YOLO(model_path)
    
    def detect(self, image):
        results = self.model(image)
        return results[0].boxes
```

## 性能指标

### 模型性能
- **检测率**: 100%
- **平均置信度**: 0.812
- **最高置信度**: 0.864
- **推理速度**: 约5-10ms/图像 (GPU)
- **模型大小**: 54.5 MB

### 数据集统计
- **总图像数**: 439张
- **总标注数**: 685个
- **训练集**: 304张图像，425个标注
- **验证集**: 90张图像，172个标注
- **测试集**: 45张图像，88个标注

## 注意事项

### 环境要求
- Python 3.12+
- PyTorch + CUDA
- Ultralytics YOLO
- OpenCV
- FFmpeg

### 文件路径
- 使用绝对路径避免相对路径问题
- 训练配置文件使用绝对路径
- 模型文件路径需要正确配置

### 训练建议
- 使用GPU进行训练以获得最佳性能
- 监控训练进度避免过拟合
- 定期保存检查点
- 使用验证集评估模型性能

## 更新日志

### 2024-10-25
- ✅ 完成水印检测模型训练
- ✅ 实现完整的训练工具链
- ✅ 达到100%检测率
- ✅ 创建训练总结和部署指南
- ✅ 更新项目文档和规则

---

**项目状态**: 训练完成，可投入使用  
**最后更新**: 2024年10月25日
