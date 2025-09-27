"""
转换记录实体
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from types import ConversionStatus, ImageFormat, ImageMode

@dataclass
class ConversionRecord:
    """转换记录实体"""
    
    # 基本信息
    id: Optional[int] = None
    user_id: int = 0
    original_filename: str = ""
    target_format: str = ""
    conversion_time: float = 0.0
    status: ConversionStatus = ConversionStatus.PENDING
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    
    # 原图信息
    original_file_path: Optional[str] = None
    original_file_size: Optional[int] = None
    original_format: Optional[str] = None
    original_width: Optional[int] = None
    original_height: Optional[int] = None
    original_mode: Optional[str] = None
    
    # 生成图信息
    converted_file_path: Optional[str] = None
    converted_file_size: Optional[int] = None
    converted_width: Optional[int] = None
    converted_height: Optional[int] = None
    converted_mode: Optional[str] = None
    
    # 处理参数
    quality: Optional[int] = None
    resize_width: Optional[int] = None
    resize_height: Optional[int] = None
    watermark: bool = False
    compression_ratio: Optional[float] = None
    
    def is_successful(self) -> bool:
        """是否转换成功"""
        return self.status == ConversionStatus.SUCCESS
    
    def get_compression_saved_bytes(self) -> int:
        """获取压缩节省的字节数"""
        if not self.original_file_size or not self.converted_file_size:
            return 0
        return self.original_file_size - self.converted_file_size
    
    def get_compression_percentage(self) -> float:
        """获取压缩百分比"""
        if not self.original_file_size or self.original_file_size == 0:
            return 0.0
        return (1 - self.converted_file_size / self.original_file_size) * 100
    
    def get_dimension_change_description(self) -> str:
        """获取尺寸变化描述"""
        if not all([self.original_width, self.original_height, self.converted_width, self.converted_height]):
            return "未知"
        
        if self.original_width == self.converted_width and self.original_height == self.converted_height:
            return "无变化"
        
        orig_ratio = self.original_width / self.original_height
        conv_ratio = self.converted_width / self.converted_height
        
        if abs(orig_ratio - conv_ratio) < 0.01:
            scale = self.converted_width / self.original_width
            return f"等比例缩放 {scale:.1%}"
        else:
            return f"{self.original_width}×{self.original_height} → {self.converted_width}×{self.converted_height}"
    
    def get_processing_summary(self) -> dict:
        """获取处理摘要"""
        return {
            "format_conversion": f"{self.original_format} → {self.target_format}",
            "quality": self.quality,
            "dimensions": self.get_dimension_change_description(),
            "watermark": "是" if self.watermark else "否",
            "compression_ratio": f"{self.compression_ratio:.1f}%" if self.compression_ratio else "未知",
            "file_size_change": f"{self.original_file_size} → {self.converted_file_size} bytes" if self.original_file_size and self.converted_file_size else "未知",
            "time_taken": f"{self.conversion_time:.2f}s"
        }
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "original_filename": self.original_filename,
            "target_format": self.target_format,
            "conversion_time": self.conversion_time,
            "status": self.status.value,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "original_image": {
                "file_path": self.original_file_path,
                "file_size": self.original_file_size,
                "width": self.original_width,
                "height": self.original_height,
                "format": self.original_format,
                "mode": self.original_mode
            },
            "converted_image": {
                "file_path": self.converted_file_path,
                "file_size": self.converted_file_size,
                "width": self.converted_width,
                "height": self.converted_height,
                "format": self.target_format,
                "mode": self.converted_mode
            },
            "processing_params": {
                "quality": self.quality,
                "resize_width": self.resize_width,
                "resize_height": self.resize_height,
                "watermark": self.watermark,
                "original_size": [self.original_width, self.original_height] if self.original_width and self.original_height else None,
                "converted_size": [self.converted_width, self.converted_height] if self.converted_width and self.converted_height else None
            },
            "comparison_stats": {
                "compression_ratio": self.compression_ratio,
                "size_reduction": self.get_compression_saved_bytes(),
                "size_reduction_percent": self.get_compression_percentage(),
                "dimension_change": self.get_dimension_change_description()
            }
        }
