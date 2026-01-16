#!/bin/bash
# LabelImg Docker 无头模式运行脚本（用于服务器环境）

echo "🐳 使用 Docker 运行 LabelImg (无头模式)"
echo "========================================"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    echo "安装命令: sudo apt install docker.io"
    exit 1
fi

# 检查是否在运行
if ! docker info &> /dev/null; then
    echo "❌ Docker 服务未运行，请启动 Docker 服务"
    echo "启动命令: sudo systemctl start docker"
    exit 1
fi

# 创建临时目录用于挂载
TEMP_DIR=$(mktemp -d)
echo "📁 临时目录: $TEMP_DIR"

# 复制数据集到临时目录
echo "📋 复制数据集到临时目录..."
cp -r datasets/coco8/images/train/* "$TEMP_DIR/" 2>/dev/null || echo "⚠️  训练集目录不存在"
cp -r datasets/coco8/labels/train/* "$TEMP_DIR/" 2>/dev/null || echo "⚠️  标签目录不存在"

# 运行 LabelImg Docker 容器（无头模式）
echo "🚀 启动 LabelImg (无头模式)..."
echo "💡 注意：此模式适用于服务器环境，无法显示图形界面"
docker run --rm \
    -v "$TEMP_DIR":/data \
    -v "$(pwd)":/workspace \
    --name labelimg-headless \
    spiridonovpolytechnic/labelimg \
    /data

echo "✅ LabelImg 会话结束"
echo "📁 标注文件已保存到: $TEMP_DIR"
echo "💡 如需保存标注，请手动复制文件"
echo "💡 如需图形界面，请使用 run_labelimg_docker.sh 脚本"

