#!/bin/bash
# 启动增强版 Web 标注工具

echo "🌐 启动增强版 Web 标注工具"
echo "================================"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python3"
    echo "安装命令: sudo apt install python3"
    exit 1
fi

# 检查是否在项目根目录
if [ ! -f "datasets/web_annotation_tool.py" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    echo "当前目录: $(pwd)"
    echo "请切换到 SoraWatermarkCleaner 项目根目录"
    exit 1
fi

# 设置默认参数
PORT=${1:-9090}
HOST=${2:-localhost}

echo "📁 项目目录: $(pwd)"
echo "🔗 访问地址: http://$HOST:$PORT"
echo ""
echo "✨ 增强功能:"
echo "  - 📁 智能目录扫描和选择"
echo "  - 🎯 可视化标注显示"
echo "  - 🗑️ 单个/批量标注删除"
echo "  - 📊 实时统计信息"
echo "  - 📤 标注数据导出"
echo "  - ⌨️ 键盘快捷键支持"
echo "  - 📱 响应式界面设计"
echo ""
echo "💡 使用说明:"
echo "  1. 在浏览器中打开 http://$HOST:$PORT"
echo "  2. 选择图像和标签目录"
echo "  3. 点击'加载图像'开始标注"
echo "  4. 拖拽鼠标创建边界框"
echo "  5. 点击标注框进行编辑/删除"
echo ""
echo "⌨️ 快捷键:"
echo "  W - 创建边界框模式"
echo "  A - 上一张图像"
echo "  D - 下一张图像"
echo "  Del - 删除选中的标注"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================"

# 启动服务器
python3 datasets/web_annotation_tool.py --port $PORT --host $HOST --base-dir .
