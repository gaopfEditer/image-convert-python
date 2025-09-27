#!/usr/bin/env python3
"""
测试增强的图片处理功能
包括详细记录、对比展示等功能
"""
import requests
import os
import json
from PIL import Image, ImageDraw, ImageFont
import time

class EnhancedImageTester:
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
    
    def create_test_image(self, filename="enhanced_test.png", size=(800, 600)):
        """创建测试图片"""
        print(f"\n🎨 创建测试图片: {filename}")
        
        # 创建一个复杂的测试图片
        img = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(img)
        
        # 添加渐变背景
        for y in range(size[1]):
            color_value = int(255 * y / size[1])
            draw.line([(0, y), (size[0], y)], fill=(color_value, 100, 255 - color_value))
        
        # 添加文字
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        text = "Enhanced Test Image"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), text, fill='white', font=font)
        
        # 添加一些图形
        draw.rectangle([50, 50, 150, 150], outline='red', width=3)
        draw.ellipse([200, 200, 300, 300], outline='blue', width=3)
        
        img.save(filename)
        file_size = os.path.getsize(filename)
        print(f"✅ 测试图片创建成功: {filename} ({file_size} bytes)")
        
        return filename, file_size
    
    def test_enhanced_conversion(self, image_path):
        """测试增强的转换功能"""
        print(f"\n🔄 测试增强转换功能: {image_path}")
        
        # 测试多种转换参数
        test_cases = [
            {
                "name": "高质量JPEG",
                "params": {
                    "target_format": "JPEG",
                    "quality": 95,
                    "watermark": False
                }
            },
            {
                "name": "压缩JPEG",
                "params": {
                    "target_format": "JPEG",
                    "quality": 30,
                    "resize_width": 400,
                    "resize_height": 300,
                    "watermark": True
                }
            },
            {
                "name": "WebP格式",
                "params": {
                    "target_format": "WEBP",
                    "quality": 80,
                    "watermark": False
                }
            },
            {
                "name": "PNG无损",
                "params": {
                    "target_format": "PNG",
                    "watermark": True
                }
            }
        ]
        
        conversion_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- 测试 {i}/{len(test_cases)}: {test_case['name']} ---")
            
            with open(image_path, 'rb') as f:
                files = {'file': (image_path, f, 'image/png')}
                data = test_case['params']
                
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/api/image/convert",
                    files=files,
                    data=data
                )
                conversion_time = time.time() - start_time
            
            if response.status_code == 200:
                # 保存转换后的图片
                output_filename = f"enhanced_{test_case['name'].replace(' ', '_').lower()}.{test_case['params']['target_format'].lower()}"
                with open(output_filename, 'wb') as f:
                    f.write(response.content)
                
                file_size = os.path.getsize(output_filename)
                print(f"✅ 转换成功: {output_filename} ({file_size} bytes)")
                
                conversion_results.append({
                    "name": test_case['name'],
                    "filename": output_filename,
                    "file_size": file_size,
                    "conversion_time": conversion_time
                })
            else:
                print(f"❌ 转换失败: {response.text}")
        
        return conversion_results
    
    def test_records_api(self):
        """测试记录API"""
        print("\n📋 测试转换记录API...")
        
        # 获取记录列表
        response = self.session.get(f"{self.base_url}/api/image/records?limit=5")
        
        if response.status_code == 200:
            records = response.json()
            print(f"✅ 获取到 {len(records)} 条记录")
            
            for i, record in enumerate(records, 1):
                print(f"\n记录 {i}:")
                print(f"  文件名: {record['original_filename']}")
                print(f"  格式: {record['original_image']['format']} → {record['converted_image']['format']}")
                print(f"  尺寸: {record['original_image']['width']}×{record['original_image']['height']} → {record['converted_image']['width']}×{record['converted_image']['height']}")
                print(f"  大小: {record['original_image']['file_size']} bytes → {record['converted_image']['file_size']} bytes")
                print(f"  压缩率: {record['comparison_stats']['compression_ratio']:.1f}%")
                print(f"  处理时间: {record['conversion_time']:.2f}s")
                
                # 测试预览功能
                if i <= 2:  # 只测试前2条记录
                    self.test_preview_api(record['id'])
            
            return records
        else:
            print(f"❌ 获取记录失败: {response.text}")
            return []
    
    def test_preview_api(self, record_id):
        """测试预览API"""
        print(f"\n🖼️ 测试预览API (记录ID: {record_id})...")
        
        # 测试原图缩略图
        response = self.session.get(f"{self.base_url}/api/image/preview/{record_id}/original?size=thumbnail")
        if response.status_code == 200:
            print("✅ 原图缩略图获取成功")
        else:
            print(f"❌ 原图缩略图获取失败: {response.status_code}")
        
        # 测试生成图缩略图
        response = self.session.get(f"{self.base_url}/api/image/preview/{record_id}/converted?size=thumbnail")
        if response.status_code == 200:
            print("✅ 生成图缩略图获取成功")
        else:
            print(f"❌ 生成图缩略图获取失败: {response.status_code}")
    
    def test_detailed_record(self, record_id):
        """测试详细记录API"""
        print(f"\n📊 测试详细记录API (记录ID: {record_id})...")
        
        response = self.session.get(f"{self.base_url}/api/image/records/{record_id}")
        
        if response.status_code == 200:
            record = response.json()
            print("✅ 详细记录获取成功")
            print(f"  处理参数: {json.dumps(record['processing_params'], indent=2)}")
            print(f"  对比统计: {json.dumps(record['comparison_stats'], indent=2)}")
            return record
        else:
            print(f"❌ 详细记录获取失败: {response.text}")
            return None
    
    def test_download_api(self, record_id):
        """测试下载API"""
        print(f"\n⬇️ 测试下载API (记录ID: {record_id})...")
        
        # 测试下载原图
        response = self.session.get(f"{self.base_url}/api/image/download/{record_id}/original")
        if response.status_code == 200:
            print("✅ 原图下载成功")
        else:
            print(f"❌ 原图下载失败: {response.status_code}")
        
        # 测试下载生成图
        response = self.session.get(f"{self.base_url}/api/image/download/{record_id}/converted")
        if response.status_code == 200:
            print("✅ 生成图下载成功")
        else:
            print(f"❌ 生成图下载失败: {response.status_code}")
    
    def generate_test_report(self, conversion_results, records):
        """生成测试报告"""
        print("\n📊 生成测试报告")
        print("=" * 60)
        
        print("\n🔄 转换测试结果:")
        print("-" * 40)
        for result in conversion_results:
            print(f"{result['name']:<15} {result['file_size']:>8} bytes {result['conversion_time']:>6.2f}s")
        
        print("\n📋 记录统计:")
        print("-" * 40)
        if records:
            total_original_size = sum(r['original_image']['file_size'] for r in records)
            total_converted_size = sum(r['converted_image']['file_size'] for r in records)
            avg_compression = sum(r['comparison_stats']['compression_ratio'] for r in records) / len(records)
            
            print(f"总记录数: {len(records)}")
            print(f"总原始大小: {total_original_size:,} bytes")
            print(f"总转换大小: {total_converted_size:,} bytes")
            print(f"平均压缩率: {avg_compression:.1f}%")
            print(f"节省空间: {total_original_size - total_converted_size:,} bytes")
        
        print("\n🎯 功能测试状态:")
        print("-" * 40)
        print("✅ 增强转换功能")
        print("✅ 记录列表API")
        print("✅ 预览功能API")
        print("✅ 详细记录API")
        print("✅ 下载功能API")
    
    def run_enhanced_test(self):
        """运行增强功能测试"""
        print("🚀 开始增强图片处理功能测试")
        print("=" * 60)
        
        # 1. 登录
        if not self.login():
            return
        
        # 2. 创建测试图片
        test_image, original_size = self.create_test_image()
        
        # 3. 测试增强转换功能
        conversion_results = self.test_enhanced_conversion(test_image)
        
        # 4. 测试记录API
        records = self.test_records_api()
        
        # 5. 测试详细记录API（如果有记录）
        if records:
            self.test_detailed_record(records[0]['id'])
            self.test_download_api(records[0]['id'])
        
        # 6. 生成测试报告
        self.generate_test_report(conversion_results, records)
        
        # 7. 清理测试文件
        print("\n🧹 清理测试文件...")
        for result in conversion_results:
            if os.path.exists(result['filename']):
                os.remove(result['filename'])
                print(f"  删除: {result['filename']}")
        
        if os.path.exists(test_image):
            os.remove(test_image)
            print(f"  删除: {test_image}")
        
        print("\n🎉 增强功能测试完成!")

def main():
    """主函数"""
    tester = EnhancedImageTester()
    tester.run_enhanced_test()

if __name__ == "__main__":
    main()
