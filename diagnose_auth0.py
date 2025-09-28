#!/usr/bin/env python3
"""
诊断Auth0配置问题
"""
import requests
import json

def diagnose_auth0():
    """诊断Auth0配置问题"""
    print("🔍 诊断Auth0配置问题")
    print("=" * 60)
    
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
    
    # 测试不同的重定向URI
    print(f"\n🔑 测试不同的重定向URI...")
    token_url = config.get('token_endpoint')
    
    # 测试数据
    test_code = "test_code_123"
    client_id = "5xzUKrmwx7bFlUb9nf7l3C0Xp0q8AqcN"
    client_secret = "5VbXSpLULWdqS7n4dLZOQjvJmkw73otJ8KsMzTPgJPIpfCM8CxAVfU-36OQkEGET"
    
    # 测试不同的重定向URI
    redirect_uris = [
        "https://subpredicative-jerrica-subtepidly.ngrok-free.dev/google-login/success",
        "https://subpredicative-jerrica-subtepidly.ngrok-free.dev",
        "http://localhost:8000/api/auth/auth0/callback",
        "https://subpredicative-jerrica-subtepidly.ngrok-free.dev/api/auth/auth0/callback"
    ]
    
    for redirect_uri in redirect_uris:
        print(f"\n   测试重定向URI: {redirect_uri}")
        
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": test_code,
            "redirect_uri": redirect_uri
        }
        
        try:
            response = requests.post(token_url, json=data, timeout=10)
            print(f"      状态码: {response.status_code}")
            print(f"      响应: {response.text}")
            
            if response.status_code == 400:
                error_data = response.json()
                if error_data.get("error") == "invalid_grant":
                    print("      ✅ 端点正常，但授权码无效（这是预期的）")
                else:
                    print(f"      ⚠️ 其他错误: {error_data}")
            else:
                print(f"      ❌ 意外的状态码: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ 请求失败: {e}")
    
    print(f"\n📋 请检查Auth0控制台配置:")
    print(f"   1. 访问: https://manage.auth0.com/")
    print(f"   2. 选择您的应用")
    print(f"   3. 在 'Allowed Callback URLs' 中添加以下URL:")
    for uri in redirect_uris:
        print(f"      - {uri}")
    print(f"   4. 在 'Allowed Web Origins' 中添加:")
    print(f"      - https://subpredicative-jerrica-subtepidly.ngrok-free.dev")
    print(f"   5. 确认应用类型为 'Regular Web Application'")

if __name__ == "__main__":
    diagnose_auth0()
