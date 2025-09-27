"""
图片转换业务服务
"""
from typing import Tuple, Optional
import time
import os

from tool.image.processor import ImageProcessor
from tool.file.manager import FileManager
from infra.database.repositories.image_repo import ImageRepository
from infra.cache.cache_service import CacheService
from business.permission.service import PermissionService
from types import ProcessingParams, ImageMetadata, ConversionStatus
from domain.entities.conversion import ConversionRecord
from domain.entities.user import User

class ImageConversionService:
    """图片转换业务服务"""
    
    def __init__(
        self,
        image_processor: ImageProcessor,
        file_manager: FileManager,
        image_repo: ImageRepository,
        cache_service: CacheService,
        permission_service: PermissionService
    ):
        self.image_processor = image_processor
        self.file_manager = file_manager
        self.image_repo = image_repo
        self.cache_service = cache_service
        self.permission_service = permission_service
    
    async def convert_image(
        self,
        user: User,
        file_content: bytes,
        original_filename: str,
        params: ProcessingParams
    ) -> Tuple[bool, Optional[ConversionRecord], Optional[str]]:
        """转换图片"""
        
        # 检查权限
        can_convert, error_message = await self.permission_service.check_conversion_permission(user.id)
        if not can_convert:
            return False, None, error_message
        
        start_time = time.time()
        
        try:
            # 保存上传的文件
            original_file_info = self.file_manager.save_uploaded_file(file_content, original_filename)
            
            # 转换图片
            converted_file_info = await self._convert_image_file(
                original_file_info.file_path,
                original_filename,
                params
            )
            
            # 计算转换时间
            conversion_time = time.time() - start_time
            
            # 创建转换记录
            conversion_record = await self._create_conversion_record(
                user=user,
                original_file_info=original_file_info,
                converted_file_info=converted_file_info,
                params=params,
                conversion_time=conversion_time
            )
            
            # 记录使用日志
            await self.permission_service.log_usage(user.id, "image_convert")
            
            # 缓存结果
            await self.cache_service.set_conversion_result(
                conversion_record.id,
                conversion_record
            )
            
            return True, conversion_record, None
            
        except Exception as e:
            # 记录失败的转换
            await self._create_failed_conversion_record(
                user=user,
                original_filename=original_filename,
                params=params,
                error_message=str(e),
                conversion_time=time.time() - start_time
            )
            
            return False, None, str(e)
    
    async def _convert_image_file(
        self,
        input_path: str,
        original_filename: str,
        params: ProcessingParams
    ) -> FileInfo:
        """转换图片文件"""
        
        # 生成输出文件路径
        name_without_ext = os.path.splitext(original_filename)[0]
        output_filename = f"{name_without_ext}_converted.{params.target_format.value.lower()}"
        
        # 转换图片
        converted_metadata = self.image_processor.convert_image(
            input_path,
            output_filename,
            params
        )
        
        # 保存转换后的文件
        with open(output_filename, 'rb') as f:
            file_content = f.read()
        
        converted_file_info = self.file_manager.save_converted_file(
            file_content,
            original_filename,
            params.target_format.value
        )
        
        # 清理临时文件
        os.remove(output_filename)
        
        return converted_file_info
    
    async def _create_conversion_record(
        self,
        user: User,
        original_file_info: FileInfo,
        converted_file_info: FileInfo,
        params: ProcessingParams,
        conversion_time: float
    ) -> ConversionRecord:
        """创建转换记录"""
        
        # 获取原图信息
        original_metadata = self.image_processor.get_image_info(original_file_info.file_path)
        converted_metadata = self.image_processor.get_image_info(converted_file_info.file_path)
        
        # 计算压缩比例
        compression_ratio = (
            (1 - converted_file_info.file_size / original_file_info.file_size) * 100
            if original_file_info.file_size > 0 else 0
        )
        
        # 创建转换记录实体
        conversion_record = ConversionRecord(
            user_id=user.id,
            original_filename=original_file_info.filename,
            target_format=params.target_format.value,
            original_file_path=original_file_info.file_path,
            original_file_size=original_file_info.file_size,
            original_format=original_metadata.format.value,
            original_width=original_metadata.width,
            original_height=original_metadata.height,
            original_mode=original_metadata.mode.value,
            converted_file_path=converted_file_info.file_path,
            converted_file_size=converted_file_info.file_size,
            converted_width=converted_metadata.width,
            converted_height=converted_metadata.height,
            converted_mode=converted_metadata.mode.value,
            quality=params.quality,
            resize_width=params.resize_width,
            resize_height=params.resize_height,
            watermark=params.watermark,
            compression_ratio=compression_ratio,
            conversion_time=conversion_time,
            status=ConversionStatus.SUCCESS
        )
        
        # 保存到数据库
        await self.image_repo.create_conversion_record(conversion_record)
        
        return conversion_record
    
    async def _create_failed_conversion_record(
        self,
        user: User,
        original_filename: str,
        params: ProcessingParams,
        error_message: str,
        conversion_time: float
    ) -> None:
        """创建失败的转换记录"""
        
        failed_record = ConversionRecord(
            user_id=user.id,
            original_filename=original_filename,
            target_format=params.target_format.value,
            conversion_time=conversion_time,
            status=ConversionStatus.FAILED,
            error_message=error_message
        )
        
        await self.image_repo.create_conversion_record(failed_record)
    
    async def get_conversion_records(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
        format_filter: Optional[str] = None
    ) -> List[ConversionRecord]:
        """获取转换记录列表"""
        
        # 尝试从缓存获取
        cache_key = f"conversion_records:{user_id}:{limit}:{offset}:{format_filter}"
        cached_records = await self.cache_service.get(cache_key)
        
        if cached_records:
            return cached_records
        
        # 从数据库获取
        records = await self.image_repo.get_conversion_records(
            user_id=user_id,
            limit=limit,
            offset=offset,
            format_filter=format_filter
        )
        
        # 缓存结果
        await self.cache_service.set(cache_key, records, ttl=300)
        
        return records
    
    async def get_conversion_record_detail(
        self,
        user_id: int,
        record_id: int
    ) -> Optional[ConversionRecord]:
        """获取转换记录详情"""
        
        # 尝试从缓存获取
        cache_key = f"conversion_record:{record_id}"
        cached_record = await self.cache_service.get(cache_key)
        
        if cached_record:
            return cached_record
        
        # 从数据库获取
        record = await self.image_repo.get_conversion_record_by_id(record_id, user_id)
        
        if record:
            # 缓存结果
            await self.cache_service.set(cache_key, record, ttl=600)
        
        return record
    
    async def delete_conversion_record(
        self,
        user_id: int,
        record_id: int
    ) -> bool:
        """删除转换记录"""
        
        # 获取记录
        record = await self.image_repo.get_conversion_record_by_id(record_id, user_id)
        if not record:
            return False
        
        # 删除相关文件
        if record.original_file_path and os.path.exists(record.original_file_path):
            self.file_manager.delete_file(record.original_file_path)
        
        if record.converted_file_path and os.path.exists(record.converted_file_path):
            self.file_manager.delete_file(record.converted_file_path)
        
        # 删除数据库记录
        await self.image_repo.delete_conversion_record(record_id, user_id)
        
        # 清除缓存
        await self.cache_service.delete(f"conversion_record:{record_id}")
        
        return True
