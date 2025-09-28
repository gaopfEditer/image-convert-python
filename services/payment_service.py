import uuid
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models import PaymentRecord, PaymentStatus, PaymentMethod, UserRole
from framework.schemas import PaymentCreate, PaymentResponse
from config import settings

class PaymentService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_payment(self, user_id: int, payment_data: PaymentCreate) -> PaymentResponse:
        """创建支付订单"""
        # 生成订单ID
        order_id = f"IMG_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # 根据目标角色确定价格
        prices = {
            UserRole.VIP: settings.vip_price,
            UserRole.SVIP: settings.svip_price
        }
        
        amount = prices.get(payment_data.target_role)
        if not amount:
            raise ValueError("无效的会员等级")
        
        # 创建支付记录
        payment_record = PaymentRecord(
            user_id=user_id,
            order_id=order_id,
            amount=amount,
            payment_method=payment_data.payment_method,
            status=PaymentStatus.PENDING,
            target_role=payment_data.target_role
        )
        
        self.db.add(payment_record)
        self.db.commit()
        self.db.refresh(payment_record)
        
        return PaymentResponse(
            id=payment_record.id,
            order_id=payment_record.order_id,
            amount=payment_record.amount,
            payment_method=payment_record.payment_method,
            status=payment_record.status,
            target_role=payment_record.target_role,
            created_at=payment_record.created_at
        )
    
    def create_alipay_payment(self, payment_record: PaymentRecord) -> Dict[str, Any]:
        """创建支付宝支付"""
        try:
            from alipay import AliPay
            
            alipay = AliPay(
                appid=settings.alipay_app_id,
                app_notify_url="http://your-domain.com/api/payment/alipay/callback",
                app_private_key_string=settings.alipay_private_key,
                alipay_public_key_string=settings.alipay_public_key,
                sign_type="RSA2",
                debug=False
            )
            
            order_string = alipay.api_alipay_trade_page_pay(
                out_trade_no=payment_record.order_id,
                total_amount=str(payment_record.amount),
                subject=f"图片转换服务 - {payment_record.target_role.value.upper()}会员",
                return_url="http://your-domain.com/payment/success",
                notify_url="http://your-domain.com/api/payment/alipay/callback"
            )
            
            return {
                "payment_url": f"{settings.alipay_gateway}?{order_string}",
                "order_id": payment_record.order_id
            }
            
        except ImportError:
            raise ValueError("支付宝SDK未安装")
        except Exception as e:
            raise ValueError(f"创建支付宝支付失败: {str(e)}")
    
    def create_wechat_payment(self, payment_record: PaymentRecord) -> Dict[str, Any]:
        """创建微信支付"""
        try:
            from wechatpay_python import WeChatPay
            
            wechat_pay = WeChatPay(
                appid=settings.wechat_app_id,
                mch_id=settings.wechat_mch_id,
                api_key=settings.wechat_api_key,
                cert_path=settings.wechat_cert_path,
                key_path=settings.wechat_key_path
            )
            
            # 创建统一下单
            order_data = {
                "out_trade_no": payment_record.order_id,
                "total_fee": int(payment_record.amount * 100),  # 转换为分
                "body": f"图片转换服务 - {payment_record.target_role.value.upper()}会员",
                "trade_type": "NATIVE",
                "notify_url": "http://your-domain.com/api/payment/wechat/callback"
            }
            
            result = wechat_pay.unified_order(order_data)
            
            return {
                "qr_code": result.get("code_url"),
                "order_id": payment_record.order_id
            }
            
        except ImportError:
            raise ValueError("微信支付SDK未安装")
        except Exception as e:
            raise ValueError(f"创建微信支付失败: {str(e)}")
    
    def verify_alipay_callback(self, callback_data: Dict[str, Any]) -> bool:
        """验证支付宝回调"""
        try:
            from alipay import AliPay
            
            alipay = AliPay(
                appid=settings.alipay_app_id,
                app_notify_url="",
                app_private_key_string=settings.alipay_private_key,
                alipay_public_key_string=settings.alipay_public_key,
                sign_type="RSA2",
                debug=False
            )
            
            return alipay.verify(callback_data, callback_data.get("sign"))
            
        except Exception:
            return False
    
    def verify_wechat_callback(self, callback_data: Dict[str, Any]) -> bool:
        """验证微信支付回调"""
        try:
            # 获取签名
            sign = callback_data.pop("sign", "")
            
            # 排序参数
            sorted_params = sorted(callback_data.items())
            
            # 拼接字符串
            string_sign_temp = "&".join([f"{k}={v}" for k, v in sorted_params if v])
            string_sign_temp += f"&key={settings.wechat_api_key}"
            
            # 计算签名
            calculated_sign = hashlib.md5(string_sign_temp.encode()).hexdigest().upper()
            
            return calculated_sign == sign
            
        except Exception:
            return False
    
    def update_payment_status(self, order_id: str, status: PaymentStatus, transaction_id: str = None) -> bool:
        """更新支付状态"""
        payment_record = self.db.query(PaymentRecord).filter(
            PaymentRecord.order_id == order_id
        ).first()
        
        if not payment_record:
            return False
        
        payment_record.status = status
        if transaction_id:
            payment_record.transaction_id = transaction_id
        
        self.db.commit()
        return True
    
    def get_payment_by_order_id(self, order_id: str) -> Optional[PaymentRecord]:
        """根据订单ID获取支付记录"""
        return self.db.query(PaymentRecord).filter(
            PaymentRecord.order_id == order_id
        ).first()
    
    def get_user_payments(self, user_id: int, limit: int = 10, offset: int = 0) -> list:
        """获取用户支付记录"""
        return self.db.query(PaymentRecord).filter(
            PaymentRecord.user_id == user_id
        ).order_by(PaymentRecord.created_at.desc()).offset(offset).limit(limit).all()
    
    def process_payment_success(self, order_id: str) -> bool:
        """处理支付成功"""
        payment_record = self.get_payment_by_order_id(order_id)
        if not payment_record or payment_record.status != PaymentStatus.SUCCESS:
            return False
        
        # 更新用户会员等级
        from services.user_service import UserService
        user_service = UserService(self.db)
        success = user_service.update_user_role(payment_record.user_id, payment_record.target_role)
        
        return success
