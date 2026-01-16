# SoraWatermarkCleaner 完整模型训练指南

## 📋 目录

1. [概述](#概述)
2. [环境准备](#环境准备)
3. [数据集准备](#数据集准备)
4. [数据标注](#数据标注)
5. [模型训练](#模型训练)
6. [训练监控](#训练监控)
7. [模型测试](#模型测试)
8. [模型部署](#模型部署)
9. [性能优化](#性能优化)
10. [故障排除](#故障排除)
11. [最佳实践](#最佳实践)

## 概述

本指南将带您完成 Sora 水印检测模型的完整训练流程，从数据准备到模型部署。我们将使用 YOLOv11s 架构训练一个高精度的水印检测模型。

### 训练目标
- **检测率**: 100%
- **平均置信度**: >0.8
- **推理速度**: <10ms/图像
- **模型大小**: <60MB

### 技术栈
- **深度学习框架**: PyTorch + Ultralytics YOLO
- **模型架构**: YOLOv11s
- **数据处理**: OpenCV, NumPy
- **可视化**: Matplotlib

## 环境准备

### 1. 系统要求

#### 硬件要求
- **GPU**: NVIDIA GPU (推荐 RTX 3060 或更高)
- **内存**: 16GB RAM (推荐 32GB)
- **存储**: 50GB 可用空间
- **CPU**: 多核处理器 (推荐 8 核以上)

#### 软件要求
- **操作系统**: Ubuntu 20.04+ / Windows 10+ / macOS 12+
- **Python**: 3.8-3.12
- **CUDA**: 11.8+ (GPU 训练必需)

### 2. 环境安装

#### 使用 uv (推荐)
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone https://github.com/linkedlist771/SoraWatermarkCleaner.git
cd SoraWatermarkCleaner

# 安装依赖
uv sync

# 激活环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

#### 使用 pip
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 验证安装

```bash
# 检查 Python 版本
python --version

# 检查 PyTorch 和 CUDA
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

# 检查 Ultralytics
python -c "from ultralytics import YOLO; print('YOLO installed successfully')"
```

## 数据集准备

### 1. 视频数据收集

#### 数据来源
- Sora 生成的视频文件
- 包含水印的视频样本
- 不同场景和角度的视频

#### 数据要求
- **格式**: MP4, AVI, MOV
- **分辨率**: 720p 或更高
- **时长**: 每个视频 10-60 秒
- **数量**: 至少 50 个视频文件

### 2. 视频帧提取

```bash
# 运行帧提取脚本
uv run python datasets/make_yolo_images.py
```

#### 脚本功能
- 从视频中提取关键帧
- 自动调整图像尺寸
- 保存为 JPG 格式
- 生成图像列表

#### 输出结构
```
datasets/
├── images/
│   ├── image_000000_frame_000001.jpg
│   ├── image_000000_frame_000002.jpg
│   └── ...
└── image_list.txt
```

### 3. 数据集结构创建

```bash
# 创建 YOLO 数据集结构
uv run python datasets/setup_yolo_dataset.py
```

#### 目录结构
```
datasets/coco8/
├── images/
│   ├── train/          # 训练图像
│   ├── val/            # 验证图像
│   └── test/           # 测试图像
└── labels/
    ├── train/          # 训练标注
    ├── val/            # 验证标注
    └── test/           # 测试标注
```

### 4. 数据集分割

```bash
# 分割数据集 (默认比例: 70% 训练, 20% 验证, 10% 测试)
uv run python datasets/split_dataset.py
```

#### 分割参数
- **训练集**: 70% (用于模型训练)
- **验证集**: 20% (用于模型验证)
- **测试集**: 10% (用于最终测试)

## 数据标注

### 1. 标注工具选择

#### 方案 1: 自动标注 (推荐)
```bash
# 使用自动标注工具
uv run python datasets/auto_annotate.py
```

**特点**:
- 快速生成基础标注
- 基于模板匹配
- 适合大量数据预处理

#### 方案 2: 手动标注
```bash
# 使用简单标注工具
uv run python datasets/simple_annotator.py
```

**特点**:
- 精确标注
- 支持边界框调整
- 适合精细调整

#### 方案 3: 批量标注
```bash
# 批量创建标注
uv run python datasets/batch_annotate.py
```

### 2. 标注格式

#### YOLO 格式
```
class_id center_x center_y width height
```

**示例**:
```
0 0.5 0.3 0.1 0.05
```

**说明**:
- `class_id`: 类别ID (0=水印)
- `center_x`: 中心点X坐标 (归一化)
- `center_y`: 中心点Y坐标 (归一化)
- `width`: 边界框宽度 (归一化)
- `height`: 边界框高度 (归一化)

### 3. 标注质量检查

```bash
# 验证标注格式
uv run python datasets/validate_annotations.py

# 可视化标注
uv run python datasets/visualize_annotations.py

# 查看数据集统计
uv run python datasets/simple_edit.py --action stats
```

#### 质量要求
- **标注完整性**: 所有水印都被标注
- **边界框精度**: 边界框紧贴水印边缘
- **格式正确性**: 符合 YOLO 格式要求
- **类别一致性**: 所有水印使用相同类别ID

## 模型训练

### 1. 训练配置

#### 配置文件: `train/coco8.yaml`
```yaml
# 数据集根目录
path: /path/to/datasets/coco8

# 训练、验证、测试集路径
train: images/train
val: images/val
test: images/test

# 类别定义
names:
  0: watermark
```

### 2. 开始训练

#### 简化训练 (推荐新手)
```bash
# 使用简化训练脚本
uv run python train/simple_train.py
```

**特点**:
- 预设最佳参数
- 自动保存模型
- 简化配置

#### 完整训练 (高级用户)
```bash
# 使用完整训练脚本
uv run python train/train_watermark_detector.py
```

**特点**:
- 完整参数控制
- 详细训练日志
- 高级优化选项

### 3. 训练参数

#### 基础参数
```python
# 训练轮数
epochs = 100

# 图像尺寸
imgsz = 640

# 批大小
batch = 16  # GPU 内存允许的情况下

# 学习率
lr0 = 0.01

# 设备
device = "cuda"  # 或 "cpu"
```

#### 高级参数
```python
# 数据增强
augment = True
mosaic = 1.0
mixup = 0.0

# 优化器
optimizer = "auto"
momentum = 0.937
weight_decay = 0.0005

# 损失函数权重
box = 7.5
cls = 0.5
dfl = 1.5
```

### 4. 训练过程

#### 阶段 1: 预热 (前 3 轮)
- 学习率逐渐增加
- 模型参数初始化
- 损失函数稳定

#### 阶段 2: 主要训练 (4-80 轮)
- 学习率按计划衰减
- 模型参数优化
- 损失函数下降

#### 阶段 3: 精调 (81-100 轮)
- 学习率进一步降低
- 模型参数微调
- 性能指标提升

## 训练监控

### 1. 实时监控

```bash
# 启动训练监控
uv run python train/monitor_training.py
```

#### 监控指标
- **训练损失**: 模型在训练集上的损失
- **验证损失**: 模型在验证集上的损失
- **mAP50**: 在 IoU=0.5 时的平均精度
- **mAP50-95**: 在 IoU=0.5-0.95 时的平均精度
- **学习率**: 当前学习率值

### 2. 训练曲线

#### 自动生成
训练过程中会自动生成训练曲线图：
- `runs/train/watermark_detector/training_curves.png`

#### 曲线解读
- **损失曲线**: 应该呈下降趋势
- **精度曲线**: 应该呈上升趋势
- **学习率曲线**: 按计划衰减

### 3. 早停机制

#### 配置参数
```python
# 早停耐心值
patience = 20

# 最小改善阈值
min_delta = 0.001
```

#### 触发条件
- 验证损失连续 20 轮无改善
- 自动保存最佳模型
- 提前结束训练

## 模型测试

### 1. 模型评估

```bash
# 在测试集上评估模型
uv run python train/test_model.py
```

#### 评估指标
- **检测率**: 成功检测的水印比例
- **平均置信度**: 检测结果的平均置信度
- **最高置信度**: 检测结果的最高置信度
- **推理速度**: 单张图像处理时间

### 2. 可视化测试

#### 生成测试结果
```bash
# 在测试图像上运行模型
uv run python train/test_model.py --option 1
```

#### 输出文件
- `runs/test/test_images/`: 带检测框的图像
- `runs/test/test_images/test_report.txt`: 测试报告

### 3. 性能基准

#### 目标指标
- **检测率**: >95%
- **平均置信度**: >0.8
- **推理速度**: <10ms/图像
- **模型大小**: <60MB

## 模型部署

### 1. 模型导出

#### 导出为 ONNX
```python
from ultralytics import YOLO

# 加载训练好的模型
model = YOLO("runs/train/watermark_detector3/weights/best.pt")

# 导出为 ONNX 格式
model.export(format="onnx")
```

#### 导出为 TensorRT
```python
# 导出为 TensorRT 格式 (需要 TensorRT)
model.export(format="engine")
```

### 2. 集成到项目

#### 更新检测器
```python
# 在 sorawm/watermark_detector.py 中
from ultralytics import YOLO

class WatermarkDetector:
    def __init__(self, model_path="runs/train/watermark_detector3/weights/best.pt"):
        self.model = YOLO(model_path)
    
    def detect(self, image):
        results = self.model(image)
        return results[0].boxes
```

### 3. 生产部署

#### Docker 部署
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "start_server.py"]
```

#### API 服务
```bash
# 启动 FastAPI 服务
uv run python start_server.py
```

## 性能优化

### 1. 模型优化

#### 模型压缩
```python
# 量化模型
model.export(format="onnx", int8=True)

# 剪枝模型
model.prune()
```

#### 架构优化
- 使用更小的模型 (YOLOv11n)
- 减少输入图像尺寸
- 优化网络结构

### 2. 推理优化

#### GPU 加速
```python
# 使用 GPU 推理
model = YOLO("best.pt", device="cuda")

# 批量推理
results = model(["image1.jpg", "image2.jpg"])
```

#### 内存优化
```python
# 减少批大小
model.predict(source="images/", batch=1)

# 使用半精度
model.half()
```

### 3. 数据优化

#### 数据增强
```python
# 增强训练数据
augment = True
mosaic = 1.0
mixup = 0.15
copy_paste = 0.3
```

#### 数据预处理
```python
# 优化图像尺寸
imgsz = 640  # 平衡精度和速度

# 数据缓存
cache = True  # 缓存图像到内存
```

## 故障排除

### 1. 常见问题

#### 内存不足
```bash
# 减少批大小
batch = 8  # 或更小

# 使用梯度累积
accumulate = 2
```

#### CUDA 错误
```bash
# 检查 CUDA 版本
nvidia-smi

# 重新安装 PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### 训练不收敛
```python
# 降低学习率
lr0 = 0.001

# 增加训练轮数
epochs = 200

# 检查数据质量
```

### 2. 调试技巧

#### 日志分析
```bash
# 查看训练日志
tail -f runs/train/watermark_detector/train.log

# 分析损失曲线
python -c "import matplotlib.pyplot as plt; plt.plot(losses)"
```

#### 数据检查
```bash
# 验证数据集
uv run python datasets/validate_annotations.py

# 可视化标注
uv run python datasets/visualize_annotations.py
```

### 3. 性能问题

#### 训练速度慢
- 使用更快的 GPU
- 增加批大小
- 启用数据缓存
- 使用混合精度训练

#### 推理速度慢
- 使用更小的模型
- 减少输入图像尺寸
- 使用 ONNX 或 TensorRT
- 批量处理图像

## 最佳实践

### 1. 数据准备

#### 数据质量
- 使用高质量的视频源
- 确保水印清晰可见
- 包含多样化的场景
- 平衡正负样本

#### 数据标注
- 精确标注水印边界
- 保持标注一致性
- 定期检查标注质量
- 使用多人标注验证

### 2. 训练策略

#### 超参数调优
- 从默认参数开始
- 逐步调整关键参数
- 使用验证集评估
- 记录所有实验

#### 模型选择
- 根据精度要求选择模型大小
- 考虑推理速度需求
- 平衡模型复杂度和性能
- 使用预训练模型

### 3. 评估验证

#### 交叉验证
- 使用多个数据分割
- 计算平均性能指标
- 分析性能方差
- 识别过拟合问题

#### 真实场景测试
- 在真实视频上测试
- 评估不同场景下的性能
- 收集用户反馈
- 持续改进模型

### 4. 部署维护

#### 版本控制
- 记录模型版本
- 保存训练配置
- 维护模型文档
- 建立回滚机制

#### 监控更新
- 监控模型性能
- 收集新数据
- 定期重新训练
- 更新模型版本

## 📚 参考资源

### 官方文档
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [PyTorch](https://pytorch.org/docs/)
- [OpenCV](https://docs.opencv.org/)

### 相关论文
- YOLOv11: [Ultralytics YOLOv11](https://github.com/ultralytics/ultralytics)
- Object Detection: [YOLO系列论文](https://arxiv.org/abs/1506.02640)

### 社区资源
- [YOLO 社区](https://community.ultralytics.com/)
- [PyTorch 论坛](https://discuss.pytorch.org/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/yolo)

## 🎯 总结

通过本指南，您应该能够：

1. ✅ 准备和标注训练数据
2. ✅ 配置和启动模型训练
3. ✅ 监控训练过程和性能
4. ✅ 测试和评估模型效果
5. ✅ 部署和优化模型性能

### 关键成功因素
- **数据质量**: 高质量的训练数据是成功的基础
- **参数调优**: 合理的超参数设置至关重要
- **持续监控**: 实时监控训练过程，及时调整
- **充分测试**: 在真实场景中验证模型性能
- **持续改进**: 根据反馈不断优化模型

### 下一步
- 尝试更大的模型架构
- 收集更多训练数据
- 优化推理性能
- 扩展到其他类型的水印检测

---

**祝您训练成功！** 🚀

如有问题，请参考故障排除章节或提交 Issue。

