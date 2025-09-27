#!/usr/bin/env python3
"""
简单的图片转换测试
"""
import requests
import os
from PIL import Image
import io

def create_simple_test_image():
    """创建一个简单的测试图片"""
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)
    img_bytes.seek(0)
    return img_bytes

def test_simple_convert():
    """测试简单的图片转换"""
    base_url = "http://localhost:8000"
    
    print("=== 创建测试图片 ===")
    test_image = create_simple_test_image()
    print(f"✅ 测试图片创建成功，大小: {len(test_image.getvalue())} bytes")
    
    print("\n=== 测试图片转换 ===")
    
    # 重置图片流
    test_image.seek(0)
    
    # 准备请求数据
    files = {
        'file': ('test.jpg', test_image, 'image/jpeg')
    }
    
    data = {
        'target_format': 'jpeg',
        'quality': 80
    }
    
    try:
        print(f"发送请求到: {base_url}/api/image/convert")
        response = requests.post(
            f"{base_url}/api/image/convert",
            files=files,
            data=data
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 转换成功")
            print(f"返回文件大小: {len(response.content)} bytes")
            
            # 保存结果
            with open("converted_test.jpg", "wb") as f:
                f.write(response.content)
            print("✅ 保存为: converted_test.jpg")
            
        else:
            print(f"❌ 转换失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求错误: {e}")

if __name__ == "__main__":
    test_simple_convert()
