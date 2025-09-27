import os
import time
from typing import Optional, Tuple
from PIL import Image, ImageOps
from sqlalchemy.orm import Session
from models import ConversionRecord
from schemas import ImageConvertRequest
from config import settings

class ImageService:
    def __init__(self, db: Session):
        self.db = db
    
    def convert_image(self, 
                     file_path: str, 
                     target_format: str, 
                     user_id: Optional[int],
                     convert_request: ImageConvertRequest) -> Tuple[bool, str, Optional[str]]:
        """
        转换图片格式
        返回: (是否成功, 输出文件路径, 错误信息)
        """
        start_time = time.time()
        
        try:
            # 打开原始图片
            with Image.open(file_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 调整大小（如果指定）
                if convert_request.resize:
                    width = convert_request.resize.get('width')
                    height = convert_request.resize.get('height')
                    if width and height and width > 0 and height > 0:
                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                    elif width and width > 0:
                        ratio = width / img.width
                        height = int(img.height * ratio)
                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                    elif height and height > 0:
                        ratio = height / img.height
                        width = int(img.width * ratio)
                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # 添加水印（如果需要）
                if convert_request.watermark:
                    img = self._add_watermark(img)
                
                # 生成输出文件路径
                original_filename = os.path.basename(file_path)
                name, _ = os.path.splitext(original_filename)
                output_filename = f"{name}_converted.{target_format.lower()}"
                output_path = os.path.join(settings.upload_dir, "converted", output_filename)
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # 保存转换后的图片
                save_kwargs = {}
                if target_format.upper() in ['JPEG', 'JPG']:
                    save_kwargs['quality'] = convert_request.quality
                    save_kwargs['optimize'] = True
                elif target_format.upper() == 'WEBP':
                    save_kwargs['quality'] = convert_request.quality
                    save_kwargs['optimize'] = True
                
                img.save(output_path, format=target_format.upper(), **save_kwargs)
                
                # 计算转换时间
                conversion_time = time.time() - start_time
                
                # 获取文件大小
                file_size = os.path.getsize(output_path)
                
                # 记录转换记录
                self._record_conversion(
                    user_id=user_id,
                    original_filename=original_filename,
                    original_format=os.path.splitext(file_path)[1][1:].upper(),
                    target_format=target_format.upper(),
                    file_size=file_size,
                    conversion_time=conversion_time,
                    status="success"
                )
                
                return True, output_path, None
                
        except Exception as e:
            conversion_time = time.time() - start_time
            error_message = str(e)
            
            # 记录失败的转换
            self._record_conversion(
                user_id=user_id,
                original_filename=os.path.basename(file_path),
                original_format=os.path.splitext(file_path)[1][1:].upper(),
                target_format=target_format.upper(),
                file_size=0,
                conversion_time=conversion_time,
                status="failed",
                error_message=error_message
            )
            
            return False, "", error_message
    
    def _add_watermark(self, img: Image.Image) -> Image.Image:
        """添加水印"""
        try:
            # 创建水印文本
            watermark_text = "ImageConvert"
            
            # 创建水印图片
            watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
            
            # 这里可以添加更复杂的水印逻辑
            # 简单示例：在右下角添加半透明文本
            from PIL import ImageDraw, ImageFont
            
            draw = ImageDraw.Draw(watermark)
            
            # 尝试使用默认字体
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # 获取文本尺寸
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算位置（右下角）
            x = img.width - text_width - 10
            y = img.height - text_height - 10
            
            # 绘制半透明文本
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
            
            # 合并水印
            img = Image.alpha_composite(img.convert('RGBA'), watermark)
            
        except Exception:
            # 如果水印添加失败，返回原图
            pass
        
        return img
    
    def _record_conversion(self, 
                          user_id: Optional[int],
                          original_filename: str,
                          original_format: str,
                          target_format: str,
                          file_size: int,
                          conversion_time: float,
                          status: str,
                          error_message: Optional[str] = None):
        """记录转换记录"""
        # 如果user_id为None，跳过记录（公开接口不需要记录到数据库）
        if user_id is None:
            return
            
        conversion_record = ConversionRecord(
            user_id=user_id,
            original_filename=original_filename,
            original_format=original_format,
            target_format=target_format,
            file_size=file_size,
            conversion_time=conversion_time,
            status=status,
            error_message=error_message
        )
        
        self.db.add(conversion_record)
        self.db.commit()
    
    def get_supported_formats(self) -> list:
        """获取支持的图片格式"""
        return [
            {"format": "JPEG", "description": "JPEG图片格式", "extension": "jpg"},
            {"format": "PNG", "description": "PNG图片格式", "extension": "png"},
            {"format": "WEBP", "description": "WebP图片格式", "extension": "webp"},
            {"format": "BMP", "description": "BMP图片格式", "extension": "bmp"},
            {"format": "TIFF", "description": "TIFF图片格式", "extension": "tiff"},
            {"format": "GIF", "description": "GIF图片格式", "extension": "gif"}
        ]
    
    def validate_image_file(self, file_path: str) -> bool:
        """验证图片文件"""
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def get_image_info(self, file_path: str) -> dict:
        """获取图片信息"""
        try:
            with Image.open(file_path) as img:
                return {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "file_size": os.path.getsize(file_path)
                }
        except Exception as e:
            return {"error": str(e)}
