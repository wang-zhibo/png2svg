import io
import numpy as np
from PIL import Image
import cv2
from pathlib import Path

def bitmap_to_svg(bitmap, width, height):
    """将位图转换为SVG路径"""
    # 创建SVG头部
    svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
'''
    
    # 找到轮廓 - 处理不同版本的OpenCV返回值
    contours_result = cv2.findContours(bitmap, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # OpenCV 3.x 返回三个值，OpenCV 4.x 返回两个值
    if len(contours_result) == 3:
        _, contours, _ = contours_result
    else:
        contours, _ = contours_result
    
    # 打印轮廓数量，用于调试
    print(f"找到 {len(contours)} 个轮廓")
    
    # 添加轮廓到SVG
    for i, contour in enumerate(contours):
        # 只处理足够大的轮廓，过滤掉噪点
        if cv2.contourArea(contour) < 10:
            continue
            
        # 创建路径数据
        path_data = ""
        for j, point in enumerate(contour):
            x, y = point[0]
            if j == 0:
                path_data += f"M{x},{y} "
            else:
                path_data += f"L{x},{y} "
        
        # 闭合路径
        path_data += "Z"
        
        # 添加路径元素到SVG
        svg += f'  <path d="{path_data}" fill="black" stroke="none" />\n'
    
    # 如果没有找到有效轮廓，添加一个示例矩形
    if len(contours) == 0 or all(cv2.contourArea(contour) < 10 for contour in contours):
        print("未找到有效轮廓，添加示例矩形")
        svg += f'  <rect x="10" y="10" width="{width-20}" height="{height-20}" fill="none" stroke="black" stroke-width="2" />\n'
        svg += f'  <text x="{width/2}" y="{height/2}" text-anchor="middle" font-size="20">未检测到有效轮廓</text>\n'
    
    # 关闭SVG标签
    svg += '</svg>'
    
    return svg

def png_to_svg(png_data):
    """将PNG图像数据转换为SVG格式"""
    try:
        # 从二进制数据加载图像
        image = Image.open(io.BytesIO(png_data))
        
        # 转换为灰度图像
        image = image.convert('L')
        
        # 获取图像尺寸
        width, height = image.size
        
        # 转换为NumPy数组
        bitmap = np.array(image)
        
        # 确保位图是uint8类型，这是cv2.threshold所需的
        if bitmap.dtype != np.uint8:
            bitmap = bitmap.astype(np.uint8)
        
        # 二值化图像 (阈值可以根据需要调整)
        threshold = 128
        _, bitmap = cv2.threshold(bitmap, threshold, 255, cv2.THRESH_BINARY_INV)
        
        # 可选：应用一些形态学操作来改善轮廓检测
        kernel = np.ones((3, 3), np.uint8)
        bitmap = cv2.morphologyEx(bitmap, cv2.MORPH_CLOSE, kernel)
        bitmap = cv2.morphologyEx(bitmap, cv2.MORPH_OPEN, kernel)
        
        # 转换为SVG
        svg_content = bitmap_to_svg(bitmap, width, height)
        
        return svg_content
    except Exception as e:
        # 记录错误并重新抛出，以便FastAPI可以处理它
        print(f"PNG到SVG转换错误: {str(e)}")
        raise

def convert_file(file_path):
    """从文件路径转换PNG到SVG"""
    with open(file_path, 'rb') as f:
        png_data = f.read()
    
    return png_to_svg(png_data)