#!/usr/bin/env python3
"""
测试反馈留言和积分系统功能
"""
import requests
import json
from datetime import datetime, date

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_login():
    """测试登录获取token"""
    print("🔐 测试用户登录...")
    
    login_data = {
        "username": "admin",
        "password": "admin666"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 登录成功: {data['user']['username']}")
        return data['access_token']
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return None

def test_feedback_operations(token):
    """测试反馈留言功能"""
    print("\n📝 测试反馈留言功能...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 创建反馈
    print("1. 创建反馈留言...")
    feedback_data = {
        "title": "图片转换功能建议",
        "content": "希望能支持更多图片格式的转换，比如HEIC格式",
        "category": "feature",
        "priority": "medium"
    }
    
    response = requests.post(
        f"{BASE_URL}/feedback/create",
        json=feedback_data,
        headers=headers
    )
    
    if response.status_code == 200:
        feedback = response.json()
        print(f"✅ 反馈创建成功: ID={feedback['id']}")
        feedback_id = feedback['id']
    else:
        print(f"❌ 反馈创建失败: {response.status_code} - {response.text}")
        return
    
    # 2. 获取反馈列表
    print("2. 获取反馈列表...")
    response = requests.get(
        f"{BASE_URL}/feedback/list?limit=10&offset=0",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取反馈列表成功: 共{data['total']}条")
    else:
        print(f"❌ 获取反馈列表失败: {response.status_code} - {response.text}")
    
    # 3. 获取反馈详情
    print("3. 获取反馈详情...")
    response = requests.get(
        f"{BASE_URL}/feedback/{feedback_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        feedback_detail = response.json()
        print(f"✅ 获取反馈详情成功: {feedback_detail['title']}")
    else:
        print(f"❌ 获取反馈详情失败: {response.status_code} - {response.text}")
    
    # 4. 更新反馈
    print("4. 更新反馈...")
    update_data = {
        "title": "图片转换功能建议（更新）",
        "priority": "high"
    }
    
    response = requests.put(
        f"{BASE_URL}/feedback/{feedback_id}",
        json=update_data,
        headers=headers
    )
    
    if response.status_code == 200:
        updated_feedback = response.json()
        print(f"✅ 反馈更新成功: {updated_feedback['title']}")
    else:
        print(f"❌ 反馈更新失败: {response.status_code} - {response.text}")

def test_points_operations(token):
    """测试积分系统功能"""
    print("\n💰 测试积分系统功能...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取积分摘要
    print("1. 获取积分摘要...")
    response = requests.get(f"{BASE_URL}/points/summary", headers=headers)
    
    if response.status_code == 200:
        summary = response.json()
        print(f"✅ 积分摘要获取成功:")
        print(f"   当前积分: {summary['current_points']}")
        print(f"   连续签到: {summary['consecutive_checkin_days']}天")
        print(f"   总签到: {summary['total_checkin_days']}天")
        print(f"   今日已签到: {summary['is_checkin_today']}")
    else:
        print(f"❌ 积分摘要获取失败: {response.status_code} - {response.text}")
    
    # 2. 用户签到
    print("2. 用户签到...")
    response = requests.post(f"{BASE_URL}/points/checkin", headers=headers)
    
    if response.status_code == 200:
        checkin = response.json()
        print(f"✅ 签到成功:")
        print(f"   获得积分: {checkin['points_earned']}")
        print(f"   连续天数: {checkin['consecutive_days']}")
    else:
        print(f"❌ 签到失败: {response.status_code} - {response.text}")
    
    # 3. 获取积分记录
    print("3. 获取积分记录...")
    response = requests.get(
        f"{BASE_URL}/points/records?limit=10&offset=0",
        headers=headers
    )
    
    if response.status_code == 200:
        records = response.json()
        print(f"✅ 积分记录获取成功: 共{len(records)}条")
        for record in records[:3]:  # 显示前3条
            print(f"   {record['description']}: {record['points']}积分")
    else:
        print(f"❌ 积分记录获取失败: {response.status_code} - {response.text}")
    
    # 4. 获取签到记录
    print("4. 获取签到记录...")
    response = requests.get(
        f"{BASE_URL}/points/checkin/records?limit=10&offset=0",
        headers=headers
    )
    
    if response.status_code == 200:
        checkin_records = response.json()
        print(f"✅ 签到记录获取成功: 共{len(checkin_records)}条")
        for record in checkin_records[:3]:  # 显示前3条
            print(f"   {record['checkin_date']}: {record['points_earned']}积分")
    else:
        print(f"❌ 签到记录获取失败: {response.status_code} - {response.text}")
    
    # 5. 积分兑换
    print("5. 积分兑换...")
    exchange_data = {
        "item_name": "VIP会员升级",
        "item_type": "vip_upgrade",
        "points_cost": 1000,
        "item_value": "升级到VIP会员"
    }
    
    response = requests.post(
        f"{BASE_URL}/points/exchange",
        json=exchange_data,
        headers=headers
    )
    
    if response.status_code == 200:
        exchange = response.json()
        print(f"✅ 积分兑换成功: {exchange['item_name']}")
    else:
        print(f"❌ 积分兑换失败: {response.status_code} - {response.text}")

def test_image_conversion_with_points(token):
    """测试图片转换与积分奖励"""
    print("\n🖼️ 测试图片转换与积分奖励...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取转换前的积分
    response = requests.get(f"{BASE_URL}/points/summary", headers=headers)
    if response.status_code == 200:
        before_points = response.json()['current_points']
        print(f"转换前积分: {before_points}")
    
    # 这里需要实际的图片文件进行转换测试
    # 由于没有图片文件，我们跳过实际的转换测试
    print("⚠️  图片转换测试需要实际的图片文件，跳过此测试")
    
    # 模拟转换后的积分检查
    response = requests.get(f"{BASE_URL}/points/summary", headers=headers)
    if response.status_code == 200:
        after_points = response.json()['current_points']
        print(f"转换后积分: {after_points}")

def main():
    """主函数"""
    print("🚀 开始测试反馈留言和积分系统...")
    
    # 测试登录
    token = test_login()
    if not token:
        print("❌ 登录失败，无法继续测试")
        return
    
    # 测试反馈功能
    test_feedback_operations(token)
    
    # 测试积分功能
    test_points_operations(token)
    
    # 测试图片转换与积分
    test_image_conversion_with_points(token)
    
    print("\n🎉 测试完成!")

if __name__ == "__main__":
    main()
