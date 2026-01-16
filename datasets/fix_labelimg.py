#!/usr/bin/env python3
"""
LabelImg 修复脚本
修复 PyQt5 兼容性问题
"""

import sys
import os
from pathlib import Path

def find_labelimg_path():
    """查找 LabelImg 安装路径"""
    try:
        import labelImg
        return Path(labelImg.__file__).parent
    except ImportError:
        print("❌ 未找到 labelImg 模块")
        return None

def fix_labelimg():
    """修复 LabelImg 的兼容性问题"""
    labelimg_path = find_labelimg_path()
    if not labelimg_path:
        return False
    
    labelimg_py = labelimg_path / "labelImg.py"
    if not labelimg_py.exists():
        print(f"❌ 未找到 labelImg.py: {labelimg_py}")
        return False
    
    print(f"📁 找到 LabelImg: {labelimg_py}")
    
    # 读取文件内容
    with open(labelimg_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经修复
    if "bar.setValue(int(bar.value() + bar.singleStep() * units))" in content:
        print("✅ LabelImg 已经修复过了")
        return True
    
    # 应用修复
    old_code = "bar.setValue(bar.value() + bar.singleStep() * units)"
    new_code = "bar.setValue(int(bar.value() + bar.singleStep() * units))"
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        # 备份原文件
        backup_path = labelimg_py.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 写入修复后的内容
        with open(labelimg_py, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ LabelImg 修复完成!")
        print(f"📁 备份文件: {backup_path}")
        return True
    else:
        print("⚠️  未找到需要修复的代码")
        return False

def main():
    """主函数"""
    print("🔧 LabelImg 修复工具")
    print("=" * 50)
    
    if fix_labelimg():
        print("\n🎉 修复完成! 现在可以尝试运行 labelImg")
        print("💡 如果还有问题，可以尝试:")
        print("   1. 重启终端")
        print("   2. 使用虚拟环境")
        print("   3. 降级到更早的 PyQt5 版本")
    else:
        print("\n❌ 修复失败")

if __name__ == "__main__":
    main()
