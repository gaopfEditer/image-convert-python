#!/usr/bin/env python3
"""
创建新的项目目录结构
"""
import os
import shutil
from pathlib import Path

def create_directory_structure():
    """创建新的目录结构"""
    
    # 定义目录结构
    directories = [
        # Framework Layer
        "framework",
        "framework/middleware",
        "framework/routes", 
        "framework/schemas",
        
        # Business Layer
        "business",
        "business/image_conversion",
        "business/user_management",
        "business/payment",
        "business/permission",
        
        # Tool Layer
        "tool",
        "tool/image",
        "tool/file",
        "tool/crypto",
        "tool/utils",
        
        # Infra Layer
        "infra",
        "infra/database",
        "infra/database/migrations",
        "infra/database/repositories",
        "infra/cache",
        "infra/storage",
        "infra/external",
        
        # Domain Layer
        "domain",
        "domain/entities",
        "domain/value_objects",
        "domain/services",
        "domain/repositories",
        
        # Types Layer
        "types",
        
        # Config
        "config",
        
        # Tests
        "tests",
        "tests/unit",
        "tests/integration", 
        "tests/e2e",
        
        # Scripts
        "scripts",
        
        # Docs
        "docs",
        "docs/api",
        "docs/architecture",
        "docs/deployment"
    ]
    
    # 创建目录
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # 创建__init__.py文件
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('"""\n{}模块\n"""\n'.format(directory.replace('/', '.')))
    
    print("✅ 目录结构创建完成")

