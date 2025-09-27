"""
图片处理路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List

from infra.database.connection import get_db
from business.image_conversion.service import ImageConversionService
from business.permission.service import PermissionService
from tool.image.processor import ImageProcessor
from tool.file.manager import FileManager
from infra.database.repositories.image_repo import ImageRepository
from infra.cache.cache_service import CacheService
from framework.schemas.image import ImageConvertRequest, ConversionRecordResponse
from framework.middleware.auth import get_current_user
from types import ProcessingParams, ImageFormat
from config import settings

router = APIRouter(prefix="/image", tags=["图片转换"])

# 依赖注入
def get_image_conversion_service(db: Session = Depends(get_db)) -> ImageConversionService:
    """获取图片转换服务"""
    image_processor = ImageProcessor()
    file_manager = FileManager(settings.storage.upload_dir)
    image_repo = ImageRepository(db)
    cache_service = CacheService()
    permission_service = PermissionService(db)
    
    return ImageConversionService(
        image_processor=image_processor,
        file_manager=file_manager,
        image_repo=image_repo,
        cache_service=cache_service,
        permission_service=permission_service
    )

@router.get("/formats", summary="获取支持的图片格式")
async def get_supported_formats():
    """获取支持的图片格式列表"""
    return [
        {"format": "JPEG", "description": "JPEG图片格式", "extension": "jpg"},
        {"format": "PNG", "description": "PNG图片格式", "extension": "png"},
        {"format": "WEBP", "description": "WebP图片格式", "extension": "webp"},
        {"format": "BMP", "description": "BMP图片格式", "extension": "bmp"},
        {"format": "TIFF", "description": "TIFF图片格式", "extension": "tiff"},
        {"format": "GIF", "description": "GIF图片格式", "extension": "gif"}
    ]

@router.post("/convert", summary="转换图片格式")
async def convert_image(
    file: UploadFile = File(...),
    target_format: str = Form(...),
    quality: int = Form(95),
    resize_width: int = Form(None),
    resize_height: int = Form(None),
    watermark: bool = Form(False),
    current_user = Depends(get_current_user),
    conversion_service: ImageConversionService = Depends(get_image_conversion_service)
):
    """转换图片格式"""
    
    # 验证文件
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.storage.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式，支持的格式: {', '.join(settings.storage.allowed_extensions)}"
        )
    
    # 检查文件大小
    file_content = await file.read()
    if len(file_content) > settings.storage.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制({settings.storage.max_file_size // 1024 // 1024}MB)"
        )
    
    # 创建处理参数
    try:
        processing_params = ProcessingParams(
            target_format=ImageFormat(target_format.upper()),
            quality=quality,
            resize_width=resize_width,
            resize_height=resize_height,
            watermark=watermark
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的目标格式: {target_format}"
        )
    
    # 执行转换
    success, conversion_record, error_message = await conversion_service.convert_image(
        user=current_user,
        file_content=file_content,
        original_filename=file.filename,
        params=processing_params
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"转换失败: {error_message}"
        )
    
    # 返回转换后的文件
    return FileResponse(
        conversion_record.converted_file_path,
        media_type=f"image/{target_format.lower()}",
        filename=f"converted_{file.filename.split('.')[0]}.{target_format.lower()}"
    )

@router.get("/records", summary="获取转换记录列表")
async def get_conversion_records(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    format_filter: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    conversion_service: ImageConversionService = Depends(get_image_conversion_service)
):
    """获取用户转换记录列表"""
    
    records = await conversion_service.get_conversion_records(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        format_filter=format_filter
    )
    
    return [record.to_dict() for record in records]

@router.get("/records/{record_id}", summary="获取转换记录详情")
async def get_conversion_record_detail(
    record_id: int,
    current_user = Depends(get_current_user),
    conversion_service: ImageConversionService = Depends(get_image_conversion_service)
):
    """获取转换记录详细信息"""
    
    record = await conversion_service.get_conversion_record_detail(
        user_id=current_user.id,
        record_id=record_id
    )
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="转换记录不存在"
        )
    
    return record.to_dict()

@router.get("/preview/{record_id}/{image_type}", summary="获取图片预览")
async def get_image_preview(
    record_id: int,
    image_type: str,
    size: str = Query("thumbnail", regex="^(thumbnail|medium|large)$"),
    current_user = Depends(get_current_user),
    conversion_service: ImageConversionService = Depends(get_image_conversion_service)
):
    """获取图片预览"""
    
    record = await conversion_service.get_conversion_record_detail(
        user_id=current_user.id,
        record_id=record_id
    )
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="转换记录不存在"
        )
    
    # 确定文件路径
    if image_type == "original":
        file_path = record.original_file_path
    elif image_type == "converted":
        file_path = record.converted_file_path
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image_type必须是'original'或'converted'"
        )
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片文件不存在"
        )
    
    # 根据尺寸要求调整图片
    if size != "large":
        # 这里可以实现缩略图生成逻辑
        pass
    
    return FileResponse(file_path)

@router.get("/download/{record_id}/{image_type}", summary="下载图片")
async def download_image(
    record_id: int,
    image_type: str,
    current_user = Depends(get_current_user),
    conversion_service: ImageConversionService = Depends(get_image_conversion_service)
):
    """下载图片文件"""
    
    record = await conversion_service.get_conversion_record_detail(
        user_id=current_user.id,
        record_id=record_id
    )
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="转换记录不存在"
        )
    
    # 确定文件路径和文件名
    if image_type == "original":
        file_path = record.original_file_path
        filename = record.original_filename
    elif image_type == "converted":
        file_path = record.converted_file_path
        filename = f"converted_{record.original_filename.split('.')[0]}.{record.target_format.lower()}"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image_type必须是'original'或'converted'"
        )
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片文件不存在"
        )
    
    return FileResponse(file_path, filename=filename)

@router.delete("/records/{record_id}", summary="删除转换记录")
async def delete_conversion_record(
    record_id: int,
    current_user = Depends(get_current_user),
    conversion_service: ImageConversionService = Depends(get_image_conversion_service)
):
    """删除转换记录"""
    
    success = await conversion_service.delete_conversion_record(
        user_id=current_user.id,
        record_id=record_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="转换记录不存在"
        )
    
    return {"message": "删除成功", "success": True}
