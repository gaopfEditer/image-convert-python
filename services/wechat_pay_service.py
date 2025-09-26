import hashlib
import hmac
import xml.etree.ElementTree as ET
import time
import uuid
import requests
from typing import Dict, Any, Optional
from config import settings
import json

class WeChatPayService:
    """微信支付服务"""
    
    def __init__(self):
        self.app_id = settings.wechat_app_id
        self.mch_id = settings.wechat_mch_id
        self.api_key = settings.wechat_api_key
        self.notify_url = settings.wechat_notify_url
        
        # 微信支付API地址
        self.unified_order_url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        self.query_order_url = "https://api.mch.weixin.qq.com/pay/orderquery"
        self.close_order_url = "https://api.mch.weixin.qq.com/pay/closeorder"
        self.refund_url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
    
    def create_unified_order(self, 
                           out_trade_no: str, 
                           total_fee: int, 
                           body: str, 
                           client_ip: str = "127.0.0.1",
                           trade_type: str = "NATIVE") -> Dict[str, Any]:
        """
        创建统一下单
        
        Args:
            out_trade_no: 商户订单号
            total_fee: 订单总金额（分）
            body: 商品描述
            client_ip: 用户IP
            trade_type: 交易类型（NATIVE-扫码支付，JSAPI-公众号支付，APP-APP支付）
        
        Returns:
            统一下单结果
        """
        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
            "body": body,
            "out_trade_no": out_trade_no,
            "total_fee": total_fee,
            "spbill_create_ip": client_ip,
            "notify_url": self.notify_url,
            "trade_type": trade_type
        }
        
        # 生成签名
        params["sign"] = self._generate_sign(params)
        
        # 转换为XML
        xml_data = self._dict_to_xml(params)
        
        try:
            response = requests.post(self.unified_order_url, data=xml_data, timeout=30)
            response.raise_for_status()
            
            # 解析响应
            result = self._xml_to_dict(response.text)
            
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                return {
                    "success": True,
                    "prepay_id": result.get("prepay_id"),
                    "code_url": result.get("code_url"),
                    "trade_type": result.get("trade_type"),
                    "out_trade_no": out_trade_no
                }
            else:
                return {
                    "success": False,
                    "error": result.get("err_code_des", "统一下单失败"),
                    "return_msg": result.get("return_msg")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"请求失败: {str(e)}"
            }
    
    def query_order(self, out_trade_no: str = None, transaction_id: str = None) -> Dict[str, Any]:
        """
        查询订单
        
        Args:
            out_trade_no: 商户订单号
            transaction_id: 微信订单号
        
        Returns:
            订单查询结果
        """
        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str()
        }
        
        if out_trade_no:
            params["out_trade_no"] = out_trade_no
        elif transaction_id:
            params["transaction_id"] = transaction_id
        else:
            return {"success": False, "error": "订单号不能为空"}
        
        # 生成签名
        params["sign"] = self._generate_sign(params)
        
        # 转换为XML
        xml_data = self._dict_to_xml(params)
        
        try:
            response = requests.post(self.query_order_url, data=xml_data, timeout=30)
            response.raise_for_status()
            
            # 解析响应
            result = self._xml_to_dict(response.text)
            
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                return {
                    "success": True,
                    "trade_state": result.get("trade_state"),
                    "transaction_id": result.get("transaction_id"),
                    "out_trade_no": result.get("out_trade_no"),
                    "total_fee": result.get("total_fee"),
                    "time_end": result.get("time_end")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("err_code_des", "查询订单失败")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"查询失败: {str(e)}"
            }
    
    def close_order(self, out_trade_no: str) -> Dict[str, Any]:
        """
        关闭订单
        
        Args:
            out_trade_no: 商户订单号
        
        Returns:
            关闭订单结果
        """
        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "out_trade_no": out_trade_no,
            "nonce_str": self._generate_nonce_str()
        }
        
        # 生成签名
        params["sign"] = self._generate_sign(params)
        
        # 转换为XML
        xml_data = self._dict_to_xml(params)
        
        try:
            response = requests.post(self.close_order_url, data=xml_data, timeout=30)
            response.raise_for_status()
            
            # 解析响应
            result = self._xml_to_dict(response.text)
            
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": result.get("err_code_des", "关闭订单失败")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"关闭订单失败: {str(e)}"
            }
    
    def verify_notify(self, xml_data: str) -> Dict[str, Any]:
        """
        验证支付回调
        
        Args:
            xml_data: 微信回调的XML数据
        
        Returns:
            验证结果和订单信息
        """
        try:
            # 解析XML
            result = self._xml_to_dict(xml_data)
            
            # 验证签名
            if not self._verify_sign(result):
                return {
                    "success": False,
                    "error": "签名验证失败"
                }
            
            # 检查支付结果
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                return {
                    "success": True,
                    "transaction_id": result.get("transaction_id"),
                    "out_trade_no": result.get("out_trade_no"),
                    "total_fee": int(result.get("total_fee", 0)),
                    "time_end": result.get("time_end"),
                    "openid": result.get("openid")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("err_code_des", "支付失败")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"解析回调数据失败: {str(e)}"
            }
    
    def create_jsapi_pay_params(self, prepay_id: str) -> Dict[str, str]:
        """
        创建JSAPI支付参数（用于公众号支付）
        
        Args:
            prepay_id: 预支付ID
        
        Returns:
            JSAPI支付参数
        """
        params = {
            "appId": self.app_id,
            "timeStamp": str(int(time.time())),
            "nonceStr": self._generate_nonce_str(),
            "package": f"prepay_id={prepay_id}",
            "signType": "MD5"
        }
        
        # 生成签名
        params["paySign"] = self._generate_sign(params)
        
        return params
    
    def _generate_nonce_str(self) -> str:
        """生成随机字符串"""
        return str(uuid.uuid4()).replace("-", "")
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名"""
        # 过滤空值并排序
        filtered_params = {k: v for k, v in params.items() if v is not None and v != ""}
        sorted_params = sorted(filtered_params.items())
        
        # 拼接字符串
        string_a = "&".join([f"{k}={v}" for k, v in sorted_params])
        string_sign_temp = f"{string_a}&key={self.api_key}"
        
        # MD5加密并转大写
        sign = hashlib.md5(string_sign_temp.encode('utf-8')).hexdigest().upper()
        return sign
    
    def _verify_sign(self, params: Dict[str, Any]) -> bool:
        """验证签名"""
        sign = params.pop("sign", "")
        calculated_sign = self._generate_sign(params)
        return sign == calculated_sign
    
    def _dict_to_xml(self, params: Dict[str, Any]) -> str:
        """字典转XML"""
        xml = "<xml>"
        for k, v in params.items():
            xml += f"<{k}><![CDATA[{v}]]></{k}>"
        xml += "</xml>"
        return xml
    
    def _xml_to_dict(self, xml_data: str) -> Dict[str, str]:
        """XML转字典"""
        root = ET.fromstring(xml_data)
        result = {}
        for child in root:
            result[child.tag] = child.text
        return result
    
    def create_refund(self, 
                     out_trade_no: str, 
                     out_refund_no: str, 
                     total_fee: int, 
                     refund_fee: int,
                     refund_desc: str = "退款") -> Dict[str, Any]:
        """
        申请退款
        
        Args:
            out_trade_no: 商户订单号
            out_refund_no: 商户退款单号
            total_fee: 订单总金额（分）
            refund_fee: 退款金额（分）
            refund_desc: 退款描述
        
        Returns:
            退款结果
        """
        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
            "out_trade_no": out_trade_no,
            "out_refund_no": out_refund_no,
            "total_fee": total_fee,
            "refund_fee": refund_fee,
            "refund_desc": refund_desc
        }
        
        # 生成签名
        params["sign"] = self._generate_sign(params)
        
        # 转换为XML
        xml_data = self._dict_to_xml(params)
        
        try:
            # 退款需要证书
            if not settings.wechat_cert_path or not settings.wechat_key_path:
                return {
                    "success": False,
                    "error": "退款需要配置商户证书"
                }
            
            response = requests.post(
                self.refund_url, 
                data=xml_data, 
                cert=(settings.wechat_cert_path, settings.wechat_key_path),
                timeout=30
            )
            response.raise_for_status()
            
            # 解析响应
            result = self._xml_to_dict(response.text)
            
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                return {
                    "success": True,
                    "refund_id": result.get("refund_id"),
                    "out_refund_no": out_refund_no
                }
            else:
                return {
                    "success": False,
                    "error": result.get("err_code_des", "退款失败")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"退款失败: {str(e)}"
            }
