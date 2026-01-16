# 水印检测模型部署指南

## 模型文件
- **最佳模型**: `runs/train/watermark_detector3/weights/best.pt`
- **最新模型**: `runs/train/watermark_detector3/weights/last.pt`

## 使用方法

### 1. 基本使用
```python
from ultralytics import YOLO

# 加载模型
model = YOLO("runs/train/watermark_detector3/weights/best.pt")

# 检测图像
results = model("path/to/image.jpg")

# 显示结果
results[0].show()
```

### 2. 批量处理
```python
# 处理多个图像
results = model(["image1.jpg", "image2.jpg", "image3.jpg"])

# 处理视频
results = model("video.mp4")
```

### 3. 集成到 SoraWatermarkCleaner
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
- **mAP50**: 检测精度指标
- **mAP50-95**: 综合精度指标
- **推理速度**: 在 GPU 上约 10-20ms/图像

## 注意事项
1. 模型需要 PyTorch 和 Ultralytics 环境
2. 建议使用 GPU 进行推理以获得最佳性能
3. 输入图像会自动调整到 640x640 尺寸
4. 检测结果包含边界框坐标和置信度

## 模型优化
- 可以导出为 ONNX 格式以提高部署效率
- 可以使用 TensorRT 进行 GPU 加速
- 可以量化模型以减少内存占用
