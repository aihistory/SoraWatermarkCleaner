# 训练参数配置指南

## 📋 参数分类

### 1. 基础参数

#### 必需参数
```python
# 数据集配置文件
data = "train/coco8.yaml"

# 训练轮数
epochs = 100

# 图像尺寸
imgsz = 640

# 批大小
batch = 16

# 设备
device = "cuda"  # 或 "cpu"
```

#### 推荐参数
```python
# 学习率
lr0 = 0.01

# 权重衰减
weight_decay = 0.0005

# 动量
momentum = 0.937

# 早停耐心值
patience = 20
```

### 2. 数据增强参数

#### 基础增强
```python
# 启用数据增强
augment = True

# 水平翻转
fliplr = 0.5

# 垂直翻转
flipud = 0.0

# 旋转角度
degrees = 0.0

# 平移
translate = 0.1

# 缩放
scale = 0.5
```

#### 高级增强
```python
# 马赛克增强
mosaic = 1.0

# 混合增强
mixup = 0.0

# 复制粘贴
copy_paste = 0.0

# 随机擦除
erasing = 0.4
```

### 3. 优化器参数

#### SGD 优化器
```python
# 优化器类型
optimizer = "SGD"

# 学习率
lr0 = 0.01

# 最终学习率
lrf = 0.01

# 动量
momentum = 0.937

# 权重衰减
weight_decay = 0.0005
```

#### Adam 优化器
```python
# 优化器类型
optimizer = "Adam"

# 学习率
lr0 = 0.001

# 最终学习率
lrf = 0.01

# 权重衰减
weight_decay = 0.0005
```

### 4. 损失函数参数

#### 边界框损失
```python
# 边界框损失权重
box = 7.5

# IoU 阈值
iou = 0.7
```

#### 分类损失
```python
# 分类损失权重
cls = 0.5

# 标签平滑
label_smoothing = 0.0
```

#### DFL 损失
```python
# DFL 损失权重
dfl = 1.5
```

### 5. 学习率调度参数

#### 预热参数
```python
# 预热轮数
warmup_epochs = 3

# 预热动量
warmup_momentum = 0.8

# 预热偏置学习率
warmup_bias_lr = 0.1
```

#### 衰减参数
```python
# 余弦学习率
cos_lr = False

# 学习率衰减因子
lrf = 0.01
```

## 🎯 参数调优策略

### 1. 根据硬件调整

#### GPU 内存 < 8GB
```python
batch = 8
imgsz = 640
cache = False
workers = 4
```

#### GPU 内存 8-16GB
```python
batch = 16
imgsz = 640
cache = True
workers = 8
```

#### GPU 内存 > 16GB
```python
batch = 32
imgsz = 640
cache = True
workers = 16
```

### 2. 根据数据集调整

#### 小数据集 (< 1000 张)
```python
epochs = 200
lr0 = 0.01
patience = 50
augment = True
mosaic = 1.0
```

#### 中等数据集 (1000-5000 张)
```python
epochs = 100
lr0 = 0.01
patience = 20
augment = True
mosaic = 0.5
```

#### 大数据集 (> 5000 张)
```python
epochs = 50
lr0 = 0.005
patience = 10
augment = True
mosaic = 0.0
```

### 3. 根据精度要求调整

#### 高精度要求
```python
epochs = 200
lr0 = 0.005
patience = 50
augment = True
mosaic = 1.0
mixup = 0.15
```

#### 平衡精度和速度
```python
epochs = 100
lr0 = 0.01
patience = 20
augment = True
mosaic = 0.5
```

#### 快速训练
```python
epochs = 50
lr0 = 0.02
patience = 10
augment = False
mosaic = 0.0
```

## 📊 参数配置模板

### 模板 1: 快速训练
```python
# 适合快速验证和测试
config = {
    "epochs": 50,
    "batch": 16,
    "imgsz": 640,
    "lr0": 0.02,
    "patience": 10,
    "augment": False,
    "mosaic": 0.0,
    "cache": False
}
```

### 模板 2: 标准训练
```python
# 适合大多数情况
config = {
    "epochs": 100,
    "batch": 16,
    "imgsz": 640,
    "lr0": 0.01,
    "patience": 20,
    "augment": True,
    "mosaic": 0.5,
    "cache": True
}
```

### 模板 3: 高精度训练
```python
# 适合追求最高精度
config = {
    "epochs": 200,
    "batch": 16,
    "imgsz": 640,
    "lr0": 0.005,
    "patience": 50,
    "augment": True,
    "mosaic": 1.0,
    "mixup": 0.15,
    "cache": True
}
```

