#!/usr/bin/env python3
"""
渔场系统前端API集成测试
模拟Flutter应用对后端API的调用
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8003"

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data['service']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_devices_api():
    """测试设备管理API"""
    print("\n🔍 测试设备管理API...")
    try:
        response = requests.get(f"{BASE_URL}/api/devices/list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 设备列表获取成功，共 {len(data)} 台设备")
            for device in data:
                print(f"   - {device['device_name']} ({device['device_type_name']})")
            return True
        else:
            print(f"❌ 设备列表获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 设备列表异常: {e}")
        return False

def test_sensor_api():
    """测试传感器数据API"""
    print("\n🔍 测试传感器数据API...")
    try:
        response = requests.get(f"{BASE_URL}/api/sensor/latest", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 传感器数据获取成功，共 {len(data)} 条数据")
            for sensor in data[:3]:  # 显示前3条
                print(f"   - {sensor['device_name']}: 温度 {sensor['temperature']}℃, PH {sensor['ph']}")
            return True
        else:
            print(f"❌ 传感器数据获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 传感器数据异常: {e}")
        return False

def test_alarms_api():
    """测试预警系统API"""
    print("\n🔍 测试预警系统API...")
    
    # 测试预警规则
    try:
        response = requests.get(f"{BASE_URL}/api/alarms/rules", timeout=5)
        if response.status_code == 200:
            rules = response.json()
            print(f"✅ 预警规则获取成功，共 {len(rules)} 条规则")
        else:
            print(f"❌ 预警规则获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 预警规则异常: {e}")
        return False
    
    # 测试预警记录
    try:
        response = requests.get(f"{BASE_URL}/api/alarms/records", timeout=5)
        if response.status_code == 200:
            records = response.json()
            print(f"✅ 预警记录获取成功，共 {len(records)} 条记录")
        else:
            print(f"❌ 预警记录获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 预警记录异常: {e}")
        return False
    
    return True

def test_reminders_api():
    """测试提醒API"""
    print("\n🔍 测试提醒API...")
    try:
        response = requests.get(f"{BASE_URL}/api/reminders", timeout=5)
        if response.status_code == 200:
            reminders = response.json()
            print(f"✅ 提醒列表获取成功，共 {len(reminders)} 条提醒")
            for reminder in reminders[:2]:  # 显示前2条
                status = "✅ 已完成" if reminder['is_completed'] else "⏰ 未完成"
                print(f"   - {reminder['title']} ({status})")
            return True
        else:
            print(f"❌ 提醒列表获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 提醒列表异常: {e}")
        return False

def test_production_api():
    """测试生产记录API"""
    print("\n🔍 测试生产记录API...")
    try:
        response = requests.get(f"{BASE_URL}/api/production/list", timeout=5)
        if response.status_code == 200:
            records = response.json()
            print(f"✅ 生产记录获取成功，共 {len(records)} 条记录")
            for record in records:
                print(f"   - {record['fish_type']}: {record['quantity']} 条")
            return True
        else:
            print(f"❌ 生产记录获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 生产记录异常: {e}")
        return False

def simulate_flutter_requests():
    """模拟Flutter应用的API调用序列"""
    print("🚀 开始模拟Flutter应用API测试...")
    print("=" * 50)
    
    results = []
    
    # 1. 应用启动时健康检查
    results.append(test_health_check())
    
    # 2. 首页加载数据
    results.append(test_devices_api())
    results.append(test_sensor_api())
    results.append(test_alarms_api())
    results.append(test_reminders_api())
    results.append(test_production_api())
    
    # 3. 测试结果统计
    print("\n" + "=" * 50)
    print("📊 测试结果统计:")
    passed = sum(results)
    total = len(results)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 所有API测试通过！前端可以正常连接后端服务。")
        return True
    else:
        print("⚠️ 部分API测试失败，需要检查后端服务。")
        return False

if __name__ == "__main__":
    start_time = time.time()
    success = simulate_flutter_requests()
    end_time = time.time()
    
    print(f"\n⏱️ 测试耗时: {end_time - start_time:.2f} 秒")
    
    if success:
        print("\n✅ 前端API集成测试完成，系统可以正常使用！")
    else:
        print("\n❌ 前端API集成测试发现问题，请检查后端服务状态。")