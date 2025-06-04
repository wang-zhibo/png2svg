from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import Optional
import io
from converter import png_to_svg, ImageToSVGConverter
from xmi_logger import XmiLogger


description = """
_________________
### 项目说明：
    高级PNG to SVG Converter - 优化版

### 功能特性:
    ✨ 支持多种阈值算法 (自适应、固定、Otsu)
    ✨ 智能边缘检测和增强
    ✨ 轮廓简化和优化
    ✨ 透明度保持
    ✨ 形态学噪点去除
    ✨ 可配置的转换参数
_________________
"""

class ConversionConfig(BaseModel):
    """转换配置模型"""
    threshold_method: str = "adaptive"  # 'fixed', 'adaptive', 'otsu'
    simplify_contours: bool = True
    min_contour_area: int = 50
    edge_detection: bool = True
    preserve_transparency: bool = True

""" 
初始化日志记录器 
可自定义: 
  - 主日志文件名 (e.g., "app_log") 
  - 日志目录 log_dir (默认 "logs") 
  - 单个日志文件体积最大值 max_size (MB) 
  - 日志保留策略 retention (e.g., "7 days") 


""" 
logger = XmiLogger( 
    file_name="app_log", 
    log_dir="logs", 
    max_size=20, 
    retention="7 days", 
)


app = FastAPI(
    title="高级PNG to SVG Converter",
    docs_url="/docs",
    redoc_url="/redoc",
    description=description,
    version="2.0.0",
    )

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回带有高级配置选项的HTML表单"""
    logger.info("访问首页")
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>高级PNG转SVG服务</title>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .form-section {
                    margin: 20px 0;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    background-color: #fafafa;
                }
                .form-section h3 {
                    margin-top: 0;
                    color: #555;
                }
                .config-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }
                .config-item {
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                }
                label {
                    font-weight: bold;
                    color: #333;
                }
                select, input[type="number"], input[type="file"] {
                    padding: 8px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 14px;
                }
                .checkbox-container {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                button {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    margin-top: 20px;
                    width: 100%;
                }
                button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                }
                .description {
                    background-color: #e8f4f8;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #3498db;
                    margin-bottom: 20px;
                }
                .help-text {
                    font-size: 12px;
                    color: #666;
                    margin-top: 3px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎨 高级PNG转SVG服务</h1>
                
                <div class="description">
                    <strong>功能特性:</strong> 智能阈值算法 • 边缘检测 • 轮廓优化 • 透明度处理 • 噪点去除
                </div>
                
                <form action="/convert/" enctype="multipart/form-data" method="post">
                    <div class="form-section">
                        <h3>📁 文件选择</h3>
                        <input type="file" name="file" accept=".png,.jpg,.jpeg" required>
                        <div class="help-text">支持PNG、JPG格式图片</div>
                    </div>
                    
                    <div class="form-section">
                        <h3>⚙️ 转换配置</h3>
                        <div class="config-grid">
                            <div class="config-item">
                                <label for="threshold_method">阈值算法:</label>
                                <select name="threshold_method" id="threshold_method">
                                    <option value="adaptive" selected>自适应阈值 (推荐)</option>
                                    <option value="otsu">Otsu自动阈值</option>
                                    <option value="fixed">固定阈值</option>
                                </select>
                                <div class="help-text">自适应阈值能更好处理光照不均的图像</div>
                            </div>
                            
                            <div class="config-item">
                                <label for="min_contour_area">最小轮廓面积:</label>
                                <input type="number" name="min_contour_area" id="min_contour_area" value="50" min="1" max="1000">
                                <div class="help-text">过滤小于此面积的轮廓，减少噪点</div>
                            </div>
                            
                            <div class="config-item">
                                <div class="checkbox-container">
                                    <input type="checkbox" name="simplify_contours" id="simplify_contours" checked>
                                    <label for="simplify_contours">简化轮廓</label>
                                </div>
                                <div class="help-text">减少路径点数，生成更小的SVG文件</div>
                            </div>
                            
                            <div class="config-item">
                                <div class="checkbox-container">
                                    <input type="checkbox" name="edge_detection" id="edge_detection" checked>
                                    <label for="edge_detection">边缘检测增强</label>
                                </div>
                                <div class="help-text">使用Canny算法增强边缘识别</div>
                            </div>
                            
                            <div class="config-item">
                                <div class="checkbox-container">
                                    <input type="checkbox" name="preserve_transparency" id="preserve_transparency" checked>
                                    <label for="preserve_transparency">保留透明度</label>
                                </div>
                                <div class="help-text">处理PNG图像的透明通道</div>
                            </div>
                        </div>
                    </div>
                    
                    <button type="submit">🚀 开始转换</button>
                </form>
                
                <div style="margin-top: 30px; text-align: center; color: #666;">
                    <small>也可以通过 <a href="/docs" target="_blank">API文档</a> 进行编程调用</small>
                </div>
            </div>
        </body>
    </html>
    """

