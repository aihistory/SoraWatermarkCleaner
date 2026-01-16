#!/bin/bash

# 高精度 Web 标注工具启动脚本
# 解决跨浏览器和跨显示器的精度问题

echo "🎯 启动高精度 Web 标注工具"
echo "=================================="

# 检查端口是否被占用
PORT=9092
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 $PORT 已被占用"
    echo "正在尝试停止现有进程..."
    pkill -f "web_annotation_tool_enhanced.py.*--port $PORT" || true
    sleep 2
fi

# 设置工作目录
cd "$(dirname "$0")/.."

# 启动高精度标注工具
echo "🚀 启动高精度标注工具 (端口 $PORT)..."
echo "📁 工作目录: $(pwd)"
echo "🌐 访问地址: http://localhost:$PORT"
echo ""

# 启动服务器
python3 datasets/web_annotation_tool_enhanced.py --port $PORT --base-dir "$(pwd)"

echo ""
echo "✅ 高精度标注工具已停止"