### 模板 4: 大数据集训练
```python
# 适合大数据集
config = {
    "epochs": 50,
    "batch": 32,
    "imgsz": 640,
    "lr0": 0.005,
    "patience": 10,
    "augment": True,
    "mosaic": 0.0,
    "cache": True,
    "workers": 16
}
```

## 🔧 参数调优流程

### 1. 基线配置
```python
# 从默认配置开始
baseline_config = {
    "epochs": 100,
    "batch": 16,
    "imgsz": 640,
    "lr0": 0.01,
    "patience": 20
}
```

### 2. 逐步调优

#### 第一步: 调整学习率
```python
# 尝试不同学习率
learning_rates = [0.005, 0.01, 0.02, 0.05]

for lr in learning_rates:
    config = baseline_config.copy()
    config["lr0"] = lr
    # 运行训练并记录结果
```

#### 第二步: 调整批大小
```python
# 尝试不同批大小
batch_sizes = [8, 16, 32, 64]

for batch in batch_sizes:
    config = baseline_config.copy()
    config["batch"] = batch
    # 运行训练并记录结果
```

#### 第三步: 调整数据增强
```python
# 尝试不同增强策略
augment_configs = [
    {"augment": False, "mosaic": 0.0},
    {"augment": True, "mosaic": 0.5},
    {"augment": True, "mosaic": 1.0, "mixup": 0.15}
]

for aug_config in augment_configs:
    config = baseline_config.copy()
    config.update(aug_config)
    # 运行训练并记录结果
```

### 3. 网格搜索
```python
# 使用网格搜索找到最佳参数组合
from itertools import product

param_grid = {
    "lr0": [0.005, 0.01, 0.02],
    "batch": [8, 16, 32],
    "epochs": [50, 100, 200]
}

best_score = 0
best_config = None

for params in product(*param_grid.values()):
    config = dict(zip(param_grid.keys(), params))
    # 运行训练
    score = train_and_evaluate(config)
    
    if score > best_score:
        best_score = score
        best_config = config
```

## 📈 性能监控

### 1. 关键指标
```python
# 监控这些指标
metrics = {
    "train_loss": "训练损失",
    "val_loss": "验证损失",
    "mAP50": "平均精度 (IoU=0.5)",
    "mAP50-95": "平均精度 (IoU=0.5-0.95)",
    "precision": "精确率",
    "recall": "召回率"
}
```

### 2. 早停策略
```python
# 配置早停
early_stopping = {
    "patience": 20,        # 耐心值
    "min_delta": 0.001,    # 最小改善
    "monitor": "val_loss", # 监控指标
    "mode": "min"          # 最小化模式
}
```

### 3. 学习率调度
```python
# 学习率调度策略
lr_scheduler = {
    "type": "cosine",      # 余弦退火
    "T_max": 100,          # 最大轮数
    "eta_min": 0.0001      # 最小学习率
}
```

## 🎯 最佳实践

### 1. 参数选择原则
- **学习率**: 从 0.01 开始，根据收敛情况调整
- **批大小**: 根据 GPU 内存选择，通常 16-32
- **训练轮数**: 根据数据集大小，通常 50-200
- **数据增强**: 小数据集使用强增强，大数据集使用弱增强

### 2. 调优顺序
1. 首先确定基础参数 (学习率、批大小)
2. 然后调整训练轮数和早停
3. 最后优化数据增强策略
4. 进行细粒度调优

### 3. 避免过拟合
```python
# 防止过拟合的参数
anti_overfitting = {
    "weight_decay": 0.0005,    # 权重衰减
    "dropout": 0.0,            # Dropout
    "label_smoothing": 0.0,    # 标签平滑
    "patience": 20             # 早停
}
```

### 4. 加速训练
```python
# 加速训练的参数
speed_up = {
    "cache": True,             # 缓存数据
    "workers": 8,              # 数据加载线程
    "amp": True,               # 混合精度
    "compile": False           # 模型编译
}
```

## 📚 参考资源

### 官方文档
- [Ultralytics 参数文档](https://docs.ultralytics.com/usage/cfg/)
- [YOLO 训练参数](https://docs.ultralytics.com/modes/train/)

### 论文参考
- [YOLOv11 论文](https://arxiv.org/abs/2405.14458)
- [超参数优化方法](https://arxiv.org/abs/1206.2944)

### 社区资源
- [YOLO 社区论坛](https://community.ultralytics.com/)
- [GitHub Issues](https://github.com/ultralytics/ultralytics/issues)

---

**祝您调优成功！** 🚀

