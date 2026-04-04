#!/usr/bin/env python3
"""
简化版渔场API服务器 - 支持基本WebSocket和HTTP API
使用Python内置库，不依赖外部包
"""

import json
import time
import socket
import threading
import select
import logging
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleWebSocketServer:
    """简化的WebSocket服务器"""
    
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.clients = {}
        self.running = False
        
    def start(self):
        """启动WebSocket服务器"""
        # 创建WebSocket服务器socket
        self.ws_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ws_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ws_socket.bind((self.host, self.port))
        self.ws_socket.listen(5)
        self.running = True
        
        logger.info(f"WebSocket服务器启动在 ws://{self.host}:{self.port}/ws")
        
        # 启动WebSocket服务器线程
        ws_thread = threading.Thread(target=self._run_ws_server)
        ws_thread.daemon = True
        ws_thread.start()
        
        # 启动模拟数据更新
        sim_thread = threading.Thread(target=self._simulate_data)
        sim_thread.daemon = True
        sim_thread.start()
    
    def stop(self):
        """停止WebSocket服务器"""
        self.running = False
        if hasattr(self, 'ws_socket'):
            self.ws_socket.close()
    
    def _run_ws_server(self):
        """运行WebSocket服务器"""
        while self.running:
            try:
                # 使用select处理多个连接
                read_sockets, _, _ = select.select([self.ws_socket] + list(self.clients.keys()), [], [], 1.0)
                
                for sock in read_sockets:
                    if sock == self.ws_socket:
                        # 新连接
                        client_socket, client_address = self.ws_socket.accept()
                        self.clients[client_socket] = {
                            'address': client_address,
                            'last_active': time.time()
                        }
                        logger.info(f"新的WebSocket连接: {client_address}")
                        
                        # 发送连接确认
                        self._send_to_client(client_socket, {
                            "type": "connection_established",
                            "client_id": id(client_socket),
                            "timestamp": datetime.now().isoformat(),
                            "message": "WebSocket连接成功"
                        })
                        
                        # 发送初始数据
                        self._send_to_client(client_socket, {
                            "type": "device_list",
                            "data": self._get_devices()
                        })
                        
                        self._send_to_client(client_socket, {
                            "type": "sensor_data",
                            "data": self._get_sensor_data()
                        })
                        
                        # 启动客户端消息监听
                        client_thread = threading.Thread(target=self._handle_client, args=(client_socket,))
                        client_thread.daemon = True
                        client_thread.start()
                    
                    else:
                        # 现有连接
                        self._handle_client_message(sock)
                
            except Exception as e:
                logger.error(f"WebSocket服务器错误: {e}")
                time.sleep(1)
    
    def _handle_client(self, client_socket):
        """处理客户端连接"""
        try:
            while self.running:
                # 简单的TCP通信，不是真正的WebSocket协议
                # 这只是一个模拟实现
                data = client_socket.recv(1024)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode())
                    logger.info(f"收到消息: {message}")
                    
                    # 发送响应
                    response = {
                        "type": "response",
                        "status": "success",
                        "received": message,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self._send_to_client(client_socket, response)
                    
                except json.JSONDecodeError:
                    response = {
                        "type": "error",
                        "status": "invalid_json",
                        "message": "无效的JSON格式"
                    }
                    self._send_to_client(client_socket, response)
                
        except Exception as e:
            logger.error(f"客户端处理错误: {e}")
        finally:
            self._remove_client(client_socket)
    
    def _handle_client_message(self, client_socket):
        """处理客户端消息"""
        try:
            data = client_socket.recv(1024)
            if data:
                # 模拟WebSocket消息处理
                try:
                    message = json.loads(data.decode())
                    logger.info(f"WebSocket消息: {message}")
                    
                    response = {
                        "type": "response",
                        "status": "success", 
                        "received": message,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self._send_to_client(client_socket, response)
                    
                except json.JSONDecodeError:
                    response = {
                        "type": "error",
                        "status": "invalid_json",
                        "message": "无效的JSON格式"
                    }
                    self._send_to_client(client_socket, response)
                    
        except Exception as e:
            logger.error(f"处理消息错误: {e}")
    
    def _send_to_client(self, client_socket, data):
        """发送数据到客户端"""
        try:
            message = json.dumps(data, ensure_ascii=False) + "\n"
            client_socket.send(message.encode())
            client_socket.recv(1024)  # 简单的ACK
        except Exception as e:
            logger.error(f"发送数据错误: {e}")
    
    def _remove_client(self, client_socket):
        """移除客户端"""
        if client_socket in self.clients:
            del self.clients[client_socket]
            try:
                client_socket.close()
            except:
                pass
            logger.info(f"客户端断开连接")
    
    def _get_devices(self):
        """获取设备列表"""
        return [
            {
                "id": "1",
                "name": "水温传感器1",
                "deviceType": "temperature_sensor",
                "deviceNumber": "TEMP_001",
                "location": "池塘A",
                "status": "online",
                "lastUpdate": datetime.now().isoformat(),
                "description": "监测水温变化"
            },
            {
                "id": "2", 
                "name": "PH传感器1",
                "deviceType": "ph_sensor",
                "deviceNumber": "PH_001",
                "location": "池塘A",
                "status": "online",
                "lastUpdate": datetime.now().isoformat(),
                "description": "监测PH值变化"
            },
            {
                "id": "3",
                "name": "溶解氧传感器1",
                "deviceType": "oxygen_sensor", 
                "deviceNumber": "OXY_001",
                "location": "池塘A",
                "status": "online",
                "lastUpdate": datetime.now().isoformat(),
                "description": "监测溶解氧含量"
            }
        ]
    
    def _get_sensor_data(self):
        """获取传感器数据"""
        return [
            {
                "deviceId": "1",
                "sensorType": "temperature",
                "value": 25.5,
                "unit": "°C",
                "timestamp": datetime.now().isoformat(),
                "status": "normal"
            },
            {
                "deviceId": "2",
                "sensorType": "ph", 
                "value": 7.2,
                "unit": "",
                "timestamp": datetime.now().isoformat(),
                "status": "normal"
            },
            {
                "deviceId": "3",
                "sensorType": "oxygen",
                "value": 6.8,
                "unit": "mg/L",
                "timestamp": datetime.now().isoformat(),
                "status": "normal"
            }
        ]
    
    def _simulate_data(self):
        """模拟数据更新"""
        while self.running:
            time.sleep(10)  # 每10秒更新一次
            
            if self.clients:
                import random
                
                # 更新设备状态
                for device in self._get_devices():
                    if device["status"] == "online" and random.random() < 0.2:
                        device["lastUpdate"] = datetime.now().isoformat()
                        
                        # 广播更新
                        update_msg = {
                            "type": "device_update",
                            "device": device,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        for client_socket in self.clients.keys():
                            self._send_to_client(client_socket, update_msg)
                
                # 更新传感器数据
                for sensor in self._get_sensor_data():
                    if random.random() < 0.3:
                        # 小幅度随机变化
                        variation = random.uniform(-0.3, 0.3)
                        sensor["value"] = round(float(sensor["value"]) + variation, 1)
                        sensor["timestamp"] = datetime.now().isoformat()
                        sensor["status"] = "normal" if 5 < sensor["value"] < 30 else "warning"
                        
                        # 广播更新
                        update_msg = {
                            "type": "sensor_update",
                            "data": sensor,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        for client_socket in self.clients.keys():
                            self._send_to_client(client_socket, update_msg)
                        
                        logger.info(f"更新传感器: {sensor['sensorType']} = {sensor['value']}{sensor['unit']}")

class HTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP请求处理"""
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        logger.info(f"HTTP GET请求: {path}")
        
        if path == "/":
            self._send_response({
                "name": "智能渔场环境控制监测系统",
                "version": "2.0.0",
                "status": "running",
                "websocket_supported": True,
                "websocket_endpoint": "/ws",
                "docs": "/api/docs"
            })
        
        elif path == "/health":
            self._send_response({
                "status": "healthy", 
                "service": "fishfarm-api",
                "websocket_supported": True,
                "websocket_endpoint": "/ws",
                "active_clients": len(ws_server.clients) if hasattr(ws_server, 'clients') else 0
            })
        
        elif path == "/ws":
            self._send_response({
                "message": "WebSocket端点",
                "connection_type": "websocket",
                "url": f"ws://{self.server.server_address[0]}:{self.server.server_address[1]}/ws"
            })
        
        elif path == "/api/devices":
            self._send_response({"data": ws_server._get_devices()})
        
        elif path == "/api/sensor-data":
            self._send_response({"data": ws_server._get_sensor_data()})
        
        elif path == "/api/alarms":
            alarms = [
                {
                    "id": "1",
                    "deviceId": "1",
                    "deviceName": "水温传感器1",
                    "alarmType": "temperature",
                    "level": "warning",
                    "title": "水温偏高",
                    "description": "当前水温25.5°C，接近上限值26°C",
                    "threshold": 26.0,
                    "status": "active",
                    "createdAt": datetime.now().isoformat()
                }
            ]
            self._send_response({"data": alarms})
        
        else:
            self._send_error(404, "API端点不存在")
    
    def _send_response(self, data, status_code=200):
        """发送JSON响应"""
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response_data.encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """发送错误响应"""
        self._send_response({"error": message}, status_code)
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

class FishFarmAPIServer:
    """完整的渔场API服务器"""
    
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.http_server = None
        self.ws_server = SimpleWebSocketServer(host, port)
        
    def start(self):
        """启动服务器"""
        logger.info(f"🐟 渔场系统API服务器启动（支持WebSocket）")
        logger.info(f"📍 HTTP地址: http://{self.host}:{self.port}")
        logger.info(f"🔌 WebSocket地址: ws://{self.host}:{self.port}/ws")
        logger.info(f"⚡ 支持的API端点:")
        logger.info(f"   - GET /api/devices - 获取设备列表")
        logger.info(f"   - GET /api/sensor-data - 获取传感器数据")
        logger.info(f"   - GET /api/alarms - 获取预警信息")
        logger.info(f"   - GET /health - 健康检查")
        logger.info(f"   - WebSocket /ws - 实时通信")
        logger.info(f"🚀 按 Ctrl+C 停止服务器")
        
        # 启动WebSocket服务器
        self.ws_server.start()
        
        # 启动HTTP服务器
        self.http_server = HTTPServer((self.host, self.port), HTTPRequestHandler)
        self.http_server.serve_forever()
    
    def stop(self):
        """停止服务器"""
        if self.ws_server:
            self.ws_server.stop()
        if self.http_server:
            self.http_server.shutdown()

if __name__ == "__main__":
    # 创建服务器实例
    server = FishFarmAPIServer(host='0.0.0.0', port=8080)
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("停止服务器")
        server.stop()