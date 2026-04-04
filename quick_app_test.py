#!/usr/bin/env python3
"""
简化的APP连接测试 - 快速诊断
"""

import socket
import json
import time

def test_app_connection():
    """快速测试APP连接问题"""
    print("🔍 APP连接快速诊断")
    print("=" * 50)
    
    # 测试地址
    test_cases = [
        ('192.168.1.200', 8080, '/health', '正确地址'),
        ('192.168.1.200', 8080, '/api/devices', '设备接口'),
        ('192.168.1.100', 8080, '/health', '错误地址'),
    ]
    
    for host, port, endpoint, desc in test_cases:
        print(f"\n📍 {desc} ({host}:{port}{endpoint}):")
        print("-" * 30)
        
        try:
            # 快速连接测试
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5秒超时
            result = sock.connect_ex((host, port))
            
            if result == 0:
                print("✅ 连接成功")
                
                # 发送HTTP请求
                request = f"GET {endpoint} HTTP/1.1\r\nHost: {host}:{port}\r\nUser-Agent: Dart/3.1\r\n\r\n"
                sock.send(request.encode())
                
                # 接收响应
                response = sock.recv(2048).decode()
                sock.close()
                
                # 简单检查响应
                if '200 OK' in response:
                    print("✅ HTTP响应正常")
                    # 尝试查找JSON
                    if '{' in response:
                        print("✅ 包含JSON响应")
                        # 提取JSON部分
                        try:
                            json_start = response.find('{')
                            json_end = response.rfind('}') + 1
                            json_str = response[json_start:json_end]
                            json_data = json.loads(json_str)
                            print(f"✅ JSON解析成功: {type(json_data)}")
                        except:
                            print("❌ JSON解析失败")
                    else:
                        print("❌ 不包含JSON响应")
                else:
                    print(f"❌ HTTP响应异常: {response[:100]}")
                
            else:
                print(f"❌ 连接失败 (错误码: {result})")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
        
        time.sleep(0.5)

def suggest_possible_issues():
    """分析可能的问题"""
    print(f"\n{'='*50}")
    print("🔍 可能的问题分析:")
    print("=" * 50)
    
    print("1. 🔧 APP端问题:")
    print("   - Dio库的配置问题")
    print("   - 错误处理逻辑过于严格")
    print("   - 超时设置问题")
    print("   - JSON解析问题")
    print("   - WebSocket连接失败")
    
    print("\n2. 🌐 网络问题:")
    print("   - 防火墙阻止")
    print("   - 路由器NAT问题")
    print("   - 移动网络vs WiFi网络")
    
    print("\n3. 📱 设备问题:")
    print("   - APP的SSL证书验证")
    print("   - APP的网络权限设置")
    print("   - APP的后台限制")
    
    print("\n4. 🎯 解决方案:")
    print("   - 检查APP的网络权限")
    print("   - 尝试其他网络环境")
    print("   - 查看APP的具体错误日志")
    print("   - 测试其他地址格式")

if __name__ == "__main__":
    test_app_connection()
    suggest_possible_issues()