#!/bin/bash
# VNC 服务器设置脚本

echo "🖥️  设置 VNC 服务器用于 LabelImg"
echo "=================================="

# 检查是否已安装 VNC 服务器
if ! command -v vncserver &> /dev/null; then
    echo "📦 安装 VNC 服务器..."
    sudo apt update
    sudo apt install -y tightvncserver xfce4 xfce4-goodies
fi

# 检查是否已安装 X11 相关包
if ! dpkg -l | grep -q "x11-utils"; then
    echo "📦 安装 X11 工具..."
    sudo apt install -y x11-utils xauth
fi

# 创建 VNC 启动脚本
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
EOF

chmod +x ~/.vnc/xstartup

# 设置 VNC 密码（如果未设置）
if [ ! -f ~/.vnc/passwd ]; then
    echo "🔐 设置 VNC 密码..."
    echo "请输入 VNC 密码（用于远程连接）:"
    vncpasswd
fi

# 启动 VNC 服务器
echo "🚀 启动 VNC 服务器..."
vncserver :1 -geometry 1920x1080 -depth 24

echo "✅ VNC 服务器已启动"
echo "📱 连接信息："
echo "   - 地址: localhost:5901"
echo "   - 或使用: vncviewer localhost:1"
echo ""
echo "💡 使用方法："
echo "1. 连接到 VNC 服务器"
echo "2. 在 VNC 会话中运行: export DISPLAY=:1"
echo "3. 然后运行: bash datasets/run_labelimg_docker.sh"
echo ""
echo "🛑 停止 VNC 服务器: vncserver -kill :1"