@app.post("/convert/")
async def convert_png(
    file: UploadFile = File(...),
    threshold_method: str = Form("adaptive"),
    simplify_contours: bool = Form(True),
    min_contour_area: int = Form(50),
    edge_detection: bool = Form(True),
    preserve_transparency: bool = Form(True)
):
    """将上传的图片文件转换为SVG并返回"""
    # 检查文件类型
    if not any(file.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
        logger.warning(f"用户尝试上传不支持的文件: {file.filename}")
        raise HTTPException(status_code=400, detail="只接受PNG、JPG、JPEG文件")
    
    logger.info(f"开始处理文件: {file.filename}, 配置: {threshold_method}, 简化轮廓: {simplify_contours}")
    
    # 读取上传的文件内容
    contents = await file.read()
    
    try:
        # 构建转换参数
        config = {
            'threshold_method': threshold_method,
            'simplify_contours': simplify_contours,
            'min_contour_area': min_contour_area,
            'edge_detection': edge_detection,
            'preserve_transparency': preserve_transparency
        }
        
        # 转换为SVG
        logger.info(f"开始转换文件: {file.filename}")
        svg_content = png_to_svg(contents, **config)
        
        # 创建文件名
        base_name = file.filename.rsplit('.', 1)[0]
        output_filename = f"{base_name}_optimized.svg"
        logger.info(f"转换成功: {file.filename} -> {output_filename}")
        
        # 返回SVG文件
        return Response(
            content=svg_content.encode('utf-8'),
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"转换错误: {str(e)}\n{error_details}")
        print(f"转换错误: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"转换过程中出错: {str(e)}")

@app.post("/api/convert/", response_class=Response)
async def api_convert_png(
    file: UploadFile = File(...),
    threshold_method: str = Query("adaptive", description="阈值方法: fixed, adaptive, otsu"),
    simplify_contours: bool = Query(True, description="是否简化轮廓"),
    min_contour_area: int = Query(50, description="最小轮廓面积"),
    edge_detection: bool = Query(True, description="是否启用边缘检测"),
    preserve_transparency: bool = Query(True, description="是否保留透明度")
):
    """API端点，将上传的图片文件转换为SVG并返回"""
    # 检查文件类型
    if not any(file.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
        logger.warning(f"API调用: 用户尝试上传不支持的文件: {file.filename}")
        raise HTTPException(status_code=400, detail="只接受PNG、JPG、JPEG文件")
    
    logger.info(f"API调用: 开始处理文件: {file.filename}")
    
    # 读取上传的文件内容
    contents = await file.read()
    
    try:
        # 构建转换参数
        config = {
            'threshold_method': threshold_method,
            'simplify_contours': simplify_contours,
            'min_contour_area': min_contour_area,
            'edge_detection': edge_detection,
            'preserve_transparency': preserve_transparency
        }
        
        # 转换为SVG
        logger.info(f"API调用: 开始转换文件: {file.filename}")
        svg_content = png_to_svg(contents, **config)
        
        # 确保SVG内容是字符串
        if not isinstance(svg_content, str):
            svg_content = str(svg_content)
        
        logger.info(f"API调用: 转换成功: {file.filename}")
        
        # 返回SVG内容
        return Response(
            content=svg_content.encode('utf-8'),
            media_type="image/svg+xml"
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"API转换错误: {str(e)}\n{error_details}")
        print(f"API转换错误: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"转换过程中出错: {str(e)}")

@app.get("/config/presets")
async def get_config_presets():
    """获取预设配置"""
    presets = {
        "photo": {
            "name": "照片优化",
            "description": "适合处理照片和复杂图像",
            "config": {
                "threshold_method": "adaptive",
                "simplify_contours": True,
                "min_contour_area": 100,
                "edge_detection": True,
                "preserve_transparency": True
            }
        },
        "logo": {
            "name": "图标/Logo",
            "description": "适合处理简单的图标和Logo",
            "config": {
                "threshold_method": "otsu",
                "simplify_contours": True,
                "min_contour_area": 20,
                "edge_detection": False,
                "preserve_transparency": True
            }
        },
        "sketch": {
            "name": "手绘/素描",
            "description": "适合处理手绘图和素描",
            "config": {
                "threshold_method": "adaptive",
                "simplify_contours": False,
                "min_contour_area": 10,
                "edge_detection": True,
                "preserve_transparency": False
            }
        },
        "text": {
            "name": "文字图像",
            "description": "适合处理包含文字的图像",
            "config": {
                "threshold_method": "otsu",
                "simplify_contours": True,
                "min_contour_area": 30,
                "edge_detection": False,
                "preserve_transparency": False
            }
        }
    }
    return presets

@app.post("/api/convert/preset/{preset_name}")
async def api_convert_with_preset(
    preset_name: str,
    file: UploadFile = File(...)
):
    """使用预设配置转换图片"""
    # 获取预设配置
    presets_response = await get_config_presets()
    
    if preset_name not in presets_response:
        raise HTTPException(status_code=400, detail=f"未找到预设配置: {preset_name}")
    
    preset_config = presets_response[preset_name]["config"]
    
    # 检查文件类型
    if not any(file.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
        logger.warning(f"预设转换: 用户尝试上传不支持的文件: {file.filename}")
        raise HTTPException(status_code=400, detail="只接受PNG、JPG、JPEG文件")
    
    logger.info(f"预设转换: 使用 {preset_name} 预设处理文件: {file.filename}")
    
    # 读取上传的文件内容
    contents = await file.read()
    
    try:
        # 转换为SVG
        svg_content = png_to_svg(contents, **preset_config)
        
        logger.info(f"预设转换成功: {file.filename} 使用 {preset_name} 预设")
        
        # 返回SVG内容
        return Response(
            content=svg_content.encode('utf-8'),
            media_type="image/svg+xml"
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"预设转换错误: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"转换过程中出错: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("高级PNG转SVG服务启动")
    uvicorn.run(app, host="0.0.0.0", port=8000) 

