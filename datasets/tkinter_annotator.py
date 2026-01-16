#!/usr/bin/env python3
"""
基于 Tkinter 的标注工具
替代 LabelImg，更稳定可靠
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import cv2
from PIL import Image, ImageTk
import numpy as np

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TkinterAnnotator:
    """基于 Tkinter 的标注工具"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("水印标注工具 - Tkinter 版本")
        self.root.geometry("1200x800")
        
        # 数据
        self.images_dir = None
        self.labels_dir = None
        self.image_files = []
        self.current_index = 0
        self.annotations = []
        self.current_image = None
        self.display_image = None
        
        # 标注状态
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_bbox = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 目录选择
        ttk.Button(control_frame, text="选择图像目录", 
                  command=self.select_images_dir).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="选择标签目录", 
                  command=self.select_labels_dir).pack(side=tk.LEFT, padx=(0, 5))
        
        # 分隔符
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 导航控制
        ttk.Button(control_frame, text="上一张", 
                  command=self.prev_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="下一张", 
                  command=self.next_image).pack(side=tk.LEFT, padx=(0, 5))
        
        # 标注控制
        ttk.Button(control_frame, text="保存标注", 
                  command=self.save_annotations).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="删除标注", 
                  command=self.delete_annotation).pack(side=tk.LEFT, padx=(0, 5))
        
        # 状态信息
        self.status_var = tk.StringVar()
        self.status_var.set("请选择图像目录")
        ttk.Label(control_frame, textvariable=self.status_var).pack(side=tk.RIGHT)
        
        # 图像显示区域
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布
        self.canvas = tk.Canvas(image_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        # 绑定键盘事件
        self.root.bind("<Key>", self.on_key_press)
        self.root.focus_set()
        
        # 标注列表
        list_frame = ttk.LabelFrame(main_frame, text="标注列表")
        list_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 创建 Treeview
        columns = ('ID', 'Center X', 'Center Y', 'Width', 'Height')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_annotation_select)
    
    def select_images_dir(self):
        """选择图像目录"""
        directory = filedialog.askdirectory(title="选择图像目录")
        if directory:
            self.images_dir = Path(directory)
            self.load_image_list()
    
    def select_labels_dir(self):
        """选择标签目录"""
        directory = filedialog.askdirectory(title="选择标签目录")
        if directory:
            self.labels_dir = Path(directory)
            self.labels_dir.mkdir(exist_ok=True, parents=True)
    
    def load_image_list(self):
        """加载图像列表"""
        if not self.images_dir:
            return
        
        self.image_files = sorted(
            list(self.images_dir.glob("*.jpg")) + 
            list(self.images_dir.glob("*.png"))
        )
        
        if self.image_files:
            self.current_index = 0
            self.load_current_image()
            self.update_status()
        else:
            messagebox.showwarning("警告", "在选择的目录中没有找到图像文件")
    
    def load_current_image(self):
        """加载当前图像"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        image_path = self.image_files[self.current_index]
        
        # 加载图像
        self.current_image = cv2.imread(str(image_path))
        if self.current_image is None:
            messagebox.showerror("错误", f"无法加载图像: {image_path}")
            return
        
        # 加载标注
        self.load_annotations()
        
        # 显示图像
        self.display_image_on_canvas()
    
    def load_annotations(self):
        """加载标注"""
        self.annotations = []
        
        if not self.labels_dir or not self.image_files:
            return
        
        image_path = self.image_files[self.current_index]
        label_path = self.labels_dir / f"{image_path.stem}.txt"
        
        if label_path.exists():
            try:
                with open(label_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            parts = line.split()
                            if len(parts) == 5:
                                class_id = int(parts[0])
                                center_x = float(parts[1])
                                center_y = float(parts[2])
                                width = float(parts[3])
                                height = float(parts[4])
                                self.annotations.append((class_id, center_x, center_y, width, height))
            except Exception as e:
                messagebox.showerror("错误", f"加载标注失败: {e}")
        
        self.update_annotation_list()
    
    def display_image_on_canvas(self):
        """在画布上显示图像"""
        if self.current_image is None:
            return
        
        # 调整图像大小以适应画布
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # 画布还没有初始化，延迟显示
            self.root.after(100, self.display_image_on_canvas)
            return
        
        # 计算缩放比例
        img_height, img_width = self.current_image.shape[:2]
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        self.scale = min(scale_x, scale_y, 1.0)  # 不放大，只缩小
        
        # 缩放图像
        new_width = int(img_width * self.scale)
        new_height = int(img_height * self.scale)
        
        resized_image = cv2.resize(self.current_image, (new_width, new_height))
        
        # 转换为 PIL 图像
        rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # 转换为 Tkinter 图像
        self.display_image = ImageTk.PhotoImage(pil_image)
        
        # 清除画布并显示图像
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width//2, canvas_height//2, 
                               image=self.display_image, anchor=tk.CENTER)
        
        # 绘制标注框
        self.draw_annotations()
    
    def draw_annotations(self):
        """绘制标注框"""
        if not self.annotations or self.current_image is None:
            return
        
        img_height, img_width = self.current_image.shape[:2]
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        for i, (class_id, center_x, center_y, width, height) in enumerate(self.annotations):
            # 转换为像素坐标
            center_x_px = center_x * img_width
            center_y_px = center_y * img_height
            width_px = width * img_width
            height_px = height * img_height
            
            # 计算边界框
            x1 = center_x_px - width_px // 2
            y1 = center_y_px - height_px // 2
            x2 = center_x_px + width_px // 2
            y2 = center_y_px + height_px // 2
            
            # 缩放到画布坐标
            x1_scaled = (x1 * self.scale) + (canvas_width - img_width * self.scale) // 2
            y1_scaled = (y1 * self.scale) + (canvas_height - img_height * self.scale) // 2
            x2_scaled = (x2 * self.scale) + (canvas_width - img_width * self.scale) // 2
            y2_scaled = (y2 * self.scale) + (canvas_height - img_height * self.scale) // 2
            
            # 绘制矩形
            color = "red" if i == len(self.annotations) - 1 else "green"
            self.canvas.create_rectangle(x1_scaled, y1_scaled, x2_scaled, y2_scaled,
                                       outline=color, width=2, tags=f"bbox_{i}")
            
            # 绘制标签
            self.canvas.create_text(x1_scaled, y1_scaled - 10, text=f"watermark {i+1}",
                                  fill=color, tags=f"label_{i}")
    
    def on_mouse_press(self, event):
        """鼠标按下事件"""
        self.drawing = True
        self.start_x = event.x
        self.start_y = event.y
    
    def on_mouse_drag(self, event):
        """鼠标拖拽事件"""
        if self.drawing:
            # 删除之前的临时矩形
            self.canvas.delete("temp_bbox")
            
            # 绘制临时矩形
            self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                       outline="blue", width=2, tags="temp_bbox")
    
    def on_mouse_release(self, event):
        """鼠标释放事件"""
        if self.drawing:
            self.drawing = False
            
            # 删除临时矩形
            self.canvas.delete("temp_bbox")
            
            # 计算边界框
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)
            
            # 检查是否有足够的尺寸
            if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
                return
            
            # 转换为图像坐标
            if self.current_image is None:
                return
            
            img_height, img_width = self.current_image.shape[:2]
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 计算图像在画布中的偏移
            offset_x = (canvas_width - img_width * self.scale) // 2
            offset_y = (canvas_height - img_height * self.scale) // 2
            
            # 转换为图像坐标
            x1_img = (x1 - offset_x) / self.scale
            y1_img = (y1 - offset_y) / self.scale
            x2_img = (x2 - offset_x) / self.scale
            y2_img = (y2 - offset_y) / self.scale
            
            # 转换为 YOLO 格式
            center_x = (x1_img + x2_img) / 2 / img_width
            center_y = (y1_img + y2_img) / 2 / img_height
            width = abs(x2_img - x1_img) / img_width
            height = abs(y2_img - y1_img) / img_height
            
            # 添加到标注列表
            self.annotations.append((0, center_x, center_y, width, height))
            
            # 更新显示
            self.update_annotation_list()
            self.display_image_on_canvas()
    
    def on_key_press(self, event):
        """键盘事件"""
        if event.keysym == 'Right' or event.keysym == 'n':
            self.next_image()
        elif event.keysym == 'Left' or event.keysym == 'p':
            self.prev_image()
        elif event.keysym == 's':
            self.save_annotations()
        elif event.keysym == 'd':
            self.delete_annotation()
    
    def prev_image(self):
        """上一张图像"""
        if self.image_files and self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()
            self.update_status()
    
    def next_image(self):
        """下一张图像"""
        if self.image_files and self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_current_image()
            self.update_status()
    
    def save_annotations(self):
        """保存标注"""
        if not self.labels_dir or not self.image_files:
            messagebox.showwarning("警告", "请先选择标签目录")
            return
        
        image_path = self.image_files[self.current_index]
        label_path = self.labels_dir / f"{image_path.stem}.txt"
        
        try:
            with open(label_path, 'w') as f:
                for class_id, center_x, center_y, width, height in self.annotations:
                    f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
            
            messagebox.showinfo("成功", f"标注已保存到: {label_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def delete_annotation(self):
        """删除选中的标注"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if 0 <= index < len(self.annotations):
                del self.annotations[index]
                self.update_annotation_list()
                self.display_image_on_canvas()
    
    def on_annotation_select(self, event):
        """标注选择事件"""
        pass
    
    def update_annotation_list(self):
        """更新标注列表"""
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加标注
        for i, (class_id, center_x, center_y, width, height) in enumerate(self.annotations):
            self.tree.insert('', 'end', values=(
                i + 1,
                f"{center_x:.3f}",
                f"{center_y:.3f}",
                f"{width:.3f}",
                f"{height:.3f}"
            ))
    
    def update_status(self):
        """更新状态信息"""
        if self.image_files:
            current_file = self.image_files[self.current_index].name
            status = f"图像 {self.current_index + 1}/{len(self.image_files)}: {current_file}"
            self.status_var.set(status)
        else:
            self.status_var.set("请选择图像目录")

def main():
    """主函数"""
    root = tk.Tk()
    app = TkinterAnnotator(root)
    
    # 设置默认目录
    default_images = Path("datasets/coco8/images/train")
    default_labels = Path("datasets/coco8/labels/train")
    
    if default_images.exists():
        app.images_dir = default_images
        app.load_image_list()
    
    if default_labels.exists():
        app.labels_dir = default_labels
    
    root.mainloop()

if __name__ == "__main__":
    main()
