#!/usr/bin/env python3
"""
标注工具启动脚本
提供多种标注工具选择
"""

import sys
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_labelimg():
    """检查 LabelImg 是否可用"""
    try:
        result = subprocess.run(['labelImg', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def start_labelimg():
    """启动 LabelImg"""
    print("🚀 启动 LabelImg...")
    print("📁 请设置:")
    print("   - 图像目录: datasets/coco8/images/train/")
    print("   - 标签目录: datasets/coco8/labels/train/")
    print("   - 格式: YOLO")
    print("   - 类别: watermark")
    
    try:
        subprocess.run(['labelImg', 'datasets/coco8/images/train/'], check=True)
    except subprocess.CalledProcessError:
        print("❌ LabelImg 启动失败")
    except FileNotFoundError:
        print("❌ 未找到 LabelImg，请先安装: pip install labelImg")

def start_simple_annotator():
    """启动简单标注工具"""
    print("🚀 启动简单标注工具...")
    try:
        subprocess.run([sys.executable, 'datasets/simple_annotator.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 简单标注工具启动失败: {e}")

def show_online_options():
    """显示在线标注选项"""
    print("\n🌐 在线标注工具选项:")
    print("1. Roboflow (https://roboflow.com/)")
    print("   - 功能强大，支持团队协作")
    print("   - 支持 YOLO 格式导出")
    print("   - 免费版本有限制")
    print()
    print("2. Label Studio (https://labelstud.io/)")
    print("   - 开源，功能丰富")
    print("   - 支持多种标注类型")
    print("   - 可本地部署")
    print()
    print("3. CVAT (https://github.com/openvinotoolkit/cvat)")
    print("   - 专业级标注工具")
    print("   - 支持视频和图像标注")
    print("   - 需要 Docker 部署")

def main():
    """主函数"""
    print("🎯 水印检测数据标注工具")
    print("=" * 50)
    
    # 检查数据集是否存在
    images_dir = Path("datasets/coco8/images/train")
    if not images_dir.exists():
        print("❌ 数据集目录不存在，请先运行:")
        print("   uv run python datasets/setup_yolo_dataset.py")
        print("   uv run python datasets/split_dataset.py")
        return
    
    image_count = len(list(images_dir.glob("*.jpg")))
    print(f"📊 找到 {image_count} 张训练图像")
    
    print("\n🛠️  可用的标注工具:")
    print("1. LabelImg (传统桌面工具)")
    print("2. 简单标注工具 (基于 OpenCV)")
    print("3. 在线标注工具推荐")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请选择标注工具 (1-4): ").strip()
            
            if choice == "1":
                if check_labelimg():
                    start_labelimg()
                else:
                    print("❌ LabelImg 不可用，尝试安装修复版本...")
                    print("正在安装 LabelImg 1.8.5...")
                    subprocess.run([sys.executable, "-m", "pip", "install", "labelImg==1.8.5"], check=True)
                    start_labelimg()
                break
                
            elif choice == "2":
                start_simple_annotator()
                break
                
            elif choice == "3":
                show_online_options()
                continue
                
            elif choice == "4":
                print("👋 退出标注工具")
                break
                
            else:
                print("❌ 无效选择，请输入 1-4")
                
        except KeyboardInterrupt:
            print("\n👋 退出标注工具")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()
