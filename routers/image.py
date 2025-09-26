from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from schemas import ImageConvertRequest, ConversionRecordResponse, MessageResponse, UsageStatsResponse
from services.image_service import ImageService
from services.permission_service import PermissionService
from services.user_service import UserService
from auth import get_current_active_user
from models import User
from config import settings
import os
import uuid

router = APIRouter(prefix="/image", tags=["图片转换"])

@router.get("/formats", summary="获取支持的图片格式")
async def get_supported_formats():
    """获取支持的图片格式列表"""
    image_service = ImageService(None)
    return image_service.get_supported_formats()

@router.post("/convert", summary="转换图片格式")
async def convert_image(
    file: UploadFile = File(...),
    target_format: str = Form(...),
    quality: int = Form(95),
    resize_width: int = Form(None),
    resize_height: int = Form(None),
    watermark: bool = Form(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """转换图片格式"""
    # 检查权限
    permission_service = PermissionService(db)
    can_convert, error_message = permission_service.check_conversion_permission(current_user.id)
    if not can_convert:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_message
        )
    
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
    upload_filename = f"{uuid.uuid4().hex}.{file_extension}"
    upload_path = os.path.join(settings.upload_dir, "uploads", upload_filename)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    
    with open(upload_path, "wb") as f:
        f.write(file_content)
    
    try:
        # 创建转换请求
        convert_request = ImageConvertRequest(
            target_format=target_format,
            quality=quality,
            resize={"width": resize_width, "height": resize_height} if resize_width or resize_height else None,
            watermark=watermark
        )
        
        # 执行转换
        image_service = ImageService(db)
        success, output_path, error_message = image_service.convert_image(
            upload_path, target_format, current_user.id, convert_request
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"转换失败: {error_message}"
            )
        
        # 记录使用日志
        permission_service.log_usage(current_user.id, "image_convert")
        
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

@router.get("/info", summary="获取图片信息")
async def get_image_info(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """获取图片信息"""
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
            detail=f"不支持的文件格式"
        )
    
    # 保存临时文件
    file_content = await file.read()
    temp_filename = f"temp_{uuid.uuid4().hex}.{file_extension}"
    temp_path = os.path.join(settings.upload_dir, "temp", temp_filename)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    
    try:
        with open(temp_path, "wb") as f:
            f.write(file_content)
        
        # 获取图片信息
        image_service = ImageService(None)
        info = image_service.get_image_info(temp_path)
        
        return info
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/usage", response_model=UsageStatsResponse, summary="获取使用统计")
async def get_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户使用统计"""
    user_service = UserService(db)
    return user_service.get_usage_stats(current_user.id)

@router.get("/records", response_model=list[ConversionRecordResponse], summary="获取转换记录")
async def get_conversion_records(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户转换记录"""
    from models import ConversionRecord
    
    records = db.query(ConversionRecord).filter(
        ConversionRecord.user_id == current_user.id
    ).order_by(ConversionRecord.created_at.desc()).offset(offset).limit(limit).all()
    
    return records
