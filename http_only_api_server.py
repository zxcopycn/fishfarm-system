#!/usr/bin/env python3
"""
简化版渔场API服务器 - 只支持HTTP API
（移除WebSocket依赖，让APP能够连接）
"""

import json
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FishFarmAPI(BaseHTTPRequestHandler):
    """渔场API服务 - 仅HTTP"""
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        logger.info(f"GET请求: {path}")
        
        if path == "/":
            self._send_response({
                "name": "智能渔场环境控制监测系统",
                "version": "2.0.0",
                "status": "running",
                "docs": "/api/docs",
                "note": "WebSocket功能暂时禁用"
            })
        
        elif path == "/health":
            self._send_response({
                "status": "healthy",
                "service": "fishfarm-api",
                "websocket": "disabled"
            })
        
        elif path == "/ws":
            # WebSocket端点信息（但不支持）
            self._send_response({
                "status": "error",
                "message": "WebSocket暂不支持，请使用HTTP API",
                "http_endpoints": ["/health", "/api/devices", "/api/sensor-data"]
            })
        
        elif path == "/api/devices":
            devices = [
                {
                    "id": 1,
                    "device_id": 1,
                    "device_name": "水温传感器1",
                    "device_type_id": 1,
                    "device_type_name": "温度传感器",
                    "device_number": "TEMP_001",
                    "location": "池塘A",
                    "status": "online",
                    "last_update": datetime.now().isoformat(),
                    "description": "监测水温变化",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "device_id": 2,
                    "device_name": "PH传感器1",
                    "device_type_id": 2,
                    "device_type_name": "PH传感器",
                    "device_number": "PH_001",
                    "location": "池塘A",
                    "status": "online",
                    "last_update": datetime.now().isoformat(),
                    "description": "监测PH值变化",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": 3,
                    "device_id": 3,
                    "device_name": "溶解氧传感器1",
                    "device_type_id": 3,
                    "device_type_name": "溶解氧传感器",
                    "device_number": "OXY_001",
                    "location": "池塘A",
                    "status": "online",
                    "last_update": datetime.now().isoformat(),
                    "description": "监测溶解氧含量",
                    "created_at": datetime.now().isoformat()
                }
            ]
            self._send_response({"data": devices})
        
        elif path == "/api/sensor-data":
            sensor_data = [
                {
                    "id": 1,
                    "device_id": 1,
                    "device_name": "水温传感器1",
                    "temperature": 25.5,
                    "ph": 7.2,
                    "ammonia": 0.5,
                    "nitrite": 0.1,
                    "oxygen": 6.8,
                    "created_at": datetime.now().isoformat(),
                    "status": "normal"
                },
                {
                    "id": 2,
                    "device_id": 2,
                    "device_name": "PH传感器1",
                    "temperature": 26.0,
                    "ph": 7.0,
                    "ammonia": 0.3,
                    "nitrite": 0.05,
                    "oxygen": 7.2,
                    "created_at": datetime.now().isoformat(),
                    "status": "normal"
                },
                {
                    "id": 3,
                    "device_id": 3,
                    "device_name": "溶解氧传感器1",
                    "temperature": 25.8,
                    "ph": 7.1,
                    "ammonia": 0.4,
                    "nitrite": 0.08,
                    "oxygen": 6.5,
                    "created_at": datetime.now().isoformat(),
                    "status": "normal"
                }
            ]
            self._send_response({"data": sensor_data})
        
        elif path == "/api/alarms":
            alarms = [
                {
                    "id": 1,
                    "device_id": 1,
                    "device_name": "水温传感器1",
                    "alarm_type": "temperature",
                    "alarm_level": "warning",
                    "title": "水温偏高",
                    "description": "当前水温25.5°C，接近上限值26°C",
                    "threshold": 26.0,
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
            ]
            self._send_response({"data": alarms})
        
        elif path == "/api/production-records":
            records = [
                {
                    "id": 1,
                    "fish_type": "鲈鱼",
                    "pond_name": "池塘A",
                    "feed_amount": 50.0,
                    "operator": "张三",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "fish_type": "鲈鱼",
                    "pond_name": "池塘A",
                    "feed_amount": 30.0,
                    "operator": "李四",
                    "created_at": datetime.now().isoformat()
                }
            ]
            self._send_response({"data": records})
        
        elif path == "/api/reminders":
            reminders = [
                {
                    "id": 1,
                    "title": "定期换水",
                    "content": "池塘A每周换水一次",
                    "remind_time": datetime.now().isoformat(),
                    "completed": False,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "title": "设备巡检",
                    "content": "检查所有传感器设备运行状态",
                    "remind_time": datetime.now().isoformat(),
                    "completed": True,
                    "created_at": datetime.now().isoformat()
                }
            ]
            self._send_response({"data": reminders})
        
        else:
            self._send_error(404, "API端点不存在")
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        logger.info(f"POST请求: {path}")
        
        if path == "/api/reminders":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            reminder_data = json.loads(post_data.decode('utf-8'))
            
            new_reminder = {
                "id": str(int(time.time())),
                "title": reminder_data.get("title", ""),
                "content": reminder_data.get("content", ""),
                "remindTime": reminder_data.get("remindTime", datetime.now().isoformat()),
                "completed": False,
                "createdAt": datetime.now().isoformat()
            }
            self._send_response({"success": True, "data": new_reminder}, status_code=201)
        else:
            self._send_error(404, "API端点不存在")
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
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

def run_server():
    """启动服务器"""
    PORT = 8080
    server = HTTPServer(('0.0.0.0', PORT), FishFarmAPI)
    
    print(f"🐟 渔场系统API服务器已启动")
    print(f"📍 地址: http://localhost:{PORT}")
    print(f"📖 API文档: http://localhost:{PORT}/")
    print(f"⚡ 支持的API端点:")
    print(f" - GET /api/devices - 获取设备列表")
    print(f" - GET /api/sensor-data - 获取传感器数据")
    print(f" - GET /api/alarms - 获取预警信息")
    print(f" - GET /api/production-records - 获取生产记录")
    print(f" - GET /api/reminders - 获取提醒列表")
    print(f" - POST /api/reminders - 添加提醒")
    print(f" - GET /health - 健康检查")
    print(f"⚠️  注意: WebSocket功能暂时禁用")
    print(f"🚀 按 Ctrl+C 停止服务器")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 服务器已停止")
        server.shutdown()


if __name__ == "__main__":
    run_server()