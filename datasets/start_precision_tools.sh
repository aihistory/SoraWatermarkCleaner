#!/bin/bash
# 启动精度测试和高精度标注工具

echo "🎯 Web 标注工具精度测试和优化"
echo "=================================="

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

echo "📁 项目目录: $(pwd)"
echo ""
echo "🔧 可用的精度工具:"
echo "1. 标准 Web 标注工具 (端口 9090)"
echo "2. 高精度 Web 标注工具 (端口 9092)"
echo "3. 精度测试工具 (端口 9091)"
echo ""

# 显示菜单
echo "请选择要启动的工具:"
echo "1) 标准标注工具"
echo "2) 高精度标注工具"
echo "3) 精度测试工具"
echo "4) 同时启动所有工具"
echo "5) 退出"
echo ""

read -p "请输入选择 (1-5): " choice

case $choice in
    1)
        echo "🚀 启动标准 Web 标注工具..."
        echo "🔗 访问地址: http://localhost:9090"
        echo "按 Ctrl+C 停止服务器"
        echo "================================"
        python3 datasets/web_annotation_tool.py --port 9090
        ;;
    2)
        echo "🎯 启动高精度 Web 标注工具..."
        echo "🔗 访问地址: http://localhost:9092"
        echo "按 Ctrl+C 停止服务器"
        echo "================================"
        python3 datasets/web_annotation_tool_enhanced.py --port 9092
        ;;
    3)
        echo "🧪 启动精度测试工具..."
        echo "🔗 访问地址: http://localhost:9091"
        echo "按 Ctrl+C 停止服务器"
        echo "================================"
        python3 datasets/precision_test_tool.py --port 9091
        ;;
    4)
        echo "🚀 启动所有工具..."
        echo ""
        echo "🔗 访问地址:"
        echo "  - 标准标注工具: http://localhost:9090"
        echo "  - 高精度标注工具: http://localhost:9092"
        echo "  - 精度测试工具: http://localhost:9091"
        echo ""
        echo "按 Ctrl+C 停止所有服务器"
        echo "================================"
        
        # 启动所有工具
        python3 datasets/web_annotation_tool.py --port 9090 &
        python3 datasets/web_annotation_tool_enhanced.py --port 9092 &
        python3 datasets/precision_test_tool.py --port 9091 &
        
        # 等待用户中断
        wait
        ;;
    5)
        echo "👋 退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选择，请重新运行脚本"
        exit 1
        ;;
esac
