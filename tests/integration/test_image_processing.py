#!/usr/bin/env python3
"""
图片处理服务测试脚本
测试格式转换、压缩、水印等功能
"""
import requests
import os
import json
from PIL import Image
import io

class ImageProcessingTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def login(self, username="admin", password="admin666"):
        """登录获取token"""
        print("🔐 正在登录...")
        response = self.session.post(
            f"{self.base_url}/api/auth/login",
            data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("✅ 登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
    
    def get_supported_formats(self):
        """获取支持的格式"""
        print("\n📋 获取支持的图片格式...")
        response = self.session.get(f"{self.base_url}/api/image/formats")
        
        if response.status_code == 200:
            formats = response.json()
            print("✅ 支持的格式:")
            for fmt in formats:
                print(f"  - {fmt['format']}: {fmt['description']} (.{fmt['extension']})")
            return formats
        else:
            print(f"❌ 获取格式失败: {response.text}")
            return []
    
    def create_test_image(self, filename="test_image.png", size=(800, 600), format="PNG"):
        """创建测试图片"""
        print(f"\n🎨 创建测试图片: {filename}")
        
        # 创建一个彩色渐变图片
        img = Image.new('RGB', size, color='white')
        pixels = img.load()
        
        # 创建渐变效果
        for x in range(size[0]):
            for y in range(size[1]):
                r = int(255 * x / size[0])
                g = int(255 * y / size[1])
                b = int(255 * (x + y) / (size[0] + size[1]))
                pixels[x, y] = (r, g, b)
        
        # 添加一些文字
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        text = "Test Image for Conversion"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), text, fill='white', font=font)
        
        # 保存图片
        img.save(filename, format=format)
        file_size = os.path.getsize(filename)
        print(f"✅ 测试图片创建成功: {filename} ({file_size} bytes)")
        
        return filename, file_size
    
    def get_image_info(self, image_path):
        """获取图片信息"""
        print(f"\n📊 获取图片信息: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'file': (image_path, f, 'image/png')}
            response = self.session.post(f"{self.base_url}/api/image/info", files=files)
        
        if response.status_code == 200:
            info = response.json()
            print("✅ 图片信息:")
            print(f"  格式: {info.get('format', 'N/A')}")
            print(f"  模式: {info.get('mode', 'N/A')}")
            print(f"  尺寸: {info.get('width', 0)} x {info.get('height', 0)}")
            print(f"  文件大小: {info.get('file_size', 0)} bytes")
            return info
        else:
            print(f"❌ 获取图片信息失败: {response.text}")
            return None
    
    def convert_image(self, image_path, target_format, quality=95, resize=None, watermark=False):
        """转换图片"""
        print(f"\n🔄 转换图片: {image_path} -> {target_format}")
        print(f"  质量: {quality}, 调整大小: {resize}, 水印: {watermark}")
        
        with open(image_path, 'rb') as f:
            files = {'file': (image_path, f, 'image/png')}
            data = {
                'target_format': target_format,
                'quality': quality,
                'watermark': watermark
            }
            
            if resize:
                data['resize_width'] = resize[0]
                data['resize_height'] = resize[1]
            
            response = self.session.post(f"{self.base_url}/api/image/convert", files=files, data=data)
        
        if response.status_code == 200:
            # 保存转换后的图片
            output_filename = f"converted_{target_format.lower()}.{target_format.lower()}"
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(output_filename)
            print(f"✅ 转换成功: {output_filename} ({file_size} bytes)")
            
            # 获取转换后图片的信息
            self.get_image_info(output_filename)
            
            return output_filename, file_size
        else:
            print(f"❌ 转换失败: {response.text}")
            return None, 0
    
    def get_usage_stats(self):
        """获取使用统计"""
        print("\n📈 获取使用统计...")
        response = self.session.get(f"{self.base_url}/api/image/usage")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ 使用统计:")
            print(f"  今日使用: {stats['today_usage']}")
            print(f"  每日限制: {stats['daily_limit']}")
            print(f"  剩余次数: {stats['remaining_usage']}")
            print(f"  用户角色: {stats['role']}")
            return stats
        else:
            print(f"❌ 获取统计失败: {response.text}")
            return None
    
    def get_conversion_records(self, limit=5):
        """获取转换记录"""
        print(f"\n📝 获取转换记录 (最近{limit}条)...")
        response = self.session.get(f"{self.base_url}/api/image/records?limit={limit}")
        
        if response.status_code == 200:
            records = response.json()
            print("✅ 转换记录:")
            for i, record in enumerate(records, 1):
                print(f"  {i}. {record['original_filename']} -> {record['target_format']}")
                print(f"     状态: {record['status']}, 大小: {record['file_size']} bytes")
                print(f"     时间: {record['conversion_time']:.2f}s, 日期: {record['created_at']}")
            return records
        else:
            print(f"❌ 获取记录失败: {response.text}")
            return []
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 开始图片处理服务综合测试")
        print("=" * 60)
        
        # 1. 登录
        if not self.login():
            return
        
        # 2. 获取支持的格式
        formats = self.get_supported_formats()
        
        # 3. 获取使用统计
        self.get_usage_stats()
        
        # 4. 创建测试图片
        test_image, original_size = self.create_test_image()
        
        # 5. 获取原始图片信息
        self.get_image_info(test_image)
        
        # 6. 测试各种转换
        conversions = [
            {"format": "JPEG", "quality": 95, "resize": None, "watermark": False},
            {"format": "JPEG", "quality": 50, "resize": None, "watermark": False},
            {"format": "WEBP", "quality": 80, "resize": (400, 300), "watermark": False},
            {"format": "PNG", "quality": 95, "resize": None, "watermark": True},
            {"format": "BMP", "quality": 95, "resize": (200, 150), "watermark": False},
        ]
        
        converted_files = []
        for i, conv in enumerate(conversions, 1):
            print(f"\n--- 转换测试 {i}/{len(conversions)} ---")
            output_file, output_size = self.convert_image(
                test_image, 
                conv["format"], 
                conv["quality"], 
                conv["resize"], 
                conv["watermark"]
            )
            
            if output_file:
                converted_files.append({
                    "original": test_image,
                    "converted": output_file,
                    "format": conv["format"],
                    "original_size": original_size,
                    "converted_size": output_size,
                    "compression_ratio": (1 - output_size / original_size) * 100 if original_size > 0 else 0
                })
        
        # 7. 显示转换结果对比
        print("\n📊 转换结果对比:")
        print("-" * 80)
        print(f"{'格式':<8} {'原始大小':<12} {'转换大小':<12} {'压缩率':<10} {'文件名'}")
        print("-" * 80)
        print(f"{'PNG':<8} {original_size:<12} {original_size:<12} {'0.0%':<10} {test_image}")
        
        for conv in converted_files:
            print(f"{conv['format']:<8} {conv['original_size']:<12} {conv['converted_size']:<12} "
                  f"{conv['compression_ratio']:.1f}%{'':<6} {conv['converted']}")
        
        # 8. 获取最终使用统计
        print("\n" + "=" * 60)
        self.get_usage_stats()
        
        # 9. 获取转换记录
        self.get_conversion_records()
        
        # # 10. 清理测试文件
        # print("\n🧹 清理测试文件...")
        # for conv in converted_files:
        #     if os.path.exists(conv['converted']):
        #         os.remove(conv['converted'])
        #         print(f"  删除: {conv['converted']}")
        
        if os.path.exists(test_image):
            os.remove(test_image)
            print(f"  删除: {test_image}")
        
        print("\n🎉 测试完成!")

def main():
    """主函数"""
    tester = ImageProcessingTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
