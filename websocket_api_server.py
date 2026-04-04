#!/usr/bin/env python3
"""
支持WebSocket的渔场API服务器
结合HTTP API和WebSocket实时通信
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import websockets
import ssl

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FishFarmAPI:
    """渔场API服务器 - 支持HTTP和WebSocket"""
    
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.clients = set()
        self.devices = self._get_mock_devices()
        self.sensor_data = self._get_mock_sensor_data()
        
    def _get_mock_devices(self):
        """获取模拟设备数据"""
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
    
    def _get_mock_sensor_data(self):
        """获取模拟传感器数据"""
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
    
    async def register_client(self, websocket):
        """注册WebSocket客户端"""
        self.clients.add(websocket)
        logger.info(f"客户端连接: {websocket.remote_address}")
        
        # 发送初始数据
        await self.send_data_to_client(websocket, {
            "type": "connection_established",
            "client_id": id(websocket),
            "timestamp": datetime.now().isoformat()
        })
        
        # 发送设备列表
        await self.send_data_to_client(websocket, {
            "type": "device_list",
            "data": self.devices
        })
        
        # 发送传感器数据
        await self.send_data_to_client(websocket, {
            "type": "sensor_data",
            "data": self.sensor_data
        })
    
    async def unregister_client(self, websocket):
        """注销WebSocket客户端"""
        self.clients.discard(websocket)
        logger.info(f"客户端断开: {websocket.remote_address}")
    
    async def send_data_to_client(self, websocket, data):
        """向单个客户端发送数据"""
        try:
            await websocket.send(json.dumps(data, ensure_ascii=False))
        except websockets.exceptions.ConnectionClosed:
            await self.unregister_client(websocket)
    
    async def broadcast_data(self, data):
        """广播数据到所有客户端"""
        if self.clients:
            message = json.dumps(data, ensure_ascii=False)
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
            logger.info(f"广播数据到 {len(self.clients)} 个客户端: {data.get('type', 'unknown')}")
    
    async def handle_client_message(self, websocket, message):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            logger.info(f"收到客户端消息: {data}")
            
            response = {"type": "response", "status": "success", "received": data}
            
            if data.get("type") == "subscribe":
                # 订阅设备更新
                device_id = data.get("device_id")
                logger.info(f"客户端订阅设备: {device_id}")
                response.update({"message": f"已订阅设备 {device_id}"})
                
            elif data.get("type") == "unsubscribe":
                # 取消订阅
                logger.info("客户端取消订阅")
                response.update({"message": "已取消订阅"})
                
            elif data.get("type") == "connect":
                # 连接确认
                response.update({"message": "连接成功", "client_id": id(websocket)})
                
            await self.send_data_to_client(websocket, response)
            
        except json.JSONDecodeError:
            await self.send_data_to_client(websocket, {
                "type": "error", 
                "status": "invalid_json", 
                "message": "无效的JSON格式"
            })
        except Exception as e:
            logger.error(f"处理客户端消息错误: {e}")
            await self.send_data_to_client(websocket, {
                "type": "error", 
                "status": "error", 
                "message": str(e)
            })
    
    async def handle_client(self, websocket, path):
        """处理WebSocket客户端"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    def start_http_server(self):
        """启动HTTP服务器（线程版本）"""
        import threading
        import socketserver
        import sys
        
        # 修改HTTP服务器处理程序
        class HTTPRequestHandler(BaseHTTPRequestHandler):
            server = None
            
            def do_GET(self):
                parsed_path = urlparse(self.path)
                path = parsed_path.path
                query = parse_qs(parsed_path.query)
                
                logger.info(f"HTTP GET请求: {path}")
                
                if path == "/":
                    self._send_response({
                        "name": "智能渔场环境控制监测系统",
                        "version": "2.0.0",
                        "status": "running",
                        "docs": "/api/docs",
                        "websocket": "/ws"
                    })
                
                elif path == "/health":
                    self._send_response({
                        "status": "healthy", 
                        "service": "fishfarm-api",
                        "websocket_supported": True,
                        "websocket_endpoint": "/ws"
                    })
                
                elif path == "/ws":
                    self._send_response({
                        "message": "WebSocket端点，请使用WebSocket协议连接",
                        "connection_type": "websocket",
                        "url": "ws://0.0.0.0:8080/ws"
                    })
                
                elif path == "/api/devices":
                    self._send_response({"data": self.server.devices})
                
                elif path == "/api/sensor-data":
                    self._send_response({"data": self.server.sensor_data})
                
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
        
        HTTPRequestHandler.server = self
        
        # 启动HTTP服务器
        http_server = HTTPServer((self.host, self.port), HTTPRequestHandler)
        logger.info(f"HTTP服务器启动在 http://{self.host}:{self.port}")
        
        try:
            http_server.serve_forever()
        except KeyboardInterrupt:
            logger.info("HTTP服务器停止")
            http_server.shutdown()
    
    async def start_websocket_server(self):
        """启动WebSocket服务器"""
        logger.info(f"WebSocket服务器启动在 ws://{self.host}:{self.port}/ws")
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=20
        ):
            logger.info("WebSocket服务器已启动")
            await asyncio.Future()  # 永远运行
    
    async def start_data_simulation(self):
        """模拟数据更新"""
        while True:
            await asyncio.sleep(30)  # 每30秒更新一次
            
            # 模拟数据变化
            import random
            for device in self.devices:
                if device["status"] == "online":
                    # 随机更新传感器数据
                    if random.random() < 0.3:  # 30%概率更新
                        device["lastUpdate"] = datetime.now().isoformat()
                        logger.info(f"更新设备 {device['name']}")
                        
                        # 广播设备更新
                        await self.broadcast_data({
                            "type": "device_update",
                            "device": device
                        })
            
            # 模拟传感器数据更新
            for sensor in self.sensor_data:
                if random.random() < 0.4:  # 40%概率更新
                    # 小幅度随机变化
                    variation = random.uniform(-0.5, 0.5)
                    sensor["value"] = round(float(sensor["value"]) + variation, 1)
                    sensor["timestamp"] = datetime.now().isoformat()
                    sensor["status"] = "normal" if 5 < sensor["value"] < 30 else "warning"
                    
                    logger.info(f"更新传感器 {sensor['sensorType']}: {sensor['value']}{sensor['unit']}")
                    
                    # 广播传感器数据更新
                    await self.broadcast_data({
                        "type": "sensor_update",
                        "data": sensor
                    })
    
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
        
        # 在新线程中启动HTTP服务器
        http_thread = threading.Thread(target=self.start_http_server)
        http_thread.daemon = True
        http_thread.start()
        
        # 在主线程中启动WebSocket和数据模拟
        asyncio.run(self.start_websocket_and_simulation())
    
    async def start_websocket_and_simulation(self):
        """启动WebSocket服务器和数据模拟"""
        await asyncio.gather(
            self.start_websocket_server(),
            self.start_data_simulation()
        )

if __name__ == "__main__":
    # 检查websockets库
    try:
        import websockets
    except ImportError:
        logger.error("❌ websockets库未安装")
        logger.error("请运行: pip install websockets")
        logger.error("或者使用系统包管理器安装")
        sys.exit(1)
    
    # 创建并启动服务器
    server = FishFarmAPI(host='0.0.0.0', port=8080)
    server.start()