#!/usr/bin/env python3
"""
图片压缩接口测试
"""
import requests
import os
from PIL import Image
import io

def create_test_image():
    """创建一个测试图片"""
    # 创建一个简单的测试图片
    img = Image.new('RGB', (800, 600), color='red')
    
    # 添加一些内容
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # 尝试使用默认字体
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # 绘制文字
    text = "Test Image for Compression"
    if font:
        draw.text((50, 50), text, fill='white', font=font)
    else:
        draw.text((50, 50), text, fill='white')
    
    # 保存到内存
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)
    img_bytes.seek(0)
    
    return img_bytes

def test_image_compress():
    """测试图片压缩接口"""
    base_url = "http://localhost:8000"
    
    # 1. 先登录获取token
    print("=== 1. 登录获取token ===")
    login_data = {
        "username": "admin@example.com",
        "password": "admin666"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return
        
        token_data = response.json()
        token = token_data["access_token"]
        print(f"✅ 登录成功，token: {token[:20]}...")
        
    except Exception as e:
        print(f"❌ 登录错误: {e}")
        return
    
    # 2. 创建测试图片
    print("\n=== 2. 创建测试图片 ===")
    test_image = create_test_image()
    print(f"✅ 测试图片创建成功，大小: {len(test_image.getvalue())} bytes")
    
    # 3. 测试不同质量的压缩
    print("\n=== 3. 测试图片压缩 ===")
    
    qualities = [95, 80, 60, 40, 20]
    
    for quality in qualities:
        print(f"\n--- 测试质量 {quality} ---")
        
        # 重置图片流
        test_image.seek(0)
        
        # 准备请求数据
        files = {
            'file': ('test_image.jpg', test_image, 'image/jpeg')
        }
        
        data = {
            'target_format': 'jpeg',
            'quality': quality,
            'resize_width': 400,  # 同时调整大小
            'resize_height': 300
        }
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/image/convert",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                # 获取压缩后的图片大小
                compressed_size = len(response.content)
                original_size = len(test_image.getvalue())
                compression_ratio = (1 - compressed_size / original_size) * 100
                
                print(f"✅ 压缩成功")
                print(f"   原始大小: {original_size} bytes")
                print(f"   压缩后大小: {compressed_size} bytes")
                print(f"   压缩率: {compression_ratio:.1f}%")
                
                # 保存压缩后的图片
                output_filename = f"compressed_q{quality}.jpg"
                with open(output_filename, 'wb') as f:
                    f.write(response.content)
                print(f"   保存为: {output_filename}")
                
            else:
                print(f"❌ 压缩失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 请求错误: {e}")
    
    # 4. 测试支持的格式
    print("\n=== 4. 测试支持的格式 ===")
    try:
        response = requests.get(f"{base_url}/api/image/formats")
        if response.status_code == 200:
            formats = response.json()
            print(f"✅ 支持的格式: {formats}")
        else:
            print(f"❌ 获取格式失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取格式错误: {e}")

if __name__ == "__main__":
    test_image_compress()
