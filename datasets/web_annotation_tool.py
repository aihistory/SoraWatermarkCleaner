#!/usr/bin/env python3
"""
增强版基于 Web 的图像标注工具
用于替代 LabelImg，支持在浏览器中进行图像标注
功能包括：目录选择、标注显示、删除标注、批量处理等
"""

import os
import json
import base64
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes

class EnhancedAnnotationHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, base_dir: str = None, **kwargs):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_index()
        elif self.path == '/debug':
            self.serve_debug()
        elif self.path == '/simple':
            self.serve_simple_test()
        elif self.path.startswith('/api/directories'):
            self.serve_directories()
        elif self.path.startswith('/api/images'):
            self.serve_images()
        elif self.path.startswith('/api/image/'):
            self.serve_image()
        elif self.path.startswith('/api/labels/'):
            self.serve_labels()
        elif self.path.startswith('/api/classes'):
            self.serve_classes()
        elif self.path.startswith('/api/statistics'):
            self.serve_statistics()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path.startswith('/api/save/'):
            self.save_annotations()
        elif self.path.startswith('/api/delete/'):
            self.delete_annotation()
        elif self.path.startswith('/api/set-directories'):
            self.set_directories()
        elif self.path.startswith('/api/export'):
            self.export_annotations()
        else:
            self.send_error(404)
    
    def serve_index(self):
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>增强版图像标注工具</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { margin: 0; font-size: 2em; }
        .content { padding: 20px; }
        
        .config-panel {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .config-row {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            align-items: center;
        }
        
        .config-row label {
            min-width: 120px;
            font-weight: bold;
            color: #495057;
        }
        
        .config-row select, .config-row input {
            flex: 1;
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .image-container { 
            position: relative; 
            display: inline-block; 
            border: 2px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
            background: #f8f9fa;
        }
        .image-container img { 
            max-width: 100%; 
            height: auto; 
            display: block;
        }
        .bbox { 
            position: absolute; 
            border: 2px solid #dc3545; 
            background: rgba(220,53,69,0.1); 
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .bbox:hover {
            border-color: #c82333;
            background: rgba(220,53,69,0.2);
        }
        .bbox.selected {
            border-color: #007bff;
            background: rgba(0,123,255,0.2);
        }
        .bbox-label {
            position: absolute;
            top: -20px;
            left: 0;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 2px 6px;
            font-size: 12px;
            border-radius: 3px;
            white-space: nowrap;
        }
        
        .controls { 
            margin: 20px 0; 
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }
        .controls button { 
            padding: 10px 20px; 
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .btn-primary { background: #007bff; color: white; }
        .btn-primary:hover { background: #0056b3; }
        .btn-success { background: #28a745; color: white; }
        .btn-success:hover { background: #1e7e34; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-warning:hover { background: #e0a800; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-danger:hover { background: #c82333; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-secondary:hover { background: #545b62; }
        
        .info { 
            background: #e9ecef; 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        
        .stat-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .annotation-list {
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .annotation-item {
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .annotation-item:last-child {
            border-bottom: none;
        }
        
        .copy-controls {
            display: flex;
            align-items: center;
            gap: 15px;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }
        
        .copy-switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
            cursor: pointer;
        }
        
        .copy-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        
        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .slider {
            background-color: #28a745;
        }
        
        input:checked + .slider:before {
            transform: translateX(26px);
        }
        
        .copy-label {
            margin-right: 10px;
            font-weight: 500;
            color: #495057;
            white-space: nowrap;
        }
        
        .copy-mode-select {
            padding: 5px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background: white;
            font-size: 14px;
        }
        
        .jump-controls {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            margin: 0 10px;
        }
        
        .jump-select {
            min-width: 200px;
            padding: 8px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 14px;
            background: white;
        }
        
        .jump-select:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }
        
        .annotation-info {
            flex: 1;
        }
        
        .annotation-actions {
            display: flex;
            gap: 5px;
        }
        
        .btn-sm {
            padding: 5px 10px;
            font-size: 12px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        @media (max-width: 768px) {
            .config-row {
                flex-direction: column;
                align-items: stretch;
            }
            .config-row label {
                min-width: auto;
                margin-bottom: 5px;
            }
            .controls {
                flex-direction: column;
                align-items: stretch;
            }
            .controls button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖼️ 增强版图像标注工具</h1>
            <p>支持目录选择、标注管理、批量处理等功能</p>
        </div>
        
        <div class="content">
            <div class="config-panel">
                <h3>📁 目录配置</h3>
                <div class="config-row">
                    <label>图像目录:</label>
                    <select id="images-dir" onchange="updateDirectories()">
                        <option value="">选择图像目录...</option>
                    </select>
                </div>
                <div class="config-row">
                    <label>标签目录:</label>
                    <select id="labels-dir" onchange="updateDirectories()">
                        <option value="">选择标签目录...</option>
                    </select>
                </div>
                <div class="config-row">
                    <label>类别标签:</label>
                    <input type="text" id="class-label" value="watermark" placeholder="输入类别名称">
                </div>
            </div>
            
            <div class="stats-grid" id="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="total-images">0</div>
                    <div class="stat-label">总图像数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="annotated-images">0</div>
                    <div class="stat-label">已标注图像</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="total-annotations">0</div>
                    <div class="stat-label">总标注数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="current-index">0</div>
                    <div class="stat-label">当前图像</div>
                </div>
            </div>
            
            
            <div class="info">
                <p><strong>当前图像:</strong> <span id="current-image">未加载</span></p>
                <p><strong>图像路径:</strong> <span id="current-image-path">未加载</span></p>
                <p><strong>使用说明:</strong></p>
                <ul>
                    <li>选择图像和标签目录后点击"加载图像"</li>
                    <li>在图像上拖拽鼠标创建边界框</li>
                    <li>点击标注框可以选中/删除</li>
                    <li>使用键盘快捷键：W(创建框)、D(下一张)、A(上一张)、Del(删除选中)</li>
                </ul>
            </div>
            
            <div class="annotation-list" id="annotation-list">
                <div class="loading">请先加载图像</div>
            </div>
            
            <div class="controls">
                <button class="btn-primary" onclick="loadImages()">📁 加载图像</button>
                <button class="btn-secondary" onclick="prevImage()">⬅️ 上一张</button>
                <button class="btn-secondary" onclick="nextImage()">➡️ 下一张</button>
                <div class="jump-controls">
                    <select id="jump-select" class="jump-select">
                        <option value="">选择图像...</option>
                    </select>
                    <button class="btn-info" onclick="jumpToSelectedImage()">🎯 跳转</button>
                </div>
                <button class="btn-success" onclick="saveAnnotations()">💾 保存标注</button>
                <button class="btn-warning" onclick="clearAnnotations()">🗑️ 清除当前</button>
                <button class="btn-danger" onclick="deleteAllAnnotations()">🗑️ 删除所有</button>
                <button class="btn-primary" onclick="exportAnnotations()">📤 导出数据</button>
            </div>
            
            <div class="copy-controls">
                <span class="copy-label">🔄 自动复制标注</span>
                <label class="copy-switch">
                    <input type="checkbox" id="auto-copy-switch" onchange="toggleAutoCopy()">
                    <span class="slider"></span>
                </label>
                <select id="copy-mode" class="copy-mode-select">
                    <option value="all">复制所有标注</option>
                    <option value="watermark">仅复制水印标注</option>
                    <option value="logo">仅复制Logo标注</option>
                    <option value="text">仅复制文本标注</option>
                </select>
            </div>
            
            <div class="image-container" id="image-container">
                <div class="loading">请先选择目录并加载图像</div>
            </div>
        </div>
    </div>

    <script>
        let images = [];
        let currentIndex = 0;
        let annotations = [];
        let isDrawing = false;
        let startX, startY, currentBbox = null;
        let selectedAnnotation = null;
        let autoCopyEnabled = false;
        let lastAnnotations = []; // 存储上一个图像的标注
        let imagesDir = '';
        let labelsDir = '';

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadDirectories();
            setupKeyboardShortcuts();
        });

        async function loadDirectories() {
            try {
                const response = await fetch('/api/directories');
                const dirs = await response.json();
                
                const imagesSelect = document.getElementById('images-dir');
                const labelsSelect = document.getElementById('labels-dir');
                
                imagesSelect.innerHTML = '<option value="">选择图像目录...</option>';
                labelsSelect.innerHTML = '<option value="">选择标签目录...</option>';
                
                dirs.images.forEach(dir => {
                    const option = document.createElement('option');
                    option.value = dir;
                    option.textContent = dir;
                    imagesSelect.appendChild(option);
                });
                
                dirs.labels.forEach(dir => {
                    const option = document.createElement('option');
                    option.value = dir;
                    option.textContent = dir;
                    labelsSelect.appendChild(option);
                });
            } catch (error) {
                showError('加载目录失败: ' + error.message);
            }
        }

        function updateDirectories() {
            imagesDir = document.getElementById('images-dir').value;
            labelsDir = document.getElementById('labels-dir').value;
            
            if (imagesDir && labelsDir) {
                setDirectories();
            }
        }

        async function setDirectories() {
            try {
                await fetch('/api/set-directories', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        images_dir: imagesDir,
                        labels_dir: labelsDir
                    })
                });
            } catch (error) {
                showError('设置目录失败: ' + error.message);
            }
        }

        async function loadImages() {
            if (!imagesDir || !labelsDir) {
                showError('请先选择图像和标签目录');
                return;
            }
            
            try {
                showLoading('加载图像中...');
                const response = await fetch('/api/images');
                images = await response.json();
                
                if (images.length === 0) {
                    showError('所选目录中没有找到图像文件');
                    return;
                }
                
                updateStats();
                loadCurrentImage();
                updateJumpSelect();
                showSuccess(`成功加载 ${images.length} 张图像`);
            } catch (error) {
                showError('加载图像失败: ' + error.message);
            }
        }

        function loadCurrentImage() {
            if (images.length === 0) return;
            
            const imageName = images[currentIndex];
            
            // 安全地设置元素内容，避免null错误
            const currentImageElement = document.getElementById('current-image');
            const currentIndexElement = document.getElementById('current-index');
            const currentImagePathElement = document.getElementById('current-image-path');
            
            if (currentImageElement) {
                currentImageElement.textContent = imageName;
            } else {
                console.warn('current-image 元素未找到');
            }
            
            if (currentIndexElement) {
                currentIndexElement.textContent = currentIndex + 1;
            } else {
                console.warn('current-index 元素未找到');
            }
            
            if (currentImagePathElement) {
                const fullPath = `${imagesDir}/${imageName}`;
                currentImagePathElement.textContent = fullPath;
            } else {
                console.warn('current-image-path 元素未找到');
            }
            
            const container = document.getElementById('image-container');
            const img = document.createElement('img');
            img.src = `/api/image/${imageName}`;
            img.alt = imageName;
            img.id = 'main-image';
            
            // 等待图像加载完成后再加载标注（强制重新加载）
            img.onload = function() {
                loadAnnotations(imageName, true); // 强制重新加载
            };
            
            img.onerror = function() {
                showError('图像加载失败: ' + imageName);
            };
            
            container.innerHTML = '';
            container.appendChild(img);
        }

        async function loadAnnotations(imageName, forceReload = false) {
            try {
                console.log('🔄 加载标注:', imageName, '强制重新加载:', forceReload, '当前标注数量:', annotations.length);
                
                // 如果不是强制重新加载且当前已有标注，则不清空
                if (!forceReload && annotations.length > 0) {
                    console.log('✅ 保持当前标注，不重新加载');
                    drawAnnotations();
                    updateAnnotationList();
                    return;
                }
                
                const response = await fetch(`/api/labels/${imageName}`);
                console.log('📡 标注响应状态:', response.status);
                
                if (response.ok) {
                    const loadedAnnotations = await response.json();
                    console.log('📥 加载到的标注数据:', loadedAnnotations);
                    annotations = loadedAnnotations;
                    console.log('💾 设置后的标注数组:', annotations);
                    drawAnnotations();
                    updateAnnotationList();
                } else {
                    console.log('📄 标注文件不存在或无法访问');
                    if (forceReload) {
                        annotations = [];
                        console.log('🗑️ 强制重新加载，清空标注数组');
                    } else {
                        console.log('🔒 非强制重新加载，保持现有标注');
                    }
                    drawAnnotations();
                    updateAnnotationList();
                }
            } catch (error) {
                console.error('❌ 加载标注失败:', error);
                if (forceReload) {
                    annotations = [];
                    console.log('🗑️ 错误时清空标注数组');
                }
                drawAnnotations();
                updateAnnotationList();
            }
        }

        function drawAnnotations() {
            const container = document.getElementById('image-container');
            const img = document.getElementById('main-image');
            if (!img) {
                console.log('图像未加载，无法绘制标注');
                return;
            }

            console.log('绘制标注，图像尺寸:', img.offsetWidth, 'x', img.offsetHeight);
            console.log('标注数据:', annotations);

            // 清除现有标注（保留正在绘制的预览框）
            const existingBboxes = container.querySelectorAll('.bbox:not([data-preview])');
            existingBboxes.forEach(bbox => bbox.remove());

            // 绘制新标注
            annotations.forEach((annotation, index) => {
                const bbox = document.createElement('div');
                bbox.className = 'bbox';
                bbox.dataset.index = index;
                bbox.dataset.annotation = 'true';
                
                // 计算像素位置
                const left = annotation.x * img.offsetWidth;
                const top = annotation.y * img.offsetHeight;
                const width = annotation.width * img.offsetWidth;
                const height = annotation.height * img.offsetHeight;
                
                bbox.style.position = 'absolute';
                bbox.style.left = left + 'px';
                bbox.style.top = top + 'px';
                bbox.style.width = width + 'px';
                bbox.style.height = height + 'px';
                bbox.style.border = '2px solid #dc3545';
                bbox.style.background = 'rgba(220,53,69,0.1)';
                bbox.style.cursor = 'pointer';
                bbox.style.pointerEvents = 'auto';
                bbox.style.zIndex = '100';
                
                console.log(`标注 ${index}:`, {
                    class: annotation.class,
                    x: annotation.x, y: annotation.y,
                    width: annotation.width, height: annotation.height,
                    pixel: { left, top, width, height }
                });
                
                const label = document.createElement('div');
                label.className = 'bbox-label';
                label.textContent = annotation.class || 'watermark';
                label.style.position = 'absolute';
                label.style.top = '-20px';
                label.style.left = '0';
                label.style.background = 'rgba(0,0,0,0.7)';
                label.style.color = 'white';
                label.style.padding = '2px 6px';
                label.style.fontSize = '12px';
                label.style.borderRadius = '3px';
                label.style.whiteSpace = 'nowrap';
                label.style.pointerEvents = 'none';
                bbox.appendChild(label);
                
                // 添加点击事件
                bbox.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    selectAnnotation(index);
                });
                
                // 添加右键菜单
                bbox.addEventListener('contextmenu', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    showAnnotationMenu(e, index);
                });
                
                container.appendChild(bbox);
            });
            
            console.log(`已绘制 ${annotations.length} 个标注框`);
        }

        function updateAnnotationList() {
            const list = document.getElementById('annotation-list');
            if (annotations.length === 0) {
                list.innerHTML = '<div class="loading">当前图像无标注</div>';
                return;
            }
            
            list.innerHTML = annotations.map((annotation, index) => `
                <div class="annotation-item ${selectedAnnotation === index ? 'selected' : ''}">
                    <div class="annotation-info">
                        <strong>${annotation.class || 'watermark'}</strong><br>
                        <small>位置: (${(annotation.x * 100).toFixed(1)}%, ${(annotation.y * 100).toFixed(1)}%)</small><br>
                        <small>大小: ${(annotation.width * 100).toFixed(1)}% × ${(annotation.height * 100).toFixed(1)}%</small>
                    </div>
                    <div class="annotation-actions">
                        <button class="btn-sm btn-warning" onclick="editAnnotation(${index})">编辑</button>
                        <button class="btn-sm btn-danger" onclick="deleteAnnotation(${index})">删除</button>
                    </div>
                </div>
            `).join('');
        }

        function selectAnnotation(index) {
            selectedAnnotation = index;
            
            // 更新视觉选中状态
            document.querySelectorAll('.bbox').forEach((bbox, i) => {
                if (bbox.dataset.annotation === 'true') {
                    bbox.classList.toggle('selected', i === index);
                    if (i === index) {
                        bbox.style.borderColor = '#007bff';
                        bbox.style.background = 'rgba(0,123,255,0.2)';
                    } else {
                        bbox.style.borderColor = '#dc3545';
                        bbox.style.background = 'rgba(220,53,69,0.1)';
                    }
                }
            });
            
            updateAnnotationList();
        }

        function showAnnotationMenu(event, index) {
            // 移除现有菜单
            const existingMenu = document.querySelector('.annotation-menu');
            if (existingMenu) {
                existingMenu.remove();
            }
            
            // 创建右键菜单
            const menu = document.createElement('div');
            menu.className = 'annotation-menu';
            menu.style.position = 'fixed';
            menu.style.left = event.clientX + 'px';
            menu.style.top = event.clientY + 'px';
            menu.style.background = 'white';
            menu.style.border = '1px solid #ccc';
            menu.style.borderRadius = '4px';
            menu.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
            menu.style.zIndex = '10000';
            menu.style.padding = '5px 0';
            
            const menuItems = [
                { text: '编辑', action: () => editAnnotation(index) },
                { text: '删除', action: () => deleteAnnotation(index) },
                { text: '复制', action: () => copyAnnotation(index) }
            ];
            
            menuItems.forEach(item => {
                const menuItem = document.createElement('div');
                menuItem.textContent = item.text;
                menuItem.style.padding = '8px 16px';
                menuItem.style.cursor = 'pointer';
                menuItem.style.fontSize = '14px';
                menuItem.addEventListener('mouseenter', () => {
                    menuItem.style.background = '#f0f0f0';
                });
                menuItem.addEventListener('mouseleave', () => {
                    menuItem.style.background = 'white';
                });
                menuItem.addEventListener('click', () => {
                    item.action();
                    menu.remove();
                });
                menu.appendChild(menuItem);
            });
            
            document.body.appendChild(menu);
            
            // 点击其他地方关闭菜单
            setTimeout(() => {
                document.addEventListener('click', function closeMenu() {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                });
            }, 100);
        }

        function editAnnotation(index) {
            const annotation = annotations[index];
            const newClass = prompt('输入新的类别标签:', annotation.class || 'watermark');
            if (newClass !== null && newClass.trim() !== '') {
                annotations[index].class = newClass.trim();
                drawAnnotations();
                updateAnnotationList();
                showSuccess('标注已更新');
            }
        }

        function deleteAnnotation(index) {
            if (confirm('确定要删除这个标注吗？')) {
                annotations.splice(index, 1);
                selectedAnnotation = null;
                drawAnnotations();
                updateAnnotationList();
                updateStats();
                showSuccess('标注已删除');
            }
        }

        function copyAnnotation(index) {
            const annotation = annotations[index];
            const newAnnotation = {
                x: annotation.x + 0.05, // 稍微偏移
                y: annotation.y + 0.05,
                width: annotation.width,
                height: annotation.height,
                class: annotation.class
            };
            annotations.push(newAnnotation);
            drawAnnotations();
            updateAnnotationList();
            updateStats();
            showSuccess('标注已复制');
        }

        function selectAnnotation(index) {
            selectedAnnotation = index;
            
            // 更新视觉选中状态
            document.querySelectorAll('.bbox').forEach((bbox, i) => {
                bbox.classList.toggle('selected', i === index);
            });
            
            updateAnnotationList();
        }

        function deleteAnnotation(index) {
            if (confirm('确定要删除这个标注吗？')) {
                annotations.splice(index, 1);
                selectedAnnotation = null;
                drawAnnotations();
                updateAnnotationList();
                updateStats();
            }
        }

        function editAnnotation(index) {
            const newClass = prompt('输入新的类别标签:', annotations[index].class || 'watermark');
            if (newClass !== null) {
                annotations[index].class = newClass;
                drawAnnotations();
                updateAnnotationList();
            }
        }

        function prevImage() {
            if (currentIndex > 0) {
                currentIndex--;
                loadCurrentImage();
                updateStats();
                updateJumpSelect();
            }
        }

        function nextImage() {
            if (currentIndex < images.length - 1) {
                // 保存当前图像的标注用于复制
                saveCurrentAnnotations();
                
                currentIndex++;
                loadCurrentImage();
                updateStats();
                updateJumpSelect();
                
                // 自动复制标注到新图像
                setTimeout(() => {
                    copyAnnotationsToNext();
                }, 100); // 稍微延迟确保图像加载完成
            }
        }
        
        function jumpToSelectedImage() {
            const jumpSelect = document.getElementById('jump-select');
            const selectedImageName = jumpSelect.value;
            
            if (!selectedImageName) {
                showError('请选择要跳转的图像');
                return;
            }
            
            const targetIndex = images.indexOf(selectedImageName);
            if (targetIndex === -1) {
                showError('选择的图像不存在');
                return;
            }
            
            // 保存当前图像的标注用于复制
            saveCurrentAnnotations();
            
            currentIndex = targetIndex;
            loadCurrentImage();
            updateStats();
            updateJumpSelect();
            
            showSuccess(`已跳转到图像: ${selectedImageName}`);
        }
        
        function updateJumpSelect() {
            const jumpSelect = document.getElementById('jump-select');
            if (jumpSelect && images.length > 0) {
                // 保存当前选中的值
                const currentValue = jumpSelect.value;
                
                // 清空选项
                jumpSelect.innerHTML = '<option value="">选择图像...</option>';
                
                // 添加所有图像选项
                images.forEach((imageName, index) => {
                    const option = document.createElement('option');
                    option.value = imageName;
                    option.textContent = `${index + 1}. ${imageName}`;
                    if (index === currentIndex) {
                        option.selected = true;
                    }
                    jumpSelect.appendChild(option);
                });
            }
        }

        async function saveAnnotations() {
            if (images.length === 0) return;
            
            const imageName = images[currentIndex];
            console.log('💾 保存标注:', imageName, '标注数量:', annotations.length);
            console.log('📋 标注数据:', annotations);
            console.log('🔍 标注数组类型:', typeof annotations, '是否为数组:', Array.isArray(annotations));
            
            try {
                const response = await fetch(`/api/save/${imageName}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(annotations)
                });
                
                console.log('📡 保存响应状态:', response.status);
                
                if (response.ok) {
                    const result = await response.json();
                    console.log('✅ 保存成功:', result);
                    showSuccess(`标注已保存！共 ${annotations.length} 个标注`);
                    updateStats();
                } else {
                    console.error('❌ 保存失败，响应状态:', response.status);
                    showError('保存失败: 服务器响应错误');
                }
            } catch (error) {
                console.error('❌ 保存异常:', error);
                showError('保存失败: ' + error.message);
            }
        }

        function toggleAutoCopy() {
            autoCopyEnabled = document.getElementById('auto-copy-switch').checked;
            console.log('🔄 自动复制功能:', autoCopyEnabled ? '已启用' : '已禁用');
            
            if (autoCopyEnabled) {
                showSuccess('自动复制功能已启用');
            } else {
                showInfo('自动复制功能已禁用');
            }
        }
        
        function getCopyMode() {
            return document.getElementById('copy-mode').value;
        }
        
        function filterAnnotationsByMode(annotations, mode) {
            if (mode === 'all') {
                return annotations;
            }
            return annotations.filter(annotation => annotation.class === mode);
        }
        
        function copyAnnotationsToNext() {
            if (!autoCopyEnabled || lastAnnotations.length === 0) {
                return;
            }
            
            const copyMode = getCopyMode();
            const filteredAnnotations = filterAnnotationsByMode(lastAnnotations, copyMode);
            
            if (filteredAnnotations.length === 0) {
                console.log('📋 没有符合复制条件的标注');
                return;
            }
            
            // 深拷贝标注以避免引用问题
            const copiedAnnotations = filteredAnnotations.map(annotation => ({
                x: annotation.x,
                y: annotation.y,
                width: annotation.width,
                height: annotation.height,
                class: annotation.class
            }));
            
            console.log(`📋 复制 ${copiedAnnotations.length} 个标注到当前图像 (模式: ${copyMode})`);
            console.log('📋 复制的标注:', copiedAnnotations);
            
            // 将复制的标注添加到当前标注中
            annotations = [...annotations, ...copiedAnnotations];
            
            // 更新界面
            drawAnnotations();
            updateAnnotationList();
            updateStats();
            
            showSuccess(`已复制 ${copiedAnnotations.length} 个标注到当前图像`);
        }
        
        function saveCurrentAnnotations() {
            // 保存当前标注到 lastAnnotations，用于复制到下一张图像
            lastAnnotations = [...annotations];
            console.log('💾 保存当前标注用于复制:', lastAnnotations.length, '个标注');
        }

        function clearAnnotations() {
            if (annotations.length === 0) return;
            
            if (confirm('确定要清除当前图像的所有标注吗？')) {
                annotations = [];
                selectedAnnotation = null;
                drawAnnotations();
                updateAnnotationList();
                updateStats();
            }
        }

        async function deleteAllAnnotations() {
            if (images.length === 0) return;
            
            if (confirm('确定要删除所有图像的标注吗？此操作不可撤销！')) {
                try {
                    await fetch('/api/delete/all', {
                        method: 'POST'
                    });
                    showSuccess('所有标注已删除！');
                    loadCurrentImage();
                    updateStats();
                } catch (error) {
                    showError('删除失败: ' + error.message);
                }
            }
        }

        async function exportAnnotations() {
            try {
                const response = await fetch('/api/export', {
                    method: 'POST'
                });
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'annotations_export.json';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                showSuccess('标注数据已导出！');
            } catch (error) {
                showError('导出失败: ' + error.message);
            }
        }

        async function updateStats() {
            try {
                const response = await fetch('/api/statistics');
                const stats = await response.json();
                
                // 安全地设置元素内容，避免null错误
                const totalImagesElement = document.getElementById('total-images');
                const annotatedImagesElement = document.getElementById('annotated-images');
                const totalAnnotationsElement = document.getElementById('total-annotations');
                const currentIndexElement = document.getElementById('current-index');
                
                if (totalImagesElement) {
                    totalImagesElement.textContent = stats.total_images;
                }
                if (annotatedImagesElement) {
                    annotatedImagesElement.textContent = stats.annotated_images;
                }
                if (totalAnnotationsElement) {
                    totalAnnotationsElement.textContent = stats.total_annotations;
                }
                if (currentIndexElement) {
                    currentIndexElement.textContent = currentIndex + 1;
                }
            } catch (error) {
                console.error('更新统计信息失败:', error);
            }
        }

        function setupKeyboardShortcuts() {
            document.addEventListener('keydown', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
                
                switch(e.key.toLowerCase()) {
                    case 'w':
                        e.preventDefault();
                        // 开始绘制模式
                        break;
                    case 'a':
                        e.preventDefault();
                        prevImage();
                        break;
                    case 'd':
                        e.preventDefault();
                        nextImage();
                        break;
                    case 'delete':
                    case 'backspace':
                        e.preventDefault();
                        if (selectedAnnotation !== null) {
                            deleteAnnotation(selectedAnnotation);
                        }
                        break;
                }
            });
        }

        // 改进的鼠标事件处理
        document.addEventListener('DOMContentLoaded', function() {
            let currentImage = null;
            
            // 图像容器点击事件
            document.addEventListener('mousedown', function(e) {
                // 检查是否点击在图像上
                if (e.target.tagName === 'IMG' && e.target.id === 'main-image') {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    currentImage = e.target;
                    isDrawing = true;
                    
                    const rect = currentImage.getBoundingClientRect();
                    startX = (e.clientX - rect.left) / rect.width;
                    startY = (e.clientY - rect.top) / rect.height;
                    
                    console.log('开始绘制标注框:', { startX, startY });
                }
            });

            // 全局鼠标移动事件
            document.addEventListener('mousemove', function(e) {
                if (isDrawing && currentImage) {
                    e.preventDefault();
                    
                    const rect = currentImage.getBoundingClientRect();
                    const currentX = (e.clientX - rect.left) / rect.width;
                    const currentY = (e.clientY - rect.top) / rect.height;
                    
                    // 移除之前的预览框
                    if (currentBbox) {
                        currentBbox.remove();
                    }
                    
                    // 计算边界框尺寸和位置
                    const width = Math.abs(currentX - startX);
                    const height = Math.abs(currentY - startY);
                    const x = Math.min(startX, currentX);
                    const y = Math.min(startY, currentY);
                    
                    // 创建预览框
                    currentBbox = document.createElement('div');
                    currentBbox.className = 'bbox';
                    currentBbox.style.position = 'absolute';
                    currentBbox.style.left = (x * rect.width) + 'px';
                    currentBbox.style.top = (y * rect.height) + 'px';
                    currentBbox.style.width = (width * rect.width) + 'px';
                    currentBbox.style.height = (height * rect.height) + 'px';
                    currentBbox.style.border = '2px solid #28a745';
                    currentBbox.style.background = 'rgba(40,167,69,0.1)';
                    currentBbox.style.pointerEvents = 'none';
                    currentBbox.style.zIndex = '1000';
                    
                    // 添加到图像容器
                    const container = document.getElementById('image-container');
                    container.appendChild(currentBbox);
                }
            });

            // 全局鼠标释放事件
            document.addEventListener('mouseup', function(e) {
                if (isDrawing && currentImage) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    isDrawing = false;
                    
                    if (currentBbox) {
                        const rect = currentImage.getBoundingClientRect();
                        const endX = (e.clientX - rect.left) / rect.width;
                        const endY = (e.clientY - rect.top) / rect.height;
                        
                        const width = Math.abs(endX - startX);
                        const height = Math.abs(endY - startY);
                        
                        // 检查最小尺寸
                        if (width > 0.01 && height > 0.01) {
                            const classLabel = document.getElementById('class-label').value || 'watermark';
                            const annotation = {
                                x: Math.min(startX, endX),
                                y: Math.min(startY, endY),
                                width: width,
                                height: height,
                                class: classLabel
                            };
                            
                            console.log('➕ 添加新标注:', annotation);
                            console.log('📊 添加前标注数量:', annotations.length);
                            annotations.push(annotation);
                            console.log('📊 添加后标注数量:', annotations.length);
                            console.log('📋 当前所有标注:', annotations);
                            
                            // 重新绘制所有标注
                            drawAnnotations();
                            updateAnnotationList();
                            updateStats();
                            
                            showSuccess(`已添加标注: ${classLabel} (总计: ${annotations.length} 个)`);
                        }
                        
                        // 清理预览框
                        currentBbox.remove();
                        currentBbox = null;
                    }
                    
                    currentImage = null;
                }
            });
            
            // 防止在标注框上触发绘制
            document.addEventListener('mousedown', function(e) {
                if (e.target.classList.contains('bbox') || e.target.classList.contains('bbox-label')) {
                    e.stopPropagation();
                }
            });
        });

        function showLoading(message) {
            const container = document.getElementById('image-container');
            container.innerHTML = `<div class="loading">${message}</div>`;
        }

        function showError(message) {
            const existing = document.querySelector('.error');
            if (existing) existing.remove();
            
            const error = document.createElement('div');
            error.className = 'error';
            error.textContent = message;
            document.querySelector('.content').insertBefore(error, document.querySelector('.config-panel').nextSibling);
            
            setTimeout(() => error.remove(), 5000);
        }

        function showSuccess(message) {
            const existing = document.querySelector('.success');
            if (existing) existing.remove();
            
            const success = document.createElement('div');
            success.className = 'success';
            success.textContent = message;
            document.querySelector('.content').insertBefore(success, document.querySelector('.config-panel').nextSibling);
            
            setTimeout(() => success.remove(), 3000);
        }
        
        function showInfo(message) {
            const existing = document.querySelector('.info');
            if (existing) existing.remove();
            
            const info = document.createElement('div');
            info.className = 'info';
            info.textContent = message;
            document.querySelector('.content').insertBefore(info, document.querySelector('.config-panel').nextSibling);
            
            setTimeout(() => info.remove(), 3000);
        }
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_debug(self):
        try:
            debug_file = Path(self.base_dir) / "datasets" / "debug_annotations.html"
            if debug_file.exists():
                with open(debug_file, 'r', encoding='utf-8') as f:
                    html = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_error(404, "Debug page not found")
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_simple_test(self):
        try:
            simple_file = Path(self.base_dir) / "datasets" / "simple_test.html"
            if simple_file.exists():
                with open(simple_file, 'r', encoding='utf-8') as f:
                    html = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_error(404, "Simple test page not found")
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_directories(self):
        try:
            # 只扫描 datasets 目录
            datasets_dir = Path(self.base_dir) / "datasets"
            images_dirs = []
            labels_dirs = []
            
            if not datasets_dir.exists():
                # 如果 datasets 目录不存在，返回空列表
                result = {'images': [], 'labels': []}
            else:
                # 扫描 datasets 目录下的所有子目录（包括多级嵌套）
                image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
                
                # 使用 os.walk 递归遍历所有子目录
                for root, dirs, files in os.walk(datasets_dir):
                    # 获取相对路径
                    rel_path = os.path.relpath(root, self.base_dir)
                    
                    # 跳过 datasets 根目录本身
                    if rel_path == 'datasets':
                        continue
                    
                    # 检查当前目录是否包含图像文件
                    has_images = any(Path(f).suffix.lower() in image_extensions for f in files)
                    
                    # 检查当前目录是否包含标签文件
                    has_labels = any(f.endswith('.txt') for f in files)
                    
                    # 如果包含图像，添加到图像目录列表
                    if has_images:
                        images_dirs.append(rel_path)
                    
                    # 如果包含标签，添加到标签目录列表
                    if has_labels:
                        labels_dirs.append(rel_path)
                
                # 去重并排序
                result = {
                    'images': sorted(set(images_dirs)),
                    'labels': sorted(set(labels_dirs))
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_images(self):
        try:
            images_path = Path(self.base_dir) / getattr(self, 'current_images_dir', 'datasets/coco8/images/train')
            if not images_path.exists():
                self.send_error(404, "Images directory not found")
                return
            
            image_files = [f.name for f in images_path.iterdir() 
                          if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']]
            image_files.sort()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(image_files).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_image(self):
        try:
            image_name = urllib.parse.unquote(self.path.split('/')[-1])
            images_path = Path(self.base_dir) / getattr(self, 'current_images_dir', 'datasets/coco8/images/train')
            image_path = images_path / image_name
            
            if not image_path.exists():
                self.send_error(404, "Image not found")
                return
            
            # 设置正确的 MIME 类型
            mime_type, _ = mimetypes.guess_type(str(image_path))
            if not mime_type:
                mime_type = 'image/jpeg'
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.send_header('Content-Length', str(len(image_data)))
            self.end_headers()
            self.wfile.write(image_data)
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_labels(self):
        try:
            image_name = urllib.parse.unquote(self.path.split('/')[-1])
            label_name = image_name.rsplit('.', 1)[0] + '.txt'
            labels_path = Path(self.base_dir) / getattr(self, 'current_labels_dir', 'datasets/coco8/labels/train')
            label_path = labels_path / label_name
            
            if not label_path.exists():
                self.send_response(404)
                self.end_headers()
                return
            
            with open(label_path, 'r') as f:
                lines = f.readlines()
            
            annotations = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    # 将类别ID转换为类别名称
                    class_id = int(parts[0])
                    class_names = ['watermark', 'logo', 'text', 'signature', 'stamp', 'other']
                    class_name = class_names[class_id] if class_id < len(class_names) else f'class_{class_id}'
                    
                    annotations.append({
                        'class': class_name,
                        'x': float(parts[1]),
                        'y': float(parts[2]),
                        'width': float(parts[3]),
                        'height': float(parts[4])
                    })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(annotations).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_classes(self):
        # 返回预定义的类别列表
        classes = ['watermark', 'logo', 'text', 'signature', 'stamp', 'other']
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(classes).encode('utf-8'))
    
    def serve_statistics(self):
        try:
            images_path = Path(self.base_dir) / getattr(self, 'current_images_dir', 'datasets/coco8/images/train')
            labels_path = Path(self.base_dir) / getattr(self, 'current_labels_dir', 'datasets/coco8/labels/train')
            
            total_images = 0
            annotated_images = 0
            total_annotations = 0
            
            if images_path.exists():
                image_files = [f for f in images_path.iterdir() 
                              if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']]
                total_images = len(image_files)
                
                if labels_path.exists():
                    for image_file in image_files:
                        label_name = image_file.stem + '.txt'
                        label_path = labels_path / label_name
                        if label_path.exists():
                            annotated_images += 1
                            with open(label_path, 'r') as f:
                                total_annotations += len(f.readlines())
            
            stats = {
                'total_images': total_images,
                'annotated_images': annotated_images,
                'total_annotations': total_annotations
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def save_annotations(self):
        try:
            image_name = urllib.parse.unquote(self.path.split('/')[-1])
            label_name = image_name.rsplit('.', 1)[0] + '.txt'
            labels_path = Path(self.base_dir) / getattr(self, 'current_labels_dir', 'datasets/coco8/labels/train')
            label_path = labels_path / label_name
            
            # 确保标签目录存在
            label_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取请求数据
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            annotations = json.loads(post_data.decode('utf-8'))
            
            # 转换为 YOLO 格式
            with open(label_path, 'w') as f:
                for annotation in annotations:
                    f.write(f"0 {annotation['x']} {annotation['y']} {annotation['width']} {annotation['height']}\n")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def delete_annotation(self):
        try:
            if self.path.endswith('/all'):
                # 删除所有标注
                labels_path = Path(self.base_dir) / getattr(self, 'current_labels_dir', 'datasets/coco8/labels/train')
                if labels_path.exists():
                    for label_file in labels_path.glob('*.txt'):
                        label_file.unlink()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
            else:
                # 删除单个标注
                image_name = urllib.parse.unquote(self.path.split('/')[-1])
                label_name = image_name.rsplit('.', 1)[0] + '.txt'
                labels_path = Path(self.base_dir) / getattr(self, 'current_labels_dir', 'datasets/coco8/labels/train')
                label_path = labels_path / label_name
                
                if label_path.exists():
                    label_path.unlink()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def set_directories(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            self.current_images_dir = data.get('images_dir', 'datasets/coco8/images/train')
            self.current_labels_dir = data.get('labels_dir', 'datasets/coco8/labels/train')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def export_annotations(self):
        try:
            labels_path = Path(self.base_dir) / getattr(self, 'current_labels_dir', 'datasets/coco8/labels/train')
            images_path = Path(self.base_dir) / getattr(self, 'current_images_dir', 'datasets/coco8/images/train')
            
            export_data = {
                'metadata': {
                    'images_dir': str(images_path),
                    'labels_dir': str(labels_path),
                    'export_time': str(Path().cwd())
                },
                'annotations': {}
            }
            
            if labels_path.exists():
                for label_file in labels_path.glob('*.txt'):
                    image_name = label_file.stem + '.jpg'  # 假设图像是 jpg 格式
                    with open(label_file, 'r') as f:
                        lines = f.readlines()
                    
                    annotations = []
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            annotations.append({
                                'class': int(parts[0]),
                                'x': float(parts[1]),
                                'y': float(parts[2]),
                                'width': float(parts[3]),
                                'height': float(parts[4])
                            })
                    
                    export_data['annotations'][image_name] = annotations
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Disposition', 'attachment; filename="annotations_export.json"')
            self.end_headers()
            self.wfile.write(json.dumps(export_data, indent=2).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))

def create_handler(base_dir):
    def handler(*args, **kwargs):
        return EnhancedAnnotationHandler(*args, base_dir=base_dir, **kwargs)
    return handler

def main():
    parser = argparse.ArgumentParser(description='增强版基于 Web 的图像标注工具')
    parser.add_argument('--port', type=int, default=9090, help='服务器端口 (默认: 9090)')
    parser.add_argument('--host', type=str, default='localhost', help='服务器地址 (默认: localhost)')
    parser.add_argument('--base-dir', type=str, default='.', help='项目根目录 (默认: 当前目录)')
    
    args = parser.parse_args()
    
    print(f"🌐 启动增强版 Web 标注工具")
    print(f"📁 项目目录: {args.base_dir}")
    print(f"🔗 访问地址: http://{args.host}:{args.port}")
    print("按 Ctrl+C 停止服务器")
    print("\n✨ 新功能:")
    print("  - 📁 目录选择和管理")
    print("  - 🎯 标注显示和编辑")
    print("  - 🗑️ 标注删除功能")
    print("  - 📊 统计信息显示")
    print("  - 📤 数据导出功能")
    print("  - ⌨️ 键盘快捷键支持")
    
    handler = create_handler(args.base_dir)
    server = HTTPServer((args.host, args.port), handler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        server.shutdown()

if __name__ == '__main__':
    main()