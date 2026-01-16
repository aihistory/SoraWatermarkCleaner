#!/bin/bash
# 使用虚拟显示运行 LabelImg

echo "🖥️  使用虚拟显示运行 LabelImg"
echo "==============================="

# 检查是否已安装 Xvfb
if ! command -v Xvfb &> /dev/null; then
    echo "📦 安装 Xvfb..."
    sudo apt update
    sudo apt install -y xvfb
fi

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 创建临时目录用于挂载
TEMP_DIR=$(mktemp -d)
echo "📁 临时目录: $TEMP_DIR"

# 复制数据集到临时目录
echo "📋 复制数据集到临时目录..."
cp -r datasets/coco8/images/train/* "$TEMP_DIR/" 2>/dev/null || echo "⚠️  训练集目录不存在"
cp -r datasets/coco8/labels/train/* "$TEMP_DIR/" 2>/dev/null || echo "⚠️  标签目录不存在"

# 启动虚拟显示
echo "🚀 启动虚拟显示..."
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &

# 等待 Xvfb 启动
sleep 2

# 运行 LabelImg Docker 容器
echo "🐳 启动 LabelImg..."
docker run --rm \
    -e DISPLAY=:99 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$TEMP_DIR":/data \
    -v "$(pwd)":/workspace \
    --name labelimg-virtual \
    spiridonovpolytechnic/labelimg \
    /data

# 清理虚拟显示
echo "🧹 清理虚拟显示..."
pkill Xvfb

echo "✅ LabelImg 会话结束"
echo "📁 标注文件已保存到: $TEMP_DIR"
echo "💡 如需保存标注，请手动复制文件"
echo "⚠️  注意：此模式无法显示图形界面，仅用于自动化处理"
