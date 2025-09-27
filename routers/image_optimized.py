from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import Optional
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from tools.database.database import get_db
from schemas import ImageConvertRequest, ConversionRecordResponse, MessageResponse, UsageStatsResponse
from services.image_service import ImageService
from services.permission_service import PermissionService
from services.user_service import UserService
from auth import get_current_active_user
from models import User
from config import settings
from PIL import Image
import os
import uuid

router = APIRouter(prefix="/image", tags=["图片转换"])

# ==================== 公开接口（不需要token） ====================

@router.get("/formats", summary="获取支持的图片格式")
async def get_supported_formats():
    """获取支持的图片格式列表 - 公开接口"""
    image_service = ImageService(None)
    return image_service.get_supported_formats()

@router.get("/info", summary="获取图片信息")
async def get_image_info(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """获取图片信息 - 公开接口"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式，支持的格式: {', '.join(settings.allowed_extensions)}"
        )
    
    # 检查文件大小
    file_content = await file.read()
    if len(file_content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制({settings.max_file_size // 1024 // 1024}MB)"
        )
    
    image_service = ImageService(db)
    try:
        info = image_service.get_image_info(file_content, file.filename)
        return info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"获取图片信息失败: {str(e)}"
        )

@router.get("/preview/{filename}", summary="预览图片")
async def preview_image(filename: str):
    """预览图片 - 公开接口"""
    # 构建文件路径
    file_path = os.path.join(settings.upload_dir, "converted", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片不存在"
        )
    
    return FileResponse(file_path)

@router.get("/download/{filename}", summary="下载图片")
async def download_image(filename: str):
    """下载图片 - 公开接口"""
    # 构建文件路径
    file_path = os.path.join(settings.upload_dir, "converted", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片不存在"
        )
    
    return FileResponse(file_path, filename=filename)

@router.post("/compress", summary="压缩图片")
async def compress_image(
    file: UploadFile = File(...),
    quality: int = Form(80),
    resize_width: int = Form(0),
    resize_height: int = Form(0),
    maxWidth: int = Form(0),  # 支持maxWidth参数
    maxHeight: int = Form(0),  # 支持maxHeight参数
    db: Session = Depends(get_db)
):
    """压缩图片 - 公开接口，专门用于图片压缩"""
    # 验证文件类型
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式，支持的格式: {', '.join(settings.allowed_extensions)}"
        )
    
    # 检查文件大小
    file_content = await file.read()
    if len(file_content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制({settings.max_file_size // 1024 // 1024}MB)"
        )
    
    # 验证质量参数
    if not 1 <= quality <= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="质量参数必须在1-100之间"
        )
    
    # 保存上传的文件
    import uuid
    upload_filename = f"{uuid.uuid4().hex}.{file_extension}"
    upload_path = os.path.join(settings.upload_dir, "uploads", upload_filename)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    
    with open(upload_path, "wb") as f:
        f.write(file_content)
    
    try:
        # 获取原图尺寸
        with Image.open(upload_path) as img:
            original_width, original_height = img.size
            
        # 优先使用maxWidth/maxHeight参数，如果没有则使用resize_width/resize_height
        final_width = maxWidth if maxWidth and maxWidth > 0 else (resize_width if resize_width and resize_width > 0 else None)
        final_height = maxHeight if maxHeight and maxHeight > 0 else (resize_height if resize_height and resize_height > 0 else None)
            
        # 如果设置的尺寸比原图大，则不进行尺寸调整（避免放大）
        if final_width and final_width > original_width:
            final_width = None
        if final_height and final_height > original_height:
            final_height = None
            
        # 对于PNG格式，建议转换为JPEG以获得更好的压缩效果
        target_format = file_extension.upper()
        if target_format == 'PNG' and quality < 90:
            target_format = 'JPEG'
            file_extension = 'jpg'
        
        # 创建压缩请求
        from schemas import ImageConvertRequest
        resize_params = None
        if final_width or final_height:
            resize_params = {"width": final_width, "height": final_height}
            
        compress_request = ImageConvertRequest(
            target_format=target_format,
            quality=quality,
            resize=resize_params,
            watermark=False  # 压缩接口默认不添加水印
        )
        
        # 执行压缩
        image_service = ImageService(db)
        # 确保格式正确（JPG -> JPEG）
        target_format = file_extension.upper()
        if target_format == 'JPG':
            target_format = 'JPEG'
        
        success, output_path, error_message = image_service.convert_image(
            upload_path, target_format, None, compress_request  # 公开接口使用None
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"压缩失败: {error_message}"
            )
        
        # 计算压缩信息
        original_size = len(file_content)
        compressed_size = os.path.getsize(output_path)
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        # 获取最终图片尺寸
        with Image.open(output_path) as final_img:
            final_width, final_height = final_img.size
        
        # 生成文件URL
        filename = f"compressed_{file.filename.split('.')[0]}.{file_extension}"
        file_url = f"/static/converted/{os.path.basename(output_path)}"
        
        # 返回压缩结果信息
        return {
            "success": True,
            "message": "压缩成功",
            "file_url": file_url,
            "filename": filename,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": round(compression_ratio, 2),
            "quality": quality,
            "original_dimensions": {
                "width": original_width,
                "height": original_height
            },
            "final_dimensions": {
                "width": final_width,
                "height": final_height
            },
            "format": file_extension.upper(),
            "size_changed": original_size != compressed_size,
            "dimensions_changed": (original_width, original_height) != (final_width, final_height)
        }
        
    finally:
        # 清理上传的临时文件
        if os.path.exists(upload_path):
            os.remove(upload_path)

@router.post("/convert", summary="转换图片格式")
async def convert_image(
    file: UploadFile = File(...),
    target_format: str = Form(...),
    quality: int = Form(95),
    resize_width: int = Form(None),
    resize_height: int = Form(None),
    watermark: bool = Form(False),
    db: Session = Depends(get_db)
):
    """转换图片格式 - 公开接口"""
    
    # 验证文件类型
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式，支持的格式: {', '.join(settings.allowed_extensions)}"
        )
    
    # 检查文件大小
    file_content = await file.read()
    if len(file_content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制({settings.max_file_size // 1024 // 1024}MB)"
        )
    
    # 保存上传的文件
    import uuid
    upload_filename = f"{uuid.uuid4().hex}.{file_extension}"
    upload_path = os.path.join(settings.upload_dir, "uploads", upload_filename)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    
    with open(upload_path, "wb") as f:
        f.write(file_content)
    
    try:
        # 创建转换请求
        from schemas import ImageConvertRequest
        convert_request = ImageConvertRequest(
            target_format=target_format,
            quality=quality,
            resize={"width": resize_width, "height": resize_height} if resize_width or resize_height else None,
            watermark=watermark
        )
        
        # 执行转换
        image_service = ImageService(db)
        success, output_path, error_message = image_service.convert_image(
            upload_path, target_format, None, convert_request  # user_id设为None
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"转换失败: {error_message}"
            )
        
        # 返回转换后的文件
        return FileResponse(
            output_path,
            media_type=f"image/{target_format.lower()}",
            filename=f"converted_{file.filename.split('.')[0]}.{target_format.lower()}"
        )
        
    finally:
        # 清理上传的临时文件
        if os.path.exists(upload_path):
            os.remove(upload_path)

@router.get("/usage", response_model=UsageStatsResponse, summary="获取使用统计")
async def get_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户使用统计 - 需要认证"""
    user_service = UserService(db)
    stats = user_service.get_usage_stats(current_user.id)
    return stats

@router.get("/records", response_model=list[ConversionRecordResponse], summary="获取转换记录")
async def get_conversion_records(
    limit: int = 5,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户转换记录 - 需要认证"""
    image_service = ImageService(db)
    records = image_service.get_conversion_records(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    return records

@router.delete("/records/{record_id}", summary="删除转换记录")
async def delete_conversion_record(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除转换记录 - 需要认证"""
    image_service = ImageService(db)
    success = image_service.delete_conversion_record(record_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在或无权限删除"
        )
    
    return {"message": "删除成功", "success": True}
