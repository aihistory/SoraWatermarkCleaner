# SoraWatermarkCleaner 标注工具文档索引

## 📚 文档概览

本文档索引整理了 SoraWatermarkCleaner 项目中标注工具相关的所有文档，包括功能说明、使用指南、测试报告等。

## 🎯 核心功能文档

### 1. 标注工具基础功能
- **LABELIMG_DOCKER_GUIDE.md** - LabelImg Docker 使用指南
- **web_annotation_tool.py** - 标准版 Web 标注工具
- **web_annotation_tool_enhanced.py** - 高精度版 Web 标注工具

### 2. 功能增强文档
- **ANNOTATION_DISPLAY_FIX.md** - 标注显示修复说明
- **DATASETS_ONLY_DIRECTORY_FIX.md** - 数据集目录限制修复
- **MULTI_LEVEL_DIRECTORY_SCAN.md** - 多级目录扫描功能
- **MULTIPLE_ANNOTATIONS_SAVE_FIX.md** - 多标注保存修复
- **AUTO_COPY_FEATURE_REPORT.md** - 自动复制功能报告
- **NULL_ERROR_FIX_REPORT.md** - 空值错误修复报告
- **UI_IMPROVEMENTS_REPORT.md** - 界面改进报告
- **IMAGE_JUMP_INSTRUCTIONS.md** - 图像跳转功能说明
- **DROPDOWN_JUMP_INSTRUCTIONS.md** - 下拉菜单跳转功能说明

### 3. 精度和测试文档
- **PRECISION_ANALYSIS_REPORT.md** - 精度分析报告
- **ANNOTATION_FIXES_REPORT.md** - 标注修复报告
- **ENHANCED_ANNOTATION_FIX_REPORT.md** - 增强版标注修复报告
- **DEBUG_STATUS_REPORT.md** - 调试状态报告

## 🛠️ 工具和脚本

### 1. 启动脚本
- **start_web_annotation.sh** - Web 标注工具启动脚本
- **start_enhanced_annotation.sh** - 增强版标注工具启动脚本
- **start_precision_tools.sh** - 精度工具启动脚本

### 2. Docker 相关脚本
- **run_labelimg_docker.sh** - LabelImg Docker 运行脚本
- **run_labelimg_docker_headless.sh** - 无头模式 LabelImg 脚本
- **setup_vnc_server.sh** - VNC 服务器设置脚本
- **run_labelimg_virtual_display.sh** - 虚拟显示 LabelImg 脚本

### 3. 测试脚本
- **test_annotation_display.py** - 标注显示测试
- **test_annotation_fixes.py** - 标注修复测试
- **test_multiple_annotations.py** - 多标注测试
- **test_enhanced_annotations.py** - 增强版标注测试
- **test_auto_copy_feature.py** - 自动复制功能测试
- **test_null_error_fix.py** - 空值错误修复测试
- **test_ui_improvements.py** - 界面改进测试
- **test_image_jump.py** - 图像跳转功能测试
- **test_dropdown_jump.py** - 下拉菜单跳转测试
- **test_page_position_fix.py** - 页面位置修复测试
- **test_page_position_keep.py** - 页面位置保持测试
- **test_button_position.py** - 按钮位置调整测试
- **test_label_position_fix.py** - 标签位置修复测试

### 4. 演示和调试工具
- **demo_web_annotation.py** - Web 标注工具演示
- **debug_annotations.html** - 标注调试页面
- **simple_test.html** - 简单测试页面
- **precision_test_tool.py** - 精度测试工具

## 📋 使用指南

### 1. 快速开始
1. 选择标注工具版本：
   - 标准版：`python3 datasets/web_annotation_tool.py --port 9090`
   - 高精度版：`python3 datasets/web_annotation_tool_enhanced.py --port 9092`

2. 访问 Web 界面：
   - 标准版：http://localhost:9090
   - 高精度版：http://localhost:9092

3. 设置目录并开始标注

### 2. 主要功能
- **目录管理**：选择图像和标签目录
- **图像浏览**：上一张/下一张/跳转功能
- **标注创建**：拖拽创建边界框
- **标注管理**：编辑、删除、复制标注
- **自动复制**：自动复制标注到下一张图像
- **数据导出**：导出标注数据

### 3. 快捷键
- **W**：创建标注框
- **A**：上一张图像
- **D**：下一张图像
- **Delete**：删除选中的标注

## 🔧 技术规格

### 1. 支持格式
- **图像格式**：JPG, PNG, BMP, GIF
- **标注格式**：YOLO 格式 (.txt)
- **类别支持**：watermark, logo, text

### 2. 系统要求
- **Python**：3.7+
- **浏览器**：Chrome, Firefox, Safari, Edge
- **操作系统**：Windows, macOS, Linux

### 3. 端口配置
- **标准版**：9090
- **高精度版**：9092

## 📊 功能对比

| 功能 | 标准版 | 高精度版 |
|------|--------|----------|
| 基础标注 | ✅ | ✅ |
| 目录管理 | ✅ | ✅ |
| 图像跳转 | ✅ | ✅ |
| 自动复制 | ✅ | ✅ |
| 精度验证 | ❌ | ✅ |
| 坐标显示 | ❌ | ✅ |
| 跨浏览器支持 | ❌ | ✅ |

## 🚨 故障排除

### 1. 常见问题
- **图像无法加载**：检查目录路径和文件权限
- **标注无法保存**：检查标签目录写入权限
- **页面显示异常**：清除浏览器缓存

### 2. 错误代码
- **404**：文件或目录不存在
- **500**：服务器内部错误
- **权限错误**：文件系统权限问题

## 📝 更新日志

### 最新更新
- ✅ 下拉菜单跳转功能
- ✅ 页面位置保持功能
- ✅ 按钮位置调整
- ✅ 自动复制标注功能
- ✅ 多标注保存修复
- ✅ 标注显示修复

### 版本历史
- **v1.0**：基础标注功能
- **v1.1**：目录管理功能
- **v1.2**：图像跳转功能
- **v1.3**：自动复制功能
- **v1.4**：界面优化
- **v1.5**：下拉菜单跳转

## 📞 支持与反馈

### 1. 问题报告
- 使用测试脚本验证功能
- 查看相关文档了解解决方案
- 检查错误日志获取详细信息

### 2. 功能请求
- 记录具体需求和使用场景
- 提供详细的描述和示例
- 考虑现有功能的扩展性

## 🔗 相关链接

- **项目主页**：SoraWatermarkCleaner
- **核心模块**：sorawm/
- **数据集**：datasets/
- **资源文件**：resources/

---

*最后更新：2024年12月*
*文档版本：v1.5*
