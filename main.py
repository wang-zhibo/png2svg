from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, Response
import io
from converter import png_to_svg
from xmi_logger import XmiLogger


description = """
_________________
### 项目说明：
    PNG to SVG Converter

### 哇哈哈:
    哈哈
_________________
"""

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
    title="PNG to SVG Converter",
    docs_url="/docs",
    redoc_url="/redoc",
    description=description,
    version="0.0.1",
    )

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回简单的HTML表单，用于上传PNG文件"""
    logger.info("访问首页")
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>PNG 转 SVG 服务</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #333;
                }
                form {
                    margin: 20px 0;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 15px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <h1>PNG 转 SVG 服务</h1>
            <p>请选择一个PNG图像文件进行上传和转换：</p>
            <form action="/convert/" enctype="multipart/form-data" method="post">
                <input type="file" name="file" accept=".png">
                <button type="submit">转换</button>
            </form>
        </body>
    </html>
    """

@app.post("/convert/")
async def convert_png(file: UploadFile = File(...)):
    """将上传的PNG文件转换为SVG并返回"""
    # 检查文件类型
    if not file.filename.lower().endswith('.png'):
        logger.warning(f"用户尝试上传非PNG文件: {file.filename}")
        raise HTTPException(status_code=400, detail="只接受PNG文件")
    
    logger.info(f"开始处理文件: {file.filename}")
    
    # 读取上传的文件内容
    contents = await file.read()
    
    try:
        # 转换为SVG
        logger.info(f"开始转换文件: {file.filename}")
        svg_content = png_to_svg(contents)
        
        # 创建文件名
        output_filename = file.filename.rsplit('.', 1)[0] + '.svg'
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
async def api_convert_png(file: UploadFile = File(...)):
    """API端点，将上传的PNG文件转换为SVG并返回"""
    # 检查文件类型
    if not file.filename.lower().endswith('.png'):
        logger.warning(f"API调用: 用户尝试上传非PNG文件: {file.filename}")
        raise HTTPException(status_code=400, detail="只接受PNG文件")
    
    logger.info(f"API调用: 开始处理文件: {file.filename}")
    
    # 读取上传的文件内容
    contents = await file.read()
    
    try:
        # 转换为SVG
        logger.info(f"API调用: 开始转换文件: {file.filename}")
        svg_content = png_to_svg(contents)
        
        # 确保SVG内容是字符串
        if not isinstance(svg_content, str):
            svg_content = str(svg_content)
        
        logger.info(f"API调用: 转换成功: {file.filename}")
        
        # 返回SVG内容
        return Response(
            content=svg_content.encode('utf-8'),  # 确保内容是二进制
            media_type="image/svg+xml"
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"API转换错误: {str(e)}\n{error_details}")
        print(f"API转换错误: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"转换过程中出错: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("PNG转SVG服务启动")
    uvicorn.run(app, host="0.0.0.0", port=8000) 

