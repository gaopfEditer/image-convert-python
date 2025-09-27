from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from tools.database.database import get_db
from schemas import PaymentCreate, PaymentResponse, MessageResponse
from services.payment_service import PaymentService
from services.wechat_pay_service import WeChatPayService
from services.permission_service import PermissionService
from auth import get_current_active_user
from models import User, PaymentStatus
from config import settings
import json

router = APIRouter(prefix="/payment", tags=["支付"])

@router.post("/create", response_model=PaymentResponse, summary="创建支付订单")
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建支付订单"""
    payment_service = PaymentService(db)
    
    try:
        payment = payment_service.create_payment(current_user.id, payment_data)
        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/alipay/create", summary="创建支付宝支付")
async def create_alipay_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建支付宝支付"""
    payment_service = PaymentService(db)
    
    try:
        # 创建支付记录
        payment = payment_service.create_payment(current_user.id, payment_data)
        
        # 创建支付宝支付
        alipay_data = payment_service.create_alipay_payment(payment)
        
        return {
            "payment_url": alipay_data["payment_url"],
            "order_id": alipay_data["order_id"],
            "amount": payment.amount,
            "target_role": payment.target_role.value
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/wechat/create", summary="创建微信支付")
async def create_wechat_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建微信支付"""
    payment_service = PaymentService(db)
    wechat_pay_service = WeChatPayService()
    
    try:
        # 创建支付记录
        payment = payment_service.create_payment(current_user.id, payment_data)
        
        # 创建微信统一下单
        total_fee = int(payment.amount * 100)  # 转换为分
        body = f"图片转换服务 - {payment.target_role.value.upper()}会员"
        
        result = wechat_pay_service.create_unified_order(
            out_trade_no=payment.order_id,
            total_fee=total_fee,
            body=body,
            trade_type="NATIVE"  # 扫码支付
        )
        
        if result["success"]:
            return {
                "qr_code": result["code_url"],
                "order_id": payment.order_id,
                "amount": payment.amount,
                "target_role": payment.target_role.value,
                "prepay_id": result["prepay_id"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"创建微信支付失败: {result['error']}"
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/alipay/callback", summary="支付宝支付回调")
async def alipay_callback(request: Request, db: Session = Depends(get_db)):
    """支付宝支付回调"""
    payment_service = PaymentService(db)
    
    # 获取回调数据
    form_data = await request.form()
    callback_data = dict(form_data)
    
    # 验证签名
    if not payment_service.verify_alipay_callback(callback_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="签名验证失败"
        )
    
    # 更新支付状态
    order_id = callback_data.get("out_trade_no")
    trade_status = callback_data.get("trade_status")
    transaction_id = callback_data.get("trade_no")
    
    if trade_status == "TRADE_SUCCESS":
        payment_service.update_payment_status(
            order_id, PaymentStatus.SUCCESS, transaction_id
        )
        # 处理支付成功
        payment_service.process_payment_success(order_id)
        return {"status": "success"}
    else:
        payment_service.update_payment_status(order_id, PaymentStatus.FAILED)
        return {"status": "failed"}

@router.post("/wechat/callback", summary="微信支付回调")
async def wechat_callback(request: Request, db: Session = Depends(get_db)):
    """微信支付回调"""
    payment_service = PaymentService(db)
    wechat_pay_service = WeChatPayService()
    
    try:
        # 获取回调数据
        body = await request.body()
        xml_data = body.decode('utf-8')
        
        # 验证回调
        result = wechat_pay_service.verify_notify(xml_data)
        
        if not result["success"]:
            return {
                "return_code": "FAIL",
                "return_msg": result["error"]
            }
        
        # 更新支付状态
        order_id = result["out_trade_no"]
        transaction_id = result["transaction_id"]
        
        payment_service.update_payment_status(
            order_id, PaymentStatus.SUCCESS, transaction_id
        )
        
        # 处理支付成功
        payment_service.process_payment_success(order_id)
        
        return {
            "return_code": "SUCCESS",
            "return_msg": "OK"
        }
        
    except Exception as e:
        return {
            "return_code": "FAIL",
            "return_msg": f"处理回调失败: {str(e)}"
        }

@router.get("/orders", response_model=list[PaymentResponse], summary="获取支付记录")
async def get_payment_orders(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户支付记录"""
    payment_service = PaymentService(db)
    return payment_service.get_user_payments(current_user.id, limit, offset)

@router.get("/upgrade-options", summary="获取升级选项")
async def get_upgrade_options(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取会员升级选项"""
    permission_service = PermissionService(db)
    return permission_service.get_upgrade_options(current_user.role)

@router.get("/role-benefits", summary="获取角色权益")
async def get_role_benefits(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前用户角色权益"""
    permission_service = PermissionService(db)
    return permission_service.get_role_benefits(current_user.role)

@router.get("/wechat/query/{order_id}", summary="查询微信支付订单")
async def query_wechat_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """查询微信支付订单状态"""
    wechat_pay_service = WeChatPayService()
    
    try:
        result = wechat_pay_service.query_order(out_trade_no=order_id)
        
        if result["success"]:
            return {
                "order_id": order_id,
                "trade_state": result["trade_state"],
                "transaction_id": result.get("transaction_id"),
                "total_fee": result.get("total_fee"),
                "time_end": result.get("time_end")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询订单失败: {str(e)}"
        )

@router.post("/wechat/close/{order_id}", summary="关闭微信支付订单")
async def close_wechat_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """关闭微信支付订单"""
    wechat_pay_service = WeChatPayService()
    
    try:
        result = wechat_pay_service.close_order(order_id)
        
        if result["success"]:
            return {"message": "订单关闭成功"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"关闭订单失败: {str(e)}"
        )
