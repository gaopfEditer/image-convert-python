"""
图片处理相关Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 图片信息Schema
class ImageInfo(BaseModel):
    filename: str
    format: str
    width: int
    height: int
    file_size: int
    url: str

# 转换结果响应Schema
class ImageConversionResponse(BaseModel):
    success: bool = True
    message: str = "转换成功"
    
    # 原图信息
    original_image: ImageInfo
    
    # 转换后图片信息
    converted_image: ImageInfo
    
    # 处理参数
    processing_params: dict
    
    # 转换统计
    conversion_stats: dict
    
    # 下载链接
    download_url: str

# 图片转换请求Schema
class ImageConvertRequest(BaseModel):
    target_format: str
    quality: Optional[int] = 95  # 图片质量 1-100
    resize: Optional[dict] = None  # {"width": 800, "height": 600}
    watermark: Optional[bool] = False

# 转换记录Schema
class ConversionRecordBase(BaseModel):
    original_filename: str
    original_format: str
    target_format: str
    file_size: int
    conversion_time: float
    status: str = "success"
    error_message: Optional[str] = None

class ConversionRecordCreate(ConversionRecordBase):
    pass

class ConversionRecordResponse(ConversionRecordBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
