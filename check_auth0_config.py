#!/usr/bin/env python3
"""
检查Auth0配置
"""
import requests
import json

def check_auth0_config():
    """检查Auth0配置"""
    print("🔍 检查Auth0配置")
    print("=" * 50)
    
    # 检查Auth0域名
    domain = "gaopfediter.us.auth0.com"
    print(f"Domain: {domain}")
    
    # 检查OpenID配置
    try:
        config_url = f"https://{domain}/.well-known/openid_configuration"
        response = requests.get(config_url, timeout=10)
        if response.status_code == 200:
            config = response.json()
            print(f"✅ OpenID配置可访问")
            print(f"   Token Endpoint: {config.get('token_endpoint')}")
            print(f"   Authorization Endpoint: {config.get('authorization_endpoint')}")
        else:
            print(f"❌ OpenID配置不可访问: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 连接Auth0失败: {e}")
        return
    
    # 测试token端点
    print(f"\n🔑 测试Token端点...")
    token_url = config.get('token_endpoint')
    
    # 使用无效的code测试端点是否正常
    test_data = {
        "grant_type": "authorization_code",
        "client_id": "5xzUKrmwx7bFlUb9nf7l3C0Xp0q8AqcN",
        "client_secret": "5VbXSpLULWdqS7n4dLZOQjvJmkw73otJ8KsMzTPgJPIpfCM8CxAVfU-36OQkEGET",
        "code": "invalid_test_code",
        "redirect_uri": "https://subpredicative-jerrica-subtepidly.ngrok-free.dev/google-login/success"
    }
    
    try:
        response = requests.post(token_url, json=test_data, timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        
        if response.status_code == 400:
            error_data = response.json()
            if error_data.get("error") == "invalid_grant":
                print("   ✅ Token端点正常，但授权码无效（这是预期的）")
            else:
                print(f"   ⚠️ 其他错误: {error_data}")
        else:
            print(f"   ❌ 意外的状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print(f"\n📋 请检查Auth0控制台配置:")
    print(f"   1. 访问: https://manage.auth0.com/")
    print(f"   2. 选择您的应用")
    print(f"   3. 确认Allowed Callback URLs包含:")
    print(f"      https://subpredicative-jerrica-subtepidly.ngrok-free.dev/google-login/success")
    print(f"   4. 确认Allowed Web Origins包含:")
    print(f"      https://subpredicative-jerrica-subtepidly.ngrok-free.dev")
    print(f"   5. 确认应用类型为 'Regular Web Application'")

if __name__ == "__main__":
    check_auth0_config()
