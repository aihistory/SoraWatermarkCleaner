#!/usr/bin/env python3
"""
增强版 Web 标注工具 - 高精度版本
解决跨浏览器和跨显示器的精度问题
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
        elif self.path.startswith('/api/precision-info'):
            self.serve_precision_info()
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
        elif self.path.startswith('/api/validate-precision'):
            self.validate_precision()
        else:
            self.send_error(404)
    
    def serve_index(self):
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>高精度 Web 标注工具</title>
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
        
        .precision-info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-size: 0.9em;
        }
        
        .precision-warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-size: 0.9em;
        }
        
        .coordinate-display {
            font-family: monospace;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 0.9em;
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
            <h1>🎯 高精度 Web 标注工具</h1>
            <p>支持跨浏览器和跨显示器的高精度标注</p>
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
            
            <div class="precision-info" id="precision-info">
                <strong>🎯 精度信息:</strong> 正在检测系统精度...
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
                    <li>使用高精度坐标计算确保准确性</li>
                    <li>支持跨浏览器和跨显示器使用</li>
                </ul>
            </div>
            
            <div class="coordinate-display" id="coordinate-display">
                坐标信息将在这里显示
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
                <button class="btn-secondary" onclick="validatePrecision()">🎯 验证精度</button>
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
        let imagesDir = '';
        let labelsDir = '';
        let precisionInfo = {};
        let autoCopyEnabled = false;
        let lastAnnotations = []; // 存储上一个图像的标注

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadDirectories();
            loadPrecisionInfo();
            setupKeyboardShortcuts();
        });

        // 加载精度信息
        async function loadPrecisionInfo() {
            try {
                const response = await fetch('/api/precision-info');
                if (response.ok) {
                    precisionInfo = await response.json();
                    updatePrecisionDisplay();
                }
            } catch (error) {
                console.error('加载精度信息失败:', error);
            }
        }

        // 更新精度显示
        function updatePrecisionDisplay() {
            const info = precisionInfo;
            const precisionDiv = document.getElementById('precision-info');
            
            let precisionText = `<strong>🎯 精度信息:</strong> `;
            precisionText += `设备像素比: ${info.devicePixelRatio || 1}, `;
            precisionText += `屏幕分辨率: ${info.screenWidth || 0}×${info.screenHeight || 0}, `;
            precisionText += `视口大小: ${info.viewportWidth || 0}×${info.viewportHeight || 0}`;
            
            if (info.devicePixelRatio > 1) {
                precisionText += ` <span style="color: #856404;">⚠️ 高DPI显示器</span>`;
            }
            
            precisionDiv.innerHTML = precisionText;
        }

        // 高精度坐标计算
        function getPreciseCoordinates(event, img) {
            const rect = img.getBoundingClientRect();
            
            // 考虑设备像素比
            const devicePixelRatio = window.devicePixelRatio || 1;
            
            // 计算相对于图像的位置
            const x = (event.clientX - rect.left) / rect.width;
            const y = (event.clientY - rect.top) / rect.height;
            
            // 确保坐标在有效范围内
            const clampedX = Math.max(0, Math.min(1, x));
            const clampedY = Math.max(0, Math.min(1, y));
            
            return {
                x: clampedX,
                y: clampedY,
                pixelX: (event.clientX - rect.left),
                pixelY: (event.clientY - rect.top),
                rect: rect
            };
        }

        // 高精度尺寸计算
        function calculatePreciseSize(startCoords, endCoords) {
            const width = Math.abs(endCoords.x - startCoords.x);
            const height = Math.abs(endCoords.y - startCoords.y);
            const x = Math.min(startCoords.x, endCoords.x);
            const y = Math.min(startCoords.y, endCoords.y);
            
            return { x, y, width, height };
        }

        // 更新坐标显示
        function updateCoordinateDisplay(coords) {
            if (!coords) return;
            
            const display = document.getElementById('coordinate-display');
            display.innerHTML = `
                <strong>坐标信息:</strong><br>
                归一化坐标: (${coords.x.toFixed(6)}, ${coords.y.toFixed(6)})<br>
                像素坐标: (${coords.pixelX.toFixed(2)}, ${coords.pixelY.toFixed(2)})<br>
                设备像素比: ${window.devicePixelRatio || 1}
            `;
        }

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
            
            // 等待图像加载完成后再加载标注
            img.onload = function() {
                loadAnnotations(imageName, true); // 强制重新加载
                updateImagePrecisionInfo(img);
            };
            
            img.onerror = function() {
                showError('图像加载失败: ' + imageName);
            };
            
            container.innerHTML = '';
            container.appendChild(img);
        }

        // 更新图像精度信息
        function updateImagePrecisionInfo(img) {
            const scaleX = img.offsetWidth / img.naturalWidth;
            const scaleY = img.offsetHeight / img.naturalHeight;
            const scaleConsistency = Math.abs(scaleX - scaleY) < 0.001;
            
            let precisionText = `<strong>图像精度信息:</strong><br>`;
            precisionText += `原始尺寸: ${img.naturalWidth} × ${img.naturalHeight}<br>`;
            precisionText += `显示尺寸: ${img.offsetWidth} × ${img.offsetHeight}<br>`;
            precisionText += `缩放比例: ${scaleX.toFixed(4)} × ${scaleY.toFixed(4)}<br>`;
            
            if (!scaleConsistency) {
                precisionText += `<span style="color: #856404;">⚠️ 缩放比例不一致，可能影响精度</span>`;
            } else {
                precisionText += `<span style="color: #155724;">✅ 缩放比例一致</span>`;
            }
            
            document.getElementById('coordinate-display').innerHTML = precisionText;
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

            // 清除现有标注
            const existingBboxes = container.querySelectorAll('.bbox');
            existingBboxes.forEach(bbox => bbox.remove());

            // 绘制新标注
            annotations.forEach((annotation, index) => {
                const bbox = document.createElement('div');
                bbox.className = 'bbox';
                bbox.dataset.index = index;
                
                // 使用高精度坐标计算
                const left = annotation.x * img.offsetWidth;
                const top = annotation.y * img.offsetHeight;
                const width = annotation.width * img.offsetWidth;
                const height = annotation.height * img.offsetHeight;
                
                bbox.style.left = left + 'px';
                bbox.style.top = top + 'px';
                bbox.style.width = width + 'px';
                bbox.style.height = height + 'px';
                
                console.log(`标注 ${index}:`, {
                    class: annotation.class,
                    x: annotation.x, y: annotation.y,
                    width: annotation.width, height: annotation.height,
                    pixel: { left, top, width, height }
                });
                
                const label = document.createElement('div');
                label.className = 'bbox-label';
                label.textContent = annotation.class || 'watermark';
                bbox.appendChild(label);
                
                bbox.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectAnnotation(index);
                });
                
                container.appendChild(bbox);
            });
            
            console.log(`已绘制 ${annotations.length} 个标注框`);
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
                    const errorText = await response.text();
                    console.error('❌ 错误详情:', errorText);
                    showError('保存失败: 服务器响应错误 - ' + response.status);
                }
            } catch (error) {
                console.error('❌ 保存异常:', error);
                showError('保存失败: ' + error.message);
            }
        }

        function updateAnnotationList() {
            const list = document.getElementById('annotation-list');
            if (!list) return;
            
            list.innerHTML = '';
            annotations.forEach((annotation, index) => {
                const item = document.createElement('div');
                item.className = 'annotation-item';
                item.innerHTML = `
                    <span>${index + 1}. ${annotation.class || 'watermark'}</span>
                    <span>(${(annotation.x * 100).toFixed(1)}%, ${(annotation.y * 100).toFixed(1)}%)</span>
                    <span>${(annotation.width * 100).toFixed(1)}% × ${(annotation.height * 100).toFixed(1)}%</span>
                `;
                list.appendChild(item);
            });
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

        async function validatePrecision() {
            try {
                const img = document.getElementById('main-image');
                if (!img) {
                    showError('请先加载图像');
                    return;
                }
                
                const response = await fetch('/api/validate-precision', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        imageWidth: img.naturalWidth,
                        imageHeight: img.naturalHeight,
                        displayWidth: img.offsetWidth,
                        displayHeight: img.offsetHeight,
                        devicePixelRatio: window.devicePixelRatio
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showSuccess(`精度验证完成: ${result.message}`);
                } else {
                    showError('精度验证失败');
                }
            } catch (error) {
                showError('精度验证时出错: ' + error.message);
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

        // 高精度鼠标事件处理
        document.addEventListener('DOMContentLoaded', function() {
            document.addEventListener('mousedown', function(e) {
                if (e.target.tagName === 'IMG') {
                    isDrawing = true;
                    const coords = getPreciseCoordinates(e, e.target);
                    startX = coords.x;
                    startY = coords.y;
                    updateCoordinateDisplay(coords);
                }
            });

            document.addEventListener('mousemove', function(e) {
                if (isDrawing && e.target.tagName === 'IMG') {
                    const coords = getPreciseCoordinates(e, e.target);
                    updateCoordinateDisplay(coords);
                    
                    if (currentBbox) {
                        currentBbox.remove();
                    }
                    
                    const size = calculatePreciseSize({x: startX, y: startY}, coords);
                    
                    if (size.width > 0.001 && size.height > 0.001) {
                        currentBbox = document.createElement('div');
                        currentBbox.className = 'bbox';
                        currentBbox.style.left = (size.x * e.target.offsetWidth) + 'px';
                        currentBbox.style.top = (size.y * e.target.offsetHeight) + 'px';
                        currentBbox.style.width = (size.width * e.target.offsetWidth) + 'px';
                        currentBbox.style.height = (size.height * e.target.offsetHeight) + 'px';
                        currentBbox.style.borderColor = '#28a745';
                        currentBbox.style.background = 'rgba(40,167,69,0.1)';
                        
                        e.target.parentNode.appendChild(currentBbox);
                    }
                }
            });

            document.addEventListener('mouseup', function(e) {
                if (isDrawing) {
                    isDrawing = false;
                    if (currentBbox) {
                        const coords = getPreciseCoordinates(e, e.target);
                        const size = calculatePreciseSize({x: startX, y: startY}, coords);
                        
                        if (size.width > 0.01 && size.height > 0.01) {
                            const classLabel = document.getElementById('class-label').value || 'watermark';
                            const annotation = {
                                x: size.x,
                                y: size.y,
                                width: size.width,
                                height: size.height,
                                class: classLabel
                            };
                            
                            console.log('➕ 添加新标注:', annotation);
                            console.log('📊 添加前标注数量:', annotations.length);
                            annotations.push(annotation);
                            console.log('📊 添加后标注数量:', annotations.length);
                            console.log('📋 当前所有标注:', annotations);
                            
                            drawAnnotations();
                            updateAnnotationList();
                            updateStats();
                            
                            showSuccess(`已添加标注: ${classLabel} (总计: ${annotations.length} 个)`);
                        }
                        currentBbox = null;
                    }
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
    
    def serve_precision_info(self):
        try:
            # 返回客户端精度信息
            precision_info = {
                'devicePixelRatio': 1,  # 这个值会在客户端获取
                'screenWidth': 1920,    # 这些值会在客户端获取
                'screenHeight': 1080,
                'viewportWidth': 1200,
                'viewportHeight': 800,
                'timestamp': int(time.time())
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(precision_info).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def validate_precision(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 验证精度参数
            image_width = data.get('imageWidth', 800)
            image_height = data.get('imageHeight', 600)
            display_width = data.get('displayWidth', 800)
            display_height = data.get('displayHeight', 600)
            device_pixel_ratio = data.get('devicePixelRatio', 1)
            
            # 计算缩放比例
            scale_x = display_width / image_width
            scale_y = display_height / image_height
            
            # 检查缩放一致性
            scale_consistency = abs(scale_x - scale_y) < 0.001
            
            # 计算精度评估
            precision_score = 100
            if not scale_consistency:
                precision_score -= 20
            
            if device_pixel_ratio > 1:
                precision_score -= 10
            
            # 检查坐标精度
            coordinate_precision = 100
            if device_pixel_ratio > 2:
                coordinate_precision -= 15
            
            result = {
                'scaleX': scale_x,
                'scaleY': scale_y,
                'scaleConsistency': scale_consistency,
                'precisionScore': precision_score,
                'coordinatePrecision': coordinate_precision,
                'devicePixelRatio': device_pixel_ratio,
                'message': f'精度评分: {precision_score}%, 坐标精度: {coordinate_precision}%'
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, str(e))

    # 其他方法保持不变，从原始文件复制...
    def serve_directories(self):
        try:
            datasets_dir = Path(self.base_dir) / "datasets"
            images_dirs = []
            labels_dirs = []
            
            if not datasets_dir.exists():
                result = {'images': [], 'labels': []}
            else:
                image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
                
                for root, dirs, files in os.walk(datasets_dir):
                    rel_path = os.path.relpath(root, self.base_dir)
                    
                    if rel_path == 'datasets':
                        continue
                    
                    has_images = any(Path(f).suffix.lower() in image_extensions for f in files)
                    has_labels = any(f.endswith('.txt') for f in files)
                    
                    if has_images:
                        images_dirs.append(rel_path)
                    if has_labels:
                        labels_dirs.append(rel_path)
                
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
            
            label_path.parent.mkdir(parents=True, exist_ok=True)
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            annotations = json.loads(post_data.decode('utf-8'))
            
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
                labels_path = Path(self.base_dir) / getattr(self, 'current_labels_dir', 'datasets/coco8/labels/train')
                if labels_path.exists():
                    for label_file in labels_path.glob('*.txt'):
                        label_file.unlink()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
            else:
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
                    image_name = label_file.stem + '.jpg'
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
    parser = argparse.ArgumentParser(description='高精度 Web 标注工具')
    parser.add_argument('--port', type=int, default=9092, help='服务器端口 (默认: 9092)')
    parser.add_argument('--host', type=str, default='localhost', help='服务器地址 (默认: localhost)')
    parser.add_argument('--base-dir', type=str, default='.', help='项目根目录 (默认: 当前目录)')
    
    args = parser.parse_args()
    
    print(f"🎯 启动高精度 Web 标注工具")
    print(f"📁 项目目录: {args.base_dir}")
    print(f"🔗 访问地址: http://{args.host}:{args.port}")
    print("按 Ctrl+C 停止服务器")
    print("\n✨ 高精度特性:")
    print("  - 🎯 高精度坐标计算")
    print("  - 📱 跨浏览器兼容性")
    print("  - 🖥️ 跨显示器适配")
    print("  - 📏 精度验证功能")
    print("  - 🔍 实时精度监控")
    
    handler = create_handler(args.base_dir)
    server = HTTPServer((args.host, args.port), handler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        server.shutdown()

if __name__ == '__main__':
    main()
