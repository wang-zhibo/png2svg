import io
import numpy as np
from PIL import Image
import cv2
from pathlib import Path
import svgwrite

class ImageToSVGConverter:
    """高级图片转SVG转换器"""
    
    def __init__(self, 
                 threshold_method='adaptive',
                 simplify_contours=True,
                 min_contour_area=50,
                 edge_detection=True,
                 preserve_transparency=True):
        """
        初始化转换器
        
        Args:
            threshold_method: 阈值方法 ('fixed', 'adaptive', 'otsu')
            simplify_contours: 是否简化轮廓
            min_contour_area: 最小轮廓面积
            edge_detection: 是否使用边缘检测
            preserve_transparency: 是否保留透明度
        """
        self.threshold_method = threshold_method
        self.simplify_contours = simplify_contours
        self.min_contour_area = min_contour_area
        self.edge_detection = edge_detection
        self.preserve_transparency = preserve_transparency

    def preprocess_image(self, image_array):
        """预处理图像"""
        # 降噪处理
        denoised = cv2.medianBlur(image_array, 5)
        
        # 如果启用边缘检测，先进行边缘增强
        if self.edge_detection:
            # 使用Canny边缘检测
            edges = cv2.Canny(denoised, 50, 150)
            # 将边缘信息与原图像结合
            denoised = cv2.addWeighted(denoised, 0.8, edges, 0.2, 0)
        
        return denoised

    def apply_threshold(self, image_array):
        """应用阈值处理"""
        if self.threshold_method == 'adaptive':
            # 自适应阈值，能更好地处理光照不均的图像
            binary = cv2.adaptiveThreshold(
                image_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )
        elif self.threshold_method == 'otsu':
            # Otsu自动阈值选择
            _, binary = cv2.threshold(
                image_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
        else:
            # 固定阈值
            _, binary = cv2.threshold(
                image_array, 128, 255, cv2.THRESH_BINARY_INV
            )
        
        return binary

    def improve_morphology(self, binary_image):
        """改进形态学操作"""
        # 使用更复杂的形态学操作序列
        kernel_small = np.ones((3, 3), np.uint8)
        kernel_medium = np.ones((5, 5), np.uint8)
        
        # 闭操作：连接邻近的区域
        closed = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel_medium)
        
        # 开操作：去除小噪点
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_small)
        
        # 填充孔洞
        filled = self.fill_holes(opened)
        
        return filled

    def fill_holes(self, binary_image):
        """填充轮廓内的孔洞"""
        # 创建一个稍大的图像，用于漫水填充
        h, w = binary_image.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)
        
        # 从边界开始漫水填充
        filled = binary_image.copy()
        cv2.floodFill(filled, mask, (0, 0), 255)
        
        # 反转填充结果并与原图像结合
        filled_inv = cv2.bitwise_not(filled)
        return cv2.bitwise_or(binary_image, filled_inv)

    def simplify_contour(self, contour):
        """简化轮廓点"""
        if not self.simplify_contours:
            return contour
        
        # 使用Douglas-Peucker算法简化轮廓
        epsilon = 0.02 * cv2.arcLength(contour, True)
        simplified = cv2.approxPolyDP(contour, epsilon, True)
        
        return simplified

    def contour_to_svg_path(self, contour):
        """将轮廓转换为SVG路径，支持曲线"""
        if len(contour) < 3:
            return ""
        
        path_data = ""
        contour = contour.reshape(-1, 2)
        
        # 移动到起始点
        path_data += f"M{contour[0][0]},{contour[0][1]} "
        
        # 如果点数较少，使用直线连接
        if len(contour) <= 4:
            for point in contour[1:]:
                path_data += f"L{point[0]},{point[1]} "
        else:
            # 使用平滑曲线连接
            for i in range(1, len(contour)):
                if i % 3 == 1 and i + 2 < len(contour):
                    # 使用三次贝塞尔曲线
                    cp1 = contour[i]
                    cp2 = contour[i + 1]
                    end = contour[i + 2]
                    path_data += f"C{cp1[0]},{cp1[1]} {cp2[0]},{cp2[1]} {end[0]},{end[1]} "
                elif i % 3 != 1:
                    continue
                else:
                    # 剩余点用直线连接
                    path_data += f"L{contour[i][0]},{contour[i][1]} "
        
        path_data += "Z"
        return path_data

    def create_optimized_svg(self, contours, width, height, has_transparency=False):
        """创建优化的SVG"""
        # 使用svgwrite库创建更标准的SVG
        dwg = svgwrite.Drawing(size=(width, height))
        dwg.viewbox(0, 0, width, height)
        
        # 添加背景（如果需要）
        if not has_transparency:
            dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill='white'))
        
        # 按面积排序轮廓，大的在后面（确保层次正确）
        contours_with_area = [(contour, cv2.contourArea(contour)) for contour in contours]
        contours_with_area.sort(key=lambda x: x[1])
        
        valid_contours = 0
        for contour, area in contours_with_area:
            if area < self.min_contour_area:
                continue
            
            # 简化轮廓
            simplified_contour = self.simplify_contour(contour)
            
            # 转换为SVG路径
            path_data = self.contour_to_svg_path(simplified_contour)
            
            if path_data:
                # 添加路径到SVG
                path = dwg.path(d=path_data)
                path.fill('black', opacity=0.9)
                path.stroke('none')
                dwg.add(path)
                valid_contours += 1
        
        # 如果没有有效轮廓，添加提示
        if valid_contours == 0:
            text = dwg.text('未检测到有效轮廓', 
                          insert=(width/2, height/2), 
                          text_anchor='middle',
                          font_size='20px',
                          fill='gray')
            dwg.add(text)
            
            # 添加边框
            border = dwg.rect(insert=(10, 10), 
                            size=(width-20, height-20),
                            fill='none',
                            stroke='gray',
                            stroke_width='2')
            dwg.add(border)
        
        return dwg.tostring()

    def process_transparency(self, image):
        """处理透明度信息"""
        if image.mode == 'RGBA':
            # 分离alpha通道
            r, g, b, a = image.split()
            
            # 创建基于alpha的mask
            alpha_array = np.array(a)
            
            # 转换为灰度
            gray_image = image.convert('L')
            gray_array = np.array(gray_image)
            
            # 将透明区域设为白色（背景）
            gray_array[alpha_array < 128] = 255
            
            return gray_array, True
        else:
            return np.array(image.convert('L')), False

    def convert(self, image_data):
        """主转换函数"""
        try:
            # 加载图像
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            print(f"处理图像: {width}x{height}, 模式: {image.mode}")
            
            # 处理透明度
            if self.preserve_transparency:
                gray_array, has_transparency = self.process_transparency(image)
            else:
                gray_array = np.array(image.convert('L'))
                has_transparency = False
            
            # 确保数据类型正确
            if gray_array.dtype != np.uint8:
                gray_array = gray_array.astype(np.uint8)
            
            print(f"灰度图像范围: {gray_array.min()} - {gray_array.max()}")
            
            # 预处理
            preprocessed = self.preprocess_image(gray_array)
            
            # 应用阈值
            binary = self.apply_threshold(preprocessed)
            
            # 改进形态学操作
            improved = self.improve_morphology(binary)
            
            # 查找轮廓
            contours_result = cv2.findContours(improved, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 处理不同OpenCV版本的返回值
            if len(contours_result) == 3:
                _, contours, _ = contours_result
            else:
                contours, _ = contours_result
            
            print(f"找到 {len(contours)} 个轮廓")
            
            # 创建优化的SVG
            svg_content = self.create_optimized_svg(contours, width, height, has_transparency)
            
            return svg_content
            
        except Exception as e:
            print(f"转换过程中出错: {str(e)}")
            raise


# 保持向后兼容的函数
def png_to_svg(png_data, **kwargs):
    """
    将PNG图像数据转换为SVG格式
    
    Args:
        png_data: PNG图像的二进制数据
        **kwargs: 转换参数
    """
    # 创建转换器实例
    converter = ImageToSVGConverter(**kwargs)
    
    # 执行转换
    return converter.convert(png_data)


def bitmap_to_svg(bitmap, width, height):
    """保持向后兼容的bitmap转SVG函数"""
    # 创建简单的SVG
    svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
'''
    
    # 找到轮廓
    contours_result = cv2.findContours(bitmap, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours_result) == 3:
        _, contours, _ = contours_result
    else:
        contours, _ = contours_result
    
    # 添加轮廓到SVG
    for contour in contours:
        if cv2.contourArea(contour) < 10:
            continue
        
        path_data = ""
        for j, point in enumerate(contour):
            x, y = point[0]
            if j == 0:
                path_data += f"M{x},{y} "
            else:
                path_data += f"L{x},{y} "
        
        path_data += "Z"
        svg += f'  <path d="{path_data}" fill="black" stroke="none" />\n'
    
    svg += '</svg>'
    return svg


def convert_file(file_path, **kwargs):
    """从文件路径转换图像到SVG"""
    with open(file_path, 'rb') as f:
        image_data = f.read()
    
    return png_to_svg(image_data, **kwargs)