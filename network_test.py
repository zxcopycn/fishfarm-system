#!/usr/bin/env python3
"""
网络环境测试脚本 - 检查各种IP地址的连通性
"""

import socket
import subprocess
import sys
import time

def get_network_info():
    """获取网络接口信息"""
    print("=== 网络接口信息 ===")
    try:
        # 尝试获取所有IP地址
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            ips = result.stdout.strip().split()
            print(f"系统IP地址: {ips}")
        
        # 尝试获取特定接口信息
        interfaces = ['eth0', 'wlan0', 'lo']
        for interface in interfaces:
            try:
                result = subprocess.run(['ifconfig', interface], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"\n{interface} 配置:")
                    print(result.stdout)
            except:
                pass
                
    except Exception as e:
        print(f"获取网络信息失败: {e}")

def test_port_connection(ip, port, timeout=5):
    """测试端口连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("🔍 网络连接测试")
    print("=" * 50)
    
    # 获取网络信息
    get_network_info()
    
    print("\n=== 端口8080连接测试 ===")
    
    # 测试不同地址
    test_ips = [
        'localhost',
        '127.0.0.1', 
        '192.168.1.100',
        '172.17.0.2',
        '112.64.186.254'
    ]
    
    results = {}
    for ip in test_ips:
        print(f"测试 {ip}:8080...", end=' ')
        try:
            if test_port_connection(ip, 8080):
                print("✅ 连接成功")
                results[ip] = True
            else:
                print("❌ 连接失败")
                results[ip] = False
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results[ip] = False
    
    print(f"\n=== 测试结果总结 ===")
    success_ips = [ip for ip, success in results.items() if success]
    if success_ips:
        print(f"✅ 可访问的地址: {success_ips}")
    else:
        print("❌ 所有地址都无法访问")
    
    return success_ips

if __name__ == "__main__":
    main()