#!/usr/bin/env python3
"""
Web 标注工具精度测试和改进工具
用于测试和验证标注精度，提供跨浏览器兼容性检查
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes

class PrecisionTestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, base_dir: str = None, **kwargs):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_precision_test()
        elif self.path.startswith('/api/test-image'):
            self.serve_test_image()
        elif self.path.startswith('/api/validate-coordinates'):
            self.serve_validation()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path.startswith('/api/validate-annotation'):
            self.validate_annotation()
        else:
            self.send_error(404)
    
    def serve_precision_test(self):
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Web 标注工具精度测试</title>
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
            max-width: 1200px; 
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
        
        .test-section {
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background: #f8f9fa;
        }
        
        .test-section h3 {
            margin-top: 0;
            color: #495057;
        }
        
        .image-container { 
            position: relative; 
            display: inline-block; 
            border: 2px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
            background: #f8f9fa;
            margin: 10px 0;
        }
        .image-container img { 
            max-width: 100%; 
            height: auto; 
            display: block;
        }
        
        .test-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .test-item {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .test-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff;
        }
        
        .test-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .precision-indicator {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .precision-excellent { background: #d4edda; color: #155724; }
        .precision-good { background: #d1ecf1; color: #0c5460; }
        .precision-fair { background: #fff3cd; color: #856404; }
        .precision-poor { background: #f8d7da; color: #721c24; }
        
        .test-controls {
            margin: 20px 0;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
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
        
        .info { 
            background: #e9ecef; 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 5px;
            border-left: 4px solid #007bff;
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
        
        .coordinate-display {
            font-family: monospace;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .test-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Web 标注工具精度测试</h1>
            <p>测试标注精度和跨浏览器兼容性</p>
        </div>
        
        <div class="content">
            <div class="test-section">
                <h3>📊 系统信息</h3>
                <div class="test-grid" id="system-info">
                    <div class="test-item">
                        <div class="test-value" id="screen-resolution">-</div>
                        <div class="test-label">屏幕分辨率</div>
                    </div>
                    <div class="test-item">
                        <div class="test-value" id="device-pixel-ratio">-</div>
                        <div class="test-label">设备像素比</div>
                    </div>
                    <div class="test-item">
                        <div class="test-value" id="browser-info">-</div>
                        <div class="test-label">浏览器信息</div>
                    </div>
                    <div class="test-item">
                        <div class="test-value" id="viewport-size">-</div>
                        <div class="test-label">视口大小</div>
                    </div>
                </div>
            </div>
            
            <div class="test-section">
                <h3>🖼️ 图像精度测试</h3>
                <div class="test-controls">
                    <button class="btn btn-primary" onclick="loadTestImage()">加载测试图像</button>
                    <button class="btn btn-success" onclick="runPrecisionTest()">运行精度测试</button>
                    <button class="btn btn-warning" onclick="validateCoordinates()">验证坐标</button>
                </div>
                
                <div class="image-container" id="test-image-container">
                    <div style="padding: 50px; text-align: center; color: #6c757d;">
                        点击"加载测试图像"开始测试
                    </div>
                </div>
                
                <div class="coordinate-display" id="coordinate-info">
                    坐标信息将在这里显示
                </div>
            </div>
            
            <div class="test-section">
                <h3>📏 精度测试结果</h3>
                <div class="test-grid" id="precision-results">
                    <div class="test-item">
                        <div class="test-value" id="coordinate-precision">-</div>
                        <div class="test-label">坐标精度</div>
                    </div>
                    <div class="test-item">
                        <div class="test-value" id="size-precision">-</div>
                        <div class="test-label">尺寸精度</div>
                    </div>
                    <div class="test-item">
                        <div class="test-value" id="overall-precision">-</div>
                        <div class="test-label">总体精度</div>
                    </div>
                    <div class="test-item">
                        <div class="test-value" id="browser-compatibility">-</div>
                        <div class="test-label">浏览器兼容性</div>
                    </div>
                </div>
            </div>
            
            <div class="test-section">
                <h3>💡 精度优化建议</h3>
                <div id="optimization-suggestions">
                    <div class="info">
                        <p><strong>运行测试后，系统将提供针对性的优化建议</strong></p>
                        <ul>
                            <li>坐标计算精度优化</li>
                            <li>跨浏览器兼容性改进</li>
                            <li>显示设备适配建议</li>
                            <li>标注工作流程优化</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let testImage = null;
        let precisionResults = {
            coordinatePrecision: 0,
            sizePrecision: 0,
            overallPrecision: 0,
            browserCompatibility: 0
        };

        // 初始化系统信息
        function initSystemInfo() {
            // 屏幕分辨率
            document.getElementById('screen-resolution').textContent = 
                `${screen.width} × ${screen.height}`;
            
            // 设备像素比
            document.getElementById('device-pixel-ratio').textContent = 
                window.devicePixelRatio || 1;
            
            // 浏览器信息
            const userAgent = navigator.userAgent;
            let browserName = 'Unknown';
            if (userAgent.includes('Chrome')) browserName = 'Chrome';
            else if (userAgent.includes('Firefox')) browserName = 'Firefox';
            else if (userAgent.includes('Safari')) browserName = 'Safari';
            else if (userAgent.includes('Edge')) browserName = 'Edge';
            
            document.getElementById('browser-info').textContent = browserName;
            
            // 视口大小
            document.getElementById('viewport-size').textContent = 
                `${window.innerWidth} × ${window.innerHeight}`;
        }

        // 加载测试图像
        async function loadTestImage() {
            try {
                const response = await fetch('/api/test-image');
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    
                    const container = document.getElementById('test-image-container');
                    container.innerHTML = `<img src="${url}" alt="Test Image" id="test-image">`;
                    
                    testImage = document.getElementById('test-image');
                    testImage.onload = function() {
                        updateCoordinateInfo();
                    };
                    
                    showSuccess('测试图像加载成功');
                } else {
                    showError('测试图像加载失败');
                }
            } catch (error) {
                showError('加载测试图像时出错: ' + error.message);
            }
        }

        // 更新坐标信息
        function updateCoordinateInfo() {
            if (!testImage) return;
            
            const info = {
                naturalWidth: testImage.naturalWidth,
                naturalHeight: testImage.naturalHeight,
                offsetWidth: testImage.offsetWidth,
                offsetHeight: testImage.offsetHeight,
                clientWidth: testImage.clientWidth,
                clientHeight: testImage.clientHeight,
                scaleX: testImage.offsetWidth / testImage.naturalWidth,
                scaleY: testImage.offsetHeight / testImage.naturalHeight
            };
            
            document.getElementById('coordinate-info').innerHTML = `
                <strong>图像尺寸信息:</strong><br>
                原始尺寸: ${info.naturalWidth} × ${info.naturalHeight}<br>
                显示尺寸: ${info.offsetWidth} × ${info.offsetHeight}<br>
                缩放比例: ${info.scaleX.toFixed(4)} × ${info.scaleY.toFixed(4)}<br>
                缩放差异: ${Math.abs(info.scaleX - info.scaleY).toFixed(6)}
            `;
        }

        // 运行精度测试
        function runPrecisionTest() {
            if (!testImage) {
                showError('请先加载测试图像');
                return;
            }
            
            // 测试坐标精度
            const coordinatePrecision = testCoordinatePrecision();
            
            // 测试尺寸精度
            const sizePrecision = testSizePrecision();
            
            // 计算总体精度
            const overallPrecision = (coordinatePrecision + sizePrecision) / 2;
            
            // 测试浏览器兼容性
            const browserCompatibility = testBrowserCompatibility();
            
            // 更新结果
            precisionResults = {
                coordinatePrecision,
                sizePrecision,
                overallPrecision,
                browserCompatibility
            };
            
            updatePrecisionResults();
            generateOptimizationSuggestions();
        }

        // 测试坐标精度
        function testCoordinatePrecision() {
            if (!testImage) return 0;
            
            // 测试鼠标坐标到归一化坐标的转换精度
            const testPoints = [
                { x: 0.1, y: 0.1 },
                { x: 0.5, y: 0.5 },
                { x: 0.9, y: 0.9 }
            ];
            
            let totalError = 0;
            let testCount = 0;
            
            testPoints.forEach(point => {
                // 模拟鼠标坐标
                const mouseX = point.x * testImage.offsetWidth;
                const mouseY = point.y * testImage.offsetHeight;
                
                // 转换回归一化坐标
                const normalizedX = mouseX / testImage.offsetWidth;
                const normalizedY = mouseY / testImage.offsetHeight;
                
                // 计算误差
                const errorX = Math.abs(normalizedX - point.x);
                const errorY = Math.abs(normalizedY - point.y);
                const error = Math.sqrt(errorX * errorX + errorY * errorY);
                
                totalError += error;
                testCount++;
            });
            
            const avgError = totalError / testCount;
            const precision = Math.max(0, 100 - (avgError * 10000)); // 转换为百分比
            
            return Math.round(precision);
        }

        // 测试尺寸精度
        function testSizePrecision() {
            if (!testImage) return 0;
            
            // 测试边界框尺寸计算精度
            const testSizes = [
                { width: 0.1, height: 0.1 },
                { width: 0.2, height: 0.2 },
                { width: 0.3, height: 0.3 }
            ];
            
            let totalError = 0;
            let testCount = 0;
            
            testSizes.forEach(size => {
                // 计算像素尺寸
                const pixelWidth = size.width * testImage.offsetWidth;
                const pixelHeight = size.height * testImage.offsetHeight;
                
                // 转换回归一化尺寸
                const normalizedWidth = pixelWidth / testImage.offsetWidth;
                const normalizedHeight = pixelHeight / testImage.offsetHeight;
                
                // 计算误差
                const errorWidth = Math.abs(normalizedWidth - size.width);
                const errorHeight = Math.abs(normalizedHeight - size.height);
                const error = Math.sqrt(errorWidth * errorWidth + errorHeight * errorHeight);
                
                totalError += error;
                testCount++;
            });
            
            const avgError = totalError / testCount;
            const precision = Math.max(0, 100 - (avgError * 10000));
            
            return Math.round(precision);
        }

        // 测试浏览器兼容性
        function testBrowserCompatibility() {
            let score = 100;
            
            // 检查关键 API 支持
            if (!window.getBoundingClientRect) score -= 20;
            if (!window.devicePixelRatio) score -= 10;
            if (!window.requestAnimationFrame) score -= 10;
            
            // 检查事件支持
            if (!document.addEventListener) score -= 15;
            if (!window.addEventListener) score -= 15;
            
            // 检查图像处理支持
            if (!document.createElement) score -= 10;
            if (!URL.createObjectURL) score -= 10;
            if (!Blob) score -= 10;
            
            return Math.max(0, score);
        }

        // 更新精度结果显示
        function updatePrecisionResults() {
            document.getElementById('coordinate-precision').innerHTML = 
                `${precisionResults.coordinatePrecision}% <span class="precision-indicator ${getPrecisionClass(precisionResults.coordinatePrecision)}">${getPrecisionLabel(precisionResults.coordinatePrecision)}</span>`;
            
            document.getElementById('size-precision').innerHTML = 
                `${precisionResults.sizePrecision}% <span class="precision-indicator ${getPrecisionClass(precisionResults.sizePrecision)}">${getPrecisionLabel(precisionResults.sizePrecision)}</span>`;
            
            document.getElementById('overall-precision').innerHTML = 
                `${precisionResults.overallPrecision}% <span class="precision-indicator ${getPrecisionClass(precisionResults.overallPrecision)}">${getPrecisionLabel(precisionResults.overallPrecision)}</span>`;
            
            document.getElementById('browser-compatibility').innerHTML = 
                `${precisionResults.browserCompatibility}% <span class="precision-indicator ${getPrecisionClass(precisionResults.browserCompatibility)}">${getPrecisionLabel(precisionResults.browserCompatibility)}</span>`;
        }

        // 获取精度等级
        function getPrecisionClass(score) {
            if (score >= 95) return 'precision-excellent';
            if (score >= 85) return 'precision-good';
            if (score >= 70) return 'precision-fair';
            return 'precision-poor';
        }

        // 获取精度标签
        function getPrecisionLabel(score) {
            if (score >= 95) return '优秀';
            if (score >= 85) return '良好';
            if (score >= 70) return '一般';
            return '较差';
        }

        // 生成优化建议
        function generateOptimizationSuggestions() {
            const suggestions = [];
            
            if (precisionResults.coordinatePrecision < 90) {
                suggestions.push('坐标精度较低，建议使用更精确的坐标计算方法');
            }
            
            if (precisionResults.sizePrecision < 90) {
                suggestions.push('尺寸精度较低，建议优化边界框尺寸计算');
            }
            
            if (precisionResults.browserCompatibility < 95) {
                suggestions.push('浏览器兼容性有待改善，建议添加兼容性检查');
            }
            
            if (testImage && Math.abs((testImage.offsetWidth / testImage.naturalWidth) - (testImage.offsetHeight / testImage.naturalHeight)) > 0.001) {
                suggestions.push('图像缩放比例不一致，可能影响标注精度');
            }
            
            if (window.devicePixelRatio > 1) {
                suggestions.push('高DPI显示器，建议考虑像素密度对精度的影响');
            }
            
            const suggestionsHtml = suggestions.length > 0 ? 
                suggestions.map(s => `<li>${s}</li>`).join('') : 
                '<li>系统精度良好，无需特殊优化</li>';
            
            document.getElementById('optimization-suggestions').innerHTML = `
                <div class="info">
                    <p><strong>优化建议:</strong></p>
                    <ul>${suggestionsHtml}</ul>
                </div>
            `;
        }

        // 验证坐标
        async function validateCoordinates() {
            if (!testImage) {
                showError('请先加载测试图像');
                return;
            }
            
            try {
                const response = await fetch('/api/validate-coordinates', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        imageWidth: testImage.naturalWidth,
                        imageHeight: testImage.naturalHeight,
                        displayWidth: testImage.offsetWidth,
                        displayHeight: testImage.offsetHeight,
                        devicePixelRatio: window.devicePixelRatio
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showSuccess('坐标验证完成: ' + result.message);
                } else {
                    showError('坐标验证失败');
                }
            } catch (error) {
                showError('坐标验证时出错: ' + error.message);
            }
        }

        function showError(message) {
            const existing = document.querySelector('.error');
            if (existing) existing.remove();
            
            const error = document.createElement('div');
            error.className = 'error';
            error.textContent = message;
            document.querySelector('.content').insertBefore(error, document.querySelector('.test-section').nextSibling);
            
            setTimeout(() => error.remove(), 5000);
        }

        function showSuccess(message) {
            const existing = document.querySelector('.success');
            if (existing) existing.remove();
            
            const success = document.createElement('div');
            success.className = 'success';
            success.textContent = message;
            document.querySelector('.content').insertBefore(success, document.querySelector('.test-section').nextSibling);
            
            setTimeout(() => success.remove(), 3000);
        }

        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {
            initSystemInfo();
        });
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_test_image(self):
        try:
            # 创建一个测试图像（简单的网格图像）
            from PIL import Image, ImageDraw
            import io
            
            # 创建 800x600 的测试图像
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # 绘制网格
            for i in range(0, 800, 50):
                draw.line([(i, 0), (i, 600)], fill='lightgray', width=1)
            for i in range(0, 600, 50):
                draw.line([(0, i), (800, i)], fill='lightgray', width=1)
            
            # 绘制一些测试标记
            test_points = [
                (100, 100, 'A'),
                (400, 300, 'B'),
                (700, 500, 'C')
            ]
            
            for x, y, label in test_points:
                draw.ellipse([x-10, y-10, x+10, y+10], fill='red', outline='darkred', width=2)
                draw.text((x+15, y-10), label, fill='black')
            
            # 转换为字节流
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.send_header('Content-Length', str(len(img_byte_arr)))
            self.end_headers()
            self.wfile.write(img_byte_arr)
            
        except ImportError:
            # 如果没有 PIL，返回一个简单的占位图像
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            svg = '''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
                <rect width="800" height="600" fill="white"/>
                <text x="400" y="300" text-anchor="middle" font-size="24" fill="black">测试图像</text>
            </svg>'''
            self.wfile.write(svg.encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_validation(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 验证坐标计算
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
            
            result = {
                'scaleX': scale_x,
                'scaleY': scale_y,
                'scaleConsistency': scale_consistency,
                'precisionScore': precision_score,
                'message': f'缩放比例: {scale_x:.4f} × {scale_y:.4f}, 精度评分: {precision_score}%'
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, str(e))

def create_handler(base_dir):
    def handler(*args, **kwargs):
        return PrecisionTestHandler(*args, base_dir=base_dir, **kwargs)
    return handler

def main():
    parser = argparse.ArgumentParser(description='Web 标注工具精度测试工具')
    parser.add_argument('--port', type=int, default=9091, help='服务器端口 (默认: 9091)')
    parser.add_argument('--host', type=str, default='localhost', help='服务器地址 (默认: localhost)')
    parser.add_argument('--base-dir', type=str, default='.', help='项目根目录 (默认: 当前目录)')
    
    args = parser.parse_args()
    
    print(f"🎯 启动 Web 标注工具精度测试")
    print(f"📁 项目目录: {args.base_dir}")
    print(f"🔗 访问地址: http://{args.host}:{args.port}")
    print("按 Ctrl+C 停止服务器")
    print("\n✨ 测试功能:")
    print("  - 📊 系统信息检测")
    print("  - 🖼️ 图像精度测试")
    print("  - 📏 坐标精度验证")
    print("  - 🌐 浏览器兼容性检查")
    print("  - 💡 优化建议生成")
    
    handler = create_handler(args.base_dir)
    server = HTTPServer((args.host, args.port), handler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        server.shutdown()

if __name__ == '__main__':
    main()
