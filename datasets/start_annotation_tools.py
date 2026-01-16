#!/usr/bin/env python3
"""
标注工具启动器
提供多种标注工具选择
"""

import sys
import subprocess
from pathlib import Path

def check_tkinter():
    """检查 Tkinter 是否可用"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def check_opencv():
    """检查 OpenCV 是否可用"""
    try:
        import cv2
        return True
    except ImportError:
        return False

def run_tkinter_annotator():
    """运行 Tkinter 标注工具"""
    print("🚀 启动 Tkinter 标注工具...")
    try:
        subprocess.run([sys.executable, "datasets/tkinter_annotator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Tkinter 标注工具启动失败: {e}")
    except FileNotFoundError:
        print("❌ 未找到 Tkinter 标注工具")

def run_headless_annotator():
    """运行无GUI标注工具"""
    print("🚀 启动无GUI标注工具...")
    try:
        subprocess.run([sys.executable, "datasets/headless_annotator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 无GUI标注工具启动失败: {e}")
    except FileNotFoundError:
        print("❌ 未找到无GUI标注工具")

def run_simple_edit():
    """运行简单编辑工具"""
    print("🚀 启动简单编辑工具...")
    try:
        subprocess.run([sys.executable, "datasets/simple_edit.py", "--action", "stats"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 简单编辑工具启动失败: {e}")
    except FileNotFoundError:
        print("❌ 未找到简单编辑工具")

def show_help():
    """显示帮助信息"""
    help_text = """
🎯 水印标注工具选择指南

根据您的环境和需求选择合适的工具:

1. Tkinter 标注工具 (推荐)
   - 图形界面，操作直观
   - 支持鼠标拖拽绘制边界框
   - 需要 Tkinter 支持
   - 命令: python datasets/tkinter_annotator.py

2. 无GUI标注工具
   - 命令行交互
   - 支持手动输入坐标
   - 适合服务器环境
   - 命令: python datasets/headless_annotator.py

3. 简单编辑工具
   - 查看和统计标注
   - 无图形界面依赖
   - 命令: python datasets/simple_edit.py

4. 可视化工具
   - 生成带标注框的图像
   - 命令: python datasets/generate_visualizations.py

💡 使用建议:
- 桌面环境: 使用 Tkinter 标注工具
- 服务器环境: 使用无GUI标注工具
- 查看标注: 使用简单编辑工具
- 验证效果: 使用可视化工具
    """
    print(help_text)

def main():
    """主函数"""
    print("🎯 水印标注工具启动器")
    print("=" * 50)
    
    # 检查环境
    has_tkinter = check_tkinter()
    has_opencv = check_opencv()
    
    print(f"📋 环境检查:")
    print(f"   Tkinter: {'✅' if has_tkinter else '❌'}")
    print(f"   OpenCV:  {'✅' if has_opencv else '❌'}")
    
    if not has_opencv:
        print("❌ 缺少 OpenCV，请安装: pip install opencv-python")
        return
    
    print("\n🛠️  可用的标注工具:")
    
    tools = []
    
    if has_tkinter:
        tools.append(("1", "Tkinter 标注工具 (图形界面)", run_tkinter_annotator))
    
    tools.extend([
        ("2", "无GUI标注工具 (命令行)", run_headless_annotator),
        ("3", "简单编辑工具 (查看统计)", run_simple_edit),
        ("4", "生成可视化图像", lambda: subprocess.run([sys.executable, "datasets/generate_visualizations.py", "--split", "train", "--count", "10"])),
        ("5", "显示帮助信息", show_help),
        ("6", "退出", lambda: sys.exit(0))
    ])
    
    for num, desc, _ in tools:
        print(f"   {num}. {desc}")
    
    while True:
        try:
            choice = input(f"\n请选择工具 (1-{len(tools)}): ").strip()
            
            for num, desc, func in tools:
                if choice == num:
                    print(f"\n🎯 选择: {desc}")
                    func()
                    return
            
            print("❌ 无效选择，请重新输入")
            
        except KeyboardInterrupt:
            print("\n👋 退出")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()
