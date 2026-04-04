#!/usr/bin/env python3
"""
简化的连接测试 - 验证APP能否正确连接
"""

import socket
import json

def test_app_connection():
    """模拟APP的连接测试"""
    print("🔍 APP连接模拟测试")
    print("=" * 50)
    
    # 测试不同地址
    test_cases = [
        ('localhost', 8080, '本地测试'),
        ('192.168.1.200', 8080, 'APP配置地址'),
        ('192.168.1.100', 8080, '您测试的地址'),
        ('112.64.186.254', 8080, '公网地址')
    ]
    
    results = {}
    
    for host, port, description in test_cases:
        print(f"\n📍 {description}: {host}:{port}")
        
        try:
            # 创建连接（模拟APP的HTTP连接）
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10秒超时
            result = sock.connect_ex((host, port))
            
            if result == 0:
                print("   ✅ 连接成功")
                
                # 发送HTTP请求（模拟APP的健康检查）
                request = f"GET /health HTTP/1.1\r\nHost: {host}:{port}\r\nUser-Agent: Dart/3.1 (dart:io)\r\nAccept: */*\r\n\r\n"
                sock.send(request.encode())
                
                # 接收响应
                response = sock.recv(1024).decode()
                sock.close()
                
                # 检查响应
                if '200 OK' in response and 'status' in response:
                    print("   ✅ HTTP响应正常")
                    results[host] = True
                else:
                    print("   ⚠️  HTTP响应异常")
                    results[host] = False
                    
            else:
                print(f"   ❌ 连接失败 (错误码: {result})")
                results[host] = False
                
        except Exception as e:
            print(f"   ❌ 连接异常: {e}")
            results[host] = False
    
    # 总结
    print(f"\n{'='*50}")
    print("📊 连接结果总结:")
    
    success_hosts = [host for host, success in results.items() if success]
    if success_hosts:
        print("✅ 可连接的地址:")
        for host in success_hosts:
            print(f"   - {host}")
    else:
        print("❌ 所有地址都无法连接")
    
    # 给出建议
    print(f"\n💡 建议:")
    if '192.168.1.200' in success_hosts:
        print("1. 使用192.168.1.200:8080作为API地址")
        print("2. 确保APP设置中使用了正确的地址")
        print("3. 检查网络防火墙是否阻止了连接")
    else:
        print("1. 检查服务器是否正在运行")
        print("2. 检查端口8080是否被占用")
        print("3. 检查网络配置")

if __name__ == "__main__":
    test_app_connection()