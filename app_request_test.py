#!/usr/bin/env python3
"""
模拟APP请求测试工具 - 测试APP是否能正常连接
"""

import socket
import json
import time
import sys
from datetime import datetime

def test_http_request(host, port, endpoint, headers=None, timeout=10):
    """模拟HTTP请求（类似Dio的请求方式）"""
    if headers is None:
        headers = {
            'User-Agent': 'Dart/3.1 (dart:io)',
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': '*/*',
            'Connection': 'close'
        }
    
    try:
        # 创建socket连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        
        # 构造HTTP请求
        request_lines = [
            f"GET {endpoint} HTTP/1.1",
            f"Host: {host}:{port}",
            f"User-Agent: {headers['User-Agent']}",
            f"Content-Type: {headers['Content-Type']}",
            f"Accept: {headers.get('Accept', '*/*')}",
            f"Connection: {headers.get('Connection', 'close')}",
            "Accept-Encoding: gzip",
            "",
            ""
        ]
        
        request = "\r\n".join(request_lines)
        print(f"📤 发送请求到 {host}:{port}{endpoint}")
        print(f"📝 请求头:")
        for line in request_lines[:-2]:
            print(f"   {line}")
        
        sock.send(request.encode('utf-8'))
        
        # 接收响应
        response = sock.recv(4096).decode('utf-8')
        sock.close()
        
        print(f"📥 收到响应:")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        return True, response
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False, str(e)

def test_all_endpoints():
    """测试所有APP会用的端点"""
    endpoints = [
        '/health',
        '/api/devices',
        '/api/sensor-data',
        '/api/alarms',
        '/api/reminders'
    ]
    
    hosts = ['localhost', '192.168.1.200']
    
    print("🔍 APP连接测试")
    print("=" * 60)
    
    results = {}
    
    for host in hosts:
        print(f"\n📍 测试主机: {host}")
        results[host] = {}
        
        for endpoint in endpoints:
            print(f"\n🌐 测试端点: {endpoint}")
            success, response = test_http_request(host, 8080, endpoint)
            
            if success:
                results[host][endpoint] = "✅ 成功"
                # 尝试解析JSON响应
                try:
                    lines = response.split('\n')
                    for line in lines:
                        if line.strip().startswith('{'):
                            json_data = json.loads(line.strip())
                            print(f"   JSON响应: {json_data}")
                            break
                except:
                    print("   响应不是JSON格式")
            else:
                results[host][endpoint] = "❌ 失败"
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 测试结果总结:")
    
    for host, endpoints in results.items():
        success_count = sum(1 for result in endpoints.values() if result == "✅ 成功")
        total_count = len(endpoints)
        print(f"  {host}: {success_count}/{total} 端点成功")
        
        for endpoint, result in endpoints.items():
            print(f"    {endpoint}: {result}")

def test_websocket_simulation():
    """模拟WebSocket连接测试"""
    print(f"\n{'='*60}")
    print("🔌 WebSocket连接模拟测试:")
    
    try:
        # 尝试连接WebSocket端点（服务器没有这个端点）
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('192.168.1.200', 8080))
        
        if result == 0:
            # 连接成功，尝试发送WebSocket握手
            print("   ⚠️  TCP连接成功，但服务器无WebSocket支持")
            print("   ❌ APP期望WebSocket连接，但服务器不支持")
        else:
            print("   ❌ TCP连接失败")
            
        sock.close()
        
    except Exception as e:
        print(f"   ❌ WebSocket连接异常: {e}")

if __name__ == "__main__":
    test_all_endpoints()
    test_websocket_simulation()
    
    print(f"\n{'='*60}")
    print("💡 建议:")
    print("1. 检查APP是否真的需要WebSocket连接")
    print("2. 如果需要，需要在服务器上添加WebSocket支持")
    print("3. 或者修改APP代码，禁用WebSocket连接")
    print("4. 检查APP的连接超时设置")