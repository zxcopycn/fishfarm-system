#!/usr/bin/env python3
"""
精确模拟APP的Dio请求 - 检查APP连接失败的真正原因
"""

import socket
import json
import time
from urllib.parse import urlparse

def simulate_dio_request(host, port, endpoint, method="GET", timeout=30):
    """模拟Dio的HTTP请求"""
    print(f"🔧 模拟Dio请求: {method} {host}:{port}{endpoint}")
    print(f"⏱️  超时设置: {timeout}秒")
    
    try:
        # 创建socket连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        start_time = time.time()
        sock.connect((host, port))
        connect_time = time.time() - start_time
        
        print(f"✅ 连接成功 (耗时: {connect_time:.3f}s)")
        
        # 构造Dio风格的HTTP请求
        request_lines = [
            f"{method} {endpoint} HTTP/1.1",
            f"Host: {host}:{port}",
            f"User-Agent: Dio/5.3.3 (dart:io)",
            f"Content-Type: application/json; charset=utf-8",
            f"Accept: */*",
            f"Accept-Encoding: gzip",
            f"Connection: close",
        ]
        
        request = "\r\n".join(request_lines) + "\r\n\r\n"
        print(f"📤 请求头:")
        for line in request_lines:
            print(f"   {line}")
        
        # 发送请求
        sock.send(request.encode('utf-8'))
        
        # 接收响应
        start_time = time.time()
        response = sock.recv(8192).decode('utf-8')
        response_time = time.time() - start_time
        
        sock.close()
        
        print(f"📥 响应 (耗时: {response_time:.3f}s)")
        print(f"{'='*50}")
        
        # 解析响应
        response_lines = response.split('\r\n')
        status_line = response_lines[0]
        headers = {}
        body_lines = []
        
        in_body = False
        for line in response_lines[1:]:
            if in_body:
                body_lines.append(line)
            elif line == '':
                in_body = True
            else:
                # 解析header
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
        
        body = '\r\n'.join(body_lines)
        
        print(f"状态行: {status_line}")
        print("响应头:")
        for key, value in headers.items():
            print(f"   {key}: {value}")
        print("响应体:")
        if body:
            print(body[:500] + "..." if len(body) > 500 else body)
        else:
            print("(无响应体)")
        
        print(f"{'='*50}")
        
        # 模拟Dio的错误检查
        if '200 OK' in status_line:
            print("✅ Dio状态检查: 200 OK")
            return True, response
        else:
            print(f"❌ Dio状态检查: {status_line}")
            return False, response
            
    except socket.timeout:
        print(f"❌ 连接超时 (Dio的30秒超时)")
        return False, "TimeoutError"
    except socket.gaierror as e:
        print(f"❌ DNS解析失败: {e}")
        return False, f"DnsError: {e}"
    except ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        return False, f"ConnectionError: {e}"
    except Exception as e:
        print(f"❌ 其他错误: {type(e).__name__}: {e}")
        return False, f"Error: {type(e).__name__}: {e}"

def test_websocket_connection(host, port, timeout=5):
    """测试WebSocket连接（APP尝试的部分）"""
    print(f"🔌 测试WebSocket连接: ws://{host}:{port}/ws")
    
    try:
        # 尝试WebSocket连接（实际上会失败，因为服务器没有WebSocket支持）
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # WebSocket握手请求
        request = (
            "GET /ws HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        
        sock.connect((host, port))
        sock.send(request.encode())
        
        # 尝试读取响应
        try:
            response = sock.recv(1024).decode()
            if '101 Switching Protocols' in response:
                print("✅ WebSocket升级成功（服务器支持WebSocket）")
            else:
                print("❌ WebSocket升级失败（服务器不支持WebSocket）")
                print(f"响应: {response[:200]}")
        except socket.timeout:
            print("❌ WebSocket握手超时（服务器可能不支持WebSocket）")
        except Exception as e:
            print(f"❌ WebSocket连接失败: {e}")
            
        sock.close()
        
    except Exception as e:
        print(f"❌ WebSocket连接异常: {e}")

def main():
    """主测试函数"""
    print("🔍 APP Dio请求模拟测试")
    print("=" * 60)
    
    # 测试地址
    test_cases = [
        ('192.168.1.200', 8080, '/health', '健康检查'),
        ('192.168.1.200', 8080, '/api/devices', '设备列表'),
        ('192.168.1.200', 8080, '/api/sensor-data', '传感器数据'),
        ('192.168.1.100', 8080, '/health', '错误地址测试'),
        ('112.64.186.254', 8080, '/health', '公网地址测试'),
    ]
    
    results = {}
    
    for host, port, endpoint, description in test_cases:
        print(f"\n📍 {description}:")
        print("-" * 40)
        
        success, response = simulate_dio_request(host, port, endpoint)
        results[(host, port, endpoint)] = success
        
        # 短暂等待
        time.sleep(1)
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 测试结果总结:")
    
    success_count = sum(results.values())
    total_count = len(results)
    print(f"成功率: {success_count}/{total_count}")
    
    for (host, port, endpoint), success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {host}:{port}{endpoint} - {status}")
    
    # WebSocket测试
    print(f"\n{'='*60}")
    print("WebSocket连接测试:")
    test_websocket_connection('192.168.1.200', 8080)
    
    # 建议分析
    print(f"\n{'='*60}")
    print("💡 分析建议:")
    
    if success_count > 0:
        print("✅ 网络连接正常，HTTP请求可以成功")
        print("❌ 如果APP仍然失败，可能是:")
        print("   1. APP的错误处理逻辑过于严格")
        print("   2. APP的Dio版本或配置问题")
        print("   3. APP的JSON解析问题")
        print("   4. APP的拦截器配置问题")
        print("   5. WebSocket连接失败导致整体连接失败")
    else:
        print("❌ 所有连接都失败，可能是网络配置问题")

if __name__ == "__main__":
    main()