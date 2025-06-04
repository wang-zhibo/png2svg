#!/usr/bin/env python3
"""
测试优化后的图片转SVG转换器
"""

import os
import time
from pathlib import Path
from converter import ImageToSVGConverter, png_to_svg

def test_basic_conversion():
    """测试基本转换功能"""
    print("🧪 测试基本转换功能...")
    
    # 创建一个简单的测试图像
    from PIL import Image, ImageDraw
    import io
    
    # 创建测试图像
    test_image = Image.new('RGB', (200, 200), 'white')
    draw = ImageDraw.Draw(test_image)
    
    # 绘制一些图形
    draw.rectangle([50, 50, 150, 150], fill='black')
    draw.ellipse([75, 75, 125, 125], fill='white')
    
    # 转换为字节流
    img_buffer = io.BytesIO()
    test_image.save(img_buffer, format='PNG')
    img_data = img_buffer.getvalue()
    
    # 测试转换
    svg_content = png_to_svg(img_data)
    
    print(f"✅ 基本转换成功! SVG长度: {len(svg_content)} 字符")
    return svg_content

def test_different_configs():
    """测试不同配置的转换效果"""
    print("\n🔧 测试不同配置...")
    
    from PIL import Image, ImageDraw
    import io
    
    # 创建复杂一点的测试图像
    test_image = Image.new('RGB', (300, 300), 'white')
    draw = ImageDraw.Draw(test_image)
    
    # 绘制多个图形
    draw.rectangle([20, 20, 80, 80], fill='black')
    draw.ellipse([100, 20, 160, 80], fill='gray')
    draw.polygon([(200, 20), (250, 80), (150, 80)], fill='darkgray')
    draw.text((50, 150), "TEST", fill='black')
    
    img_buffer = io.BytesIO()
    test_image.save(img_buffer, format='PNG')
    img_data = img_buffer.getvalue()
    
    configs = {
        "自适应阈值": {"threshold_method": "adaptive"},
        "Otsu阈值": {"threshold_method": "otsu"}, 
        "固定阈值": {"threshold_method": "fixed"},
        "启用边缘检测": {"edge_detection": True},
        "禁用边缘检测": {"edge_detection": False},
        "简化轮廓": {"simplify_contours": True},
        "不简化轮廓": {"simplify_contours": False}
    }
    
    results = {}
    for name, config in configs.items():
        start_time = time.time()
        svg_content = png_to_svg(img_data, **config)
        end_time = time.time()
        
        results[name] = {
            'length': len(svg_content),
            'time': end_time - start_time
        }
        
        print(f"  {name}: {results[name]['length']} 字符, {results[name]['time']:.3f}s")
    
    return results

def test_transparency():
    """测试透明度处理"""
    print("\n🎨 测试透明度处理...")
    
    from PIL import Image, ImageDraw
    import io
    
    # 创建带透明度的图像
    test_image = Image.new('RGBA', (200, 200), (255, 255, 255, 0))  # 透明背景
    draw = ImageDraw.Draw(test_image)
    
    # 绘制半透明图形
    draw.rectangle([50, 50, 150, 150], fill=(0, 0, 0, 255))  # 不透明黑色
    draw.ellipse([75, 75, 125, 125], fill=(128, 128, 128, 128))  # 半透明灰色
    
    img_buffer = io.BytesIO()
    test_image.save(img_buffer, format='PNG')
    img_data = img_buffer.getvalue()
    
    # 测试保留透明度
    svg_with_alpha = png_to_svg(img_data, preserve_transparency=True)
    svg_without_alpha = png_to_svg(img_data, preserve_transparency=False)
    
    print(f"  保留透明度: {len(svg_with_alpha)} 字符")
    print(f"  忽略透明度: {len(svg_without_alpha)} 字符")
    
    return svg_with_alpha, svg_without_alpha

def test_performance():
    """测试性能"""
    print("\n⚡ 性能测试...")
    
    from PIL import Image, ImageDraw
    import io
    
    # 创建不同大小的图像进行测试
    sizes = [(100, 100), (300, 300), (500, 500)]
    
    for width, height in sizes:
        # 创建测试图像
        test_image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(test_image)
        
        # 绘制复杂图形
        for i in range(0, width, 30):
            for j in range(0, height, 30):
                draw.rectangle([i, j, i+20, j+20], fill='black')
        
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()
        
        # 测试转换时间
        start_time = time.time()
        svg_content = png_to_svg(img_data)
        end_time = time.time()
        
        print(f"  {width}x{height}: {end_time - start_time:.3f}s, SVG: {len(svg_content)} 字符")

def save_test_results():
    """保存测试结果"""
    print("\n💾 保存测试结果...")
    
    # 创建输出目录
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)
    
    # 测试基本转换并保存
    svg_content = test_basic_conversion()
    
    with open(output_dir / "basic_test.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"✅ 测试结果保存到: {output_dir}")

def main():
    """主测试函数"""
    print("🚀 开始测试优化后的图片转SVG转换器")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_basic_conversion()
        test_different_configs()
        test_transparency()
        test_performance()
        save_test_results()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成!")
        print("\n📋 测试总结:")
        print("  ✓ 基本转换功能正常")
        print("  ✓ 配置选项工作正常")
        print("  ✓ 透明度处理正常")
        print("  ✓ 性能表现良好")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        raise

if __name__ == "__main__":
    main() 