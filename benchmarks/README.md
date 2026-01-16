# 性能基准测试

这个目录包含了 SoraWatermarkCleaner 的性能基准测试工具，用于验证优化效果。

## 使用方法

### 1. 快速测试

```bash
# 运行快速性能测试
python benchmarks/performance_test.py --video resources/dog_vs_sam.mp4 --quick
```

### 2. 全面测试

```bash
# 运行全面的性能基准测试
python benchmarks/performance_test.py --video resources/dog_vs_sam.mp4 --output benchmark_results
```

## 测试配置

测试会对比以下配置的性能：

- **original_single_frame**: 原始单帧处理（基准）
- **batch_processing_default**: 默认批处理配置
- **batch_processing_small**: 小批量处理 (batch_size=4)
- **batch_processing_medium**: 中等批量处理 (batch_size=8)
- **batch_processing_large**: 大批量处理 (batch_size=16)
- **batch_processing_xlarge**: 超大批量处理 (batch_size=32)

## 性能指标

测试会测量以下指标：

- **处理速度**: FPS（帧/秒）
- **实时因子**: 相对于视频播放速度的倍数
- **内存使用**: CPU 和 GPU 内存占用
- **加速比**: 相对于基准测试的性能提升

## 输出文件

测试完成后会生成：

- `benchmark_results_YYYYMMDD_HHMMSS.json`: 详细的 JSON 格式结果
- `benchmark_results_YYYYMMDD_HHMMSS.txt`: 简化的文本报告

## 示例输出

```
SoraWatermarkCleaner 性能基准测试报告
==================================================

系统信息:
  CPU 核心数: 8
  总内存: 32.00 GB
  PyTorch 版本: 2.1.0
  GPU: NVIDIA GeForce RTX 4090
  GPU 内存: 24.00 GB

性能总结:
  基准性能: 2.50 FPS
  最佳性能: 12.30 FPS
  最佳配置: batch_processing_large
  最大加速比: 4.92x
  成功测试: 6/6

详细测试结果:
  original_single_frame:
    处理速度: 2.50 FPS
    实时因子: 0.08x
    总耗时: 120.50 秒

  batch_processing_large:
    处理速度: 12.30 FPS
    实时因子: 0.41x
    相对加速: 4.92x
    总耗时: 24.50 秒
```

## 注意事项

1. 确保有足够的磁盘空间存储测试输出视频
2. GPU 测试需要 CUDA 支持
3. 大视频文件测试可能需要较长时间
4. 建议在系统负载较低时运行测试以获得准确结果
