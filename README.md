# PNG 转 SVG 转换服务

这是一个使用 Python FastAPI 构建的 Web 服务，用于将 PNG 图像文件转换为 SVG 格式。

## 功能特性

*   通过 Web 界面上传 PNG 文件。
*   将 PNG 图像转换为 SVG 格式。
*   提供 API 端点 (`/api/convert/`) 用于程序化转换。
*   使用 OpenCV 进行图像处理和轮廓检测。
*   自动生成 API 文档 (Swagger UI 和 ReDoc)。
*   使用 XmiLogger 进行日志记录。

## 技术栈

*   **Web 框架**: FastAPI
*   **ASGI 服务器**: Uvicorn
*   **图像处理**: Pillow, OpenCV-Python, NumPy
*   **日志**: XmiLogger (假设这是一个自定义或第三方库)

## 安装

1.  **克隆仓库** (如果适用):
    ```bash
    git clone <your-repo-url>
    cd png2svg
    ```

2.  **创建虚拟环境** (推荐):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate  # Windows
    ```

3.  **安装依赖**:
    确保您已安装 `potrace` (如果使用基于 potrace 的转换器) 或 `opencv` 的系统依赖。
    在 macOS 上:
    ```bash
    brew install opencv # 如果使用 OpenCV
    # brew install potrace # 如果使用 potrace
    ```
    然后安装 Python 依赖:
    ```bash
    pip install -r requirements.txt
    ```
    *注意*: 如果 `xmi_logger` 是一个本地或私有库，请确保它在您的 Python 环境中可用。

## 使用方法

1.  **运行服务**:
    ```bash
    python3 main.py
    ```
    或者使用 Uvicorn (支持热重载):
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    服务将在 `http://localhost:8000` 上运行。

2.  **Web 界面**:
    在浏览器中打开 `http://localhost:8000`。选择一个 PNG 文件并点击“转换”按钮。转换后的 SVG 文件将自动下载。

3.  **API 端点**:
    使用 POST 请求将 PNG 文件发送到 `http://localhost:8000/api/convert/`。
    示例 (使用 curl):
    ```bash
    curl -X POST -F "file=@/path/to/your/image.png" http://localhost:8000/api/convert/ -o output.svg
    ```
    响应将是 SVG 文件的内容。

## API 文档

服务启动后，可以在以下地址访问自动生成的 API 文档：

*   **Swagger UI**: `http://localhost:8000/docs`
*   **ReDoc**: `http://localhost:8000/redoc`

## 日志

服务日志将记录在项目根目录下的 `logs` 文件夹中，文件名为 `app_log.log` (根据 `main.py` 中的 `XmiLogger` 配置)。

## 注意事项

*   转换质量取决于原始 PNG 图像的复杂度和清晰度。
*   当前实现使用基于 OpenCV 的轮廓检测和二值化，可能最适合线条图和简单图形。