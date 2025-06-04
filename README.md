# �� 高级PNG转SVG转换服务 v2.0

这是一个使用 Python FastAPI 构建的高级 Web 服务，用于将图像文件智能转换为高质量 SVG 格式。

## ✨ 功能特性

### 🔧 智能转换算法
- **多种阈值算法**: 自适应阈值、Otsu自动阈值、固定阈值
- **边缘检测增强**: 使用Canny算法提升边缘识别准确性
- **轮廓优化**: Douglas-Peucker算法简化路径，减少文件大小
- **透明度处理**: 智能处理PNG透明通道
- **形态学降噪**: 自动去除噪点和填充孔洞

### 🎯 预设配置
- **照片优化**: 适合处理照片和复杂图像
- **图标/Logo**: 专门优化简单图标和Logo
- **手绘/素描**: 最适合手绘图和素描
- **文字图像**: 针对包含文字的图像优化

### 🌐 多种接口
- **Web界面**: 美观的现代化用户界面
- **REST API**: 完整的API端点支持
- **预设API**: 一键使用预设配置
- **参数化API**: 完全自定义转换参数

### 📁 文件支持
- PNG (包含透明度)
- JPG/JPEG
- 自动文件格式检测

## 🛠 技术栈

- **Web框架**: FastAPI 0.104+
- **ASGI服务器**: Uvicorn
- **图像处理**: OpenCV, Pillow, NumPy
- **SVG生成**: svgwrite
- **日志系统**: XmiLogger

## 📦 安装

1. **克隆仓库**:
   ```bash
   git clone <your-repo-url>
   cd png2svg
   ```

2. **创建虚拟环境**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate  # Windows
   ```

3. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 使用方法

### 启动服务
```bash
python main.py
```
或使用开发模式（支持热重载）：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问: `http://localhost:8000`

### Web界面使用

1. 打开浏览器访问 `http://localhost:8000`
2. 选择图片文件（支持PNG、JPG）
3. 调整转换参数：
   - **阈值算法**: 选择最适合的阈值方法
   - **最小轮廓面积**: 过滤小噪点
   - **简化轮廓**: 减少路径点数
   - **边缘检测**: 增强边缘识别
   - **保留透明度**: 处理PNG透明通道
4. 点击"🚀 开始转换"

### API使用

#### 基础API转换
```bash
curl -X POST -F "file=@image.png" \
  "http://localhost:8000/api/convert/?threshold_method=adaptive&simplify_contours=true" \
  -o output.svg
```

#### 使用预设配置
```bash
# 照片优化预设
curl -X POST -F "file=@photo.png" \
  "http://localhost:8000/api/convert/preset/photo" \
  -o photo.svg

# Logo优化预设  
curl -X POST -F "file=@logo.png" \
  "http://localhost:8000/api/convert/preset/logo" \
  -o logo.svg
```

#### 完整参数示例
```bash
curl -X POST -F "file=@image.png" \
  "http://localhost:8000/api/convert/" \
  -G \
  -d "threshold_method=adaptive" \
  -d "simplify_contours=true" \
  -d "min_contour_area=50" \
  -d "edge_detection=true" \
  -d "preserve_transparency=true" \
  -o output.svg
```

## 📖 API文档

启动服务后可访问自动生成的API文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## ⚙️ 配置参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `threshold_method` | string | "adaptive" | 阈值算法: `adaptive`, `otsu`, `fixed` |
| `simplify_contours` | boolean | true | 是否简化轮廓路径 |
| `min_contour_area` | integer | 50 | 最小轮廓面积（像素） |
| `edge_detection` | boolean | true | 是否启用边缘检测增强 |
| `preserve_transparency` | boolean | true | 是否保留PNG透明度 |

### 阈值算法说明

- **adaptive**: 自适应阈值，适合光照不均的图像
- **otsu**: Otsu算法自动选择最佳阈值，适合双峰分布的图像
- **fixed**: 固定阈值128，适合对比度高的图像

## 🧪 测试

运行测试脚本验证功能：
```bash
python test_converter.py
```

测试内容包括：
- 基本转换功能
- 不同配置对比
- 透明度处理
- 性能测试

## 📁 项目结构

```
png2svg/
├── main.py              # FastAPI应用主文件
├── converter.py         # 核心转换逻辑
├── test_converter.py    # 测试脚本
├── requirements.txt     # 依赖列表
├── README.md           # 项目文档
├── logs/               # 日志目录
└── test_results/       # 测试输出目录
```

## 🔧 高级功能

### 自定义转换器

```python
from converter import ImageToSVGConverter

# 创建自定义转换器
converter = ImageToSVGConverter(
    threshold_method='adaptive',
    simplify_contours=True,
    min_contour_area=100,
    edge_detection=True,
    preserve_transparency=True
)

# 转换图像
with open('image.png', 'rb') as f:
    image_data = f.read()

svg_content = converter.convert(image_data)
```

### 批量处理

```python
from pathlib import Path
from converter import convert_file

input_dir = Path("input_images")
output_dir = Path("output_svgs")
output_dir.mkdir(exist_ok=True)

for image_file in input_dir.glob("*.png"):
    svg_content = convert_file(
        image_file, 
        threshold_method='adaptive',
        simplify_contours=True
    )
    
    output_file = output_dir / f"{image_file.stem}.svg"
    with open(output_file, 'w') as f:
        f.write(svg_content)
```

## 📊 性能优化

- **内存优化**: 流式处理大图像
- **算法优化**: 多级轮廓简化
- **缓存机制**: 智能预处理缓存
- **并发支持**: FastAPI原生异步支持

## 📝 日志

日志文件位置: `logs/app_log.log`

日志级别:
- INFO: 基本操作信息
- WARNING: 文件格式警告
- ERROR: 转换错误详情

## ⚠️ 注意事项

1. **图像质量**: 转换质量取决于原始图像的清晰度和对比度
2. **复杂度**: 过于复杂的图像可能生成较大的SVG文件
3. **透明度**: PNG透明度处理需要启用`preserve_transparency`
4. **内存使用**: 大图像处理可能需要较多内存

## 🤝 贡献

欢迎提交Issue和Pull Request！

## �� 许可证

本项目采用MIT许可证。