def create_core_files():
    """创建核心文件"""
    
    # 1. 类型定义
    types_content = '''"""
全局类型定义
"""
from typing import Optional, List, Dict, Any, Union, Tuple
from enum import Enum
from datetime import datetime

# 通用类型
UserId = int
ImageId = int
ConversionId = int
PaymentId = int

# 状态枚举
class ConversionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"

class UserRole(str, Enum):
    FREE = "FREE"
    VIP = "VIP"
    SVIP = "SVIP"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

# 图片相关类型
class ImageFormat(str, Enum):
    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    BMP = "BMP"
    TIFF = "TIFF"
    GIF = "GIF"

class ImageMode(str, Enum):
    RGB = "RGB"
    RGBA = "RGBA"
    L = "L"
    P = "P"

# 处理参数类型
@dataclass
class ProcessingParams:
    target_format: ImageFormat
    quality: int = 95
    resize_width: Optional[int] = None
    resize_height: Optional[int] = None
    watermark: bool = False

# 文件信息类型
@dataclass
class FileInfo:
    filename: str
    file_size: int
    file_path: str
    mime_type: str

# 图片元数据类型
@dataclass
class ImageMetadata:
    width: int
    height: int
    format: ImageFormat
    mode: ImageMode
    file_size: int
    dpi_x: Optional[float] = None
    dpi_y: Optional[float] = None
    has_transparency: bool = False

# API响应类型
@dataclass
class ApiResponse:
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error_code: Optional[str] = None

# 分页类型
@dataclass
class PaginationParams:
    page: int = 1
    size: int = 10
    offset: int = 0

@dataclass
class PaginatedResponse:
    items: List[Any]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
'''
    
    with open("types/__init__.py", "w", encoding="utf-8") as f:
        f.write(types_content)
    
    # 2. 配置管理
    config_content = '''"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class DatabaseConfig(BaseSettings):
    url: str = "mysql+pymysql://root:123456@1.94.137.69:3306/image_convert_db"
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

class RedisConfig(BaseSettings):
    host: str = "1.94.137.69"
    port: int = 6379
    database: int = 0
    password: Optional[str] = "foobared"
    url: str = "redis://:foobared@1.94.137.69:6379/0"

class StorageConfig(BaseSettings):
    type: str = "local"  # local, oss, s3
    upload_dir: str = "uploads"
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]

class JWTConfig(BaseSettings):
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

class PaymentConfig(BaseSettings):
    alipay_app_id: str = ""
    alipay_private_key: str = ""
    alipay_public_key: str = ""
    wechat_app_id: str = ""
    wechat_mch_id: str = ""
    wechat_api_key: str = ""

class Settings(BaseSettings):
    debug: bool = False
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    storage: StorageConfig = StorageConfig()
    jwt: JWTConfig = JWTConfig()
    payment: PaymentConfig = PaymentConfig()
    
    class Config:
        env_file = ".env"

settings = Settings()

# 确保上传目录存在
os.makedirs(settings.storage.upload_dir, exist_ok=True)
'''
    
    with open("config/__init__.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    # 3. 主应用入口
    main_content = '''"""
应用主入口
"""
from framework.fastapi_app import create_app
from config import settings

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
'''
    
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(main_content)
    
    print("✅ 核心文件创建完成")

def create_tool_layer():
    """创建工具层文件"""
    
    # 图片处理工具
    image_processor_content = '''"""
图片处理工具 - Sharp封装
"""
from PIL import Image, ImageOps, ImageDraw, ImageFont
from typing import Optional, Tuple, Dict, Any
from types import ImageMetadata, ProcessingParams, ImageFormat
import os

class ImageProcessor:
    """图片处理器"""
    
    def __init__(self):
        self.supported_formats = {
            ImageFormat.JPEG: 'JPEG',
            ImageFormat.PNG: 'PNG', 
            ImageFormat.WEBP: 'WEBP',
            ImageFormat.BMP: 'BMP',
            ImageFormat.TIFF: 'TIFF',
            ImageFormat.GIF: 'GIF'
        }
    
    def get_image_info(self, file_path: str) -> ImageMetadata:
        """获取图片信息"""
        try:
            with Image.open(file_path) as img:
                return ImageMetadata(
                    width=img.width,
                    height=img.height,
                    format=ImageFormat(img.format),
                    mode=ImageMode(img.mode),
                    file_size=os.path.getsize(file_path),
                    dpi_x=img.info.get('dpi', (72, 72))[0],
                    dpi_y=img.info.get('dpi', (72, 72))[1],
                    has_transparency=img.mode in ('RGBA', 'LA', 'P')
                )
        except Exception as e:
            raise ValueError(f"无法读取图片信息: {e}")
    
    def convert_image(self, input_path: str, output_path: str, params: ProcessingParams) -> ImageMetadata:
        """转换图片"""
        try:
            with Image.open(input_path) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 调整大小
                if params.resize_width or params.resize_height:
                    img = self._resize_image(img, params.resize_width, params.resize_height)
                
                # 添加水印
                if params.watermark:
                    img = self._add_watermark(img)
                
                # 保存图片
                save_kwargs = self._get_save_kwargs(params)
                img.save(output_path, format=self.supported_formats[params.target_format], **save_kwargs)
                
                return self.get_image_info(output_path)
                
        except Exception as e:
            raise ValueError(f"图片转换失败: {e}")
    
    def _resize_image(self, img: Image.Image, width: Optional[int], height: Optional[int]) -> Image.Image:
        """调整图片大小"""
        if width and height:
            return img.resize((width, height), Image.Resampling.LANCZOS)
        elif width:
            ratio = width / img.width
            new_height = int(img.height * ratio)
            return img.resize((width, new_height), Image.Resampling.LANCZOS)
        elif height:
            ratio = height / img.height
            new_width = int(img.width * ratio)
            return img.resize((new_width, height), Image.Resampling.LANCZOS)
        return img
    
    def _add_watermark(self, img: Image.Image) -> Image.Image:
        """添加水印"""
        try:
            watermark_text = "ImageConvert"
            watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = img.width - text_width - 10
            y = img.height - text_height - 10
            
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
            
            return Image.alpha_composite(img.convert('RGBA'), watermark)
        except Exception:
            return img
    
    def _get_save_kwargs(self, params: ProcessingParams) -> Dict[str, Any]:
        """获取保存参数"""
        kwargs = {}
        if params.target_format in [ImageFormat.JPEG, ImageFormat.WEBP]:
            kwargs['quality'] = params.quality
            kwargs['optimize'] = True
        return kwargs
    
    def create_thumbnail(self, input_path: str, output_path: str, size: Tuple[int, int] = (100, 100)) -> str:
        """创建缩略图"""
        try:
            with Image.open(input_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(output_path, "JPEG", quality=85)
                return output_path
        except Exception as e:
            raise ValueError(f"创建缩略图失败: {e}")
'''
    
    with open("tool/image/processor.py", "w", encoding="utf-8") as f:
        f.write(image_processor_content)
    
    # 文件管理工具
    file_manager_content = '''"""
文件管理工具
"""
import os
import uuid
import mimetypes
from typing import Optional, List, Tuple
from pathlib import Path
from types import FileInfo

class FileManager:
    """文件管理器"""
    
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def save_uploaded_file(self, file_content: bytes, original_filename: str) -> FileInfo:
        """保存上传的文件"""
        # 验证文件
        self._validate_file(file_content, original_filename)
        
        # 生成唯一文件名
        file_extension = Path(original_filename).suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # 创建目录
        file_dir = os.path.join(self.upload_dir, "uploads")
        os.makedirs(file_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(file_dir, unique_filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return FileInfo(
            filename=unique_filename,
            file_size=len(file_content),
            file_path=file_path,
            mime_type=mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
        )
    
    def save_converted_file(self, file_content: bytes, original_filename: str, target_format: str) -> FileInfo:
        """保存转换后的文件"""
        # 生成文件名
        name_without_ext = Path(original_filename).stem
        converted_filename = f"{name_without_ext}_converted.{target_format.lower()}"
        
        # 创建目录
        file_dir = os.path.join(self.upload_dir, "converted")
        os.makedirs(file_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(file_dir, converted_filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return FileInfo(
            filename=converted_filename,
            file_size=len(file_content),
            file_path=file_path,
            mime_type=f"image/{target_format.lower()}"
        )
    
    def _validate_file(self, file_content: bytes, filename: str) -> None:
        """验证文件"""
        # 检查文件大小
        if len(file_content) > self.max_file_size:
            raise ValueError(f"文件大小超过限制 ({self.max_file_size // 1024 // 1024}MB)")
        
        # 检查文件扩展名
        file_extension = Path(filename).suffix.lower()
        if file_extension not in self.allowed_extensions:
            raise ValueError(f"不支持的文件格式: {file_extension}")
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """获取文件信息"""
        if not os.path.exists(file_path):
            return None
        
        return FileInfo(
            filename=os.path.basename(file_path),
            file_size=os.path.getsize(file_path),
            file_path=file_path,
            mime_type=mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        )
'''
    
    with open("tool/file/manager.py", "w", encoding="utf-8") as f:
        f.write(file_manager_content)
    
    print("✅ 工具层文件创建完成")

def main():
    """主函数"""
    print("🚀 开始创建新的项目结构...")
    
    # 创建目录结构
    create_directory_structure()
    
    # 创建核心文件
    create_core_files()
    
    # 创建工具层
    create_tool_layer()
    
    print("🎉 项目结构创建完成!")

if __name__ == "__main__":
    main()
