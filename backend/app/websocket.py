"""
WebSocket实时推送服务
推送实时数据到客户端
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
import json
from typing import Dict, Set
from datetime import datetime

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储所有活跃的连接
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """接受新的WebSocket连接"""
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
        logger.info(f"WebSocket连接建立: {client_id}")

    def disconnect(self, websocket: WebSocket, client_id: str):
        """断开WebSocket连接"""
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        logger.info(f"WebSocket连接断开: {client_id}")

    async def broadcast(self, client_id: str, message: dict):
        """向特定客户端广播消息"""
        if client_id not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[client_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                disconnected.add(connection)

        # 移除断开的连接
        for connection in disconnected:
            self.active_connections[client_id].discard(connection)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]

    async def send_personal(self, websocket: WebSocket, message: dict):
        """向特定连接发送消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送个人消息失败: {e}")


# 创建连接管理器实例
manager = ConnectionManager()


async def send_sensor_update(client_id: str, device_id: int, data: dict):
    """发送传感器数据更新"""
    await manager.broadcast(
        client_id,
        {
            "type": "sensor_update",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "device_id": device_id,
                **data
            }
        }
    )


async def send_device_status_update(client_id: str, device_id: int, status: int):
    """发送设备状态更新"""
    await manager.broadcast(
        client_id,
        {
            "type": "device_status_update",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "device_id": device_id,
                "status": status
            }
        }
    )


async def send_alarm_alert(client_id: str, alarm_data: dict):
    """发送预警警报"""
    await manager.broadcast(
        client_id,
        {
            "type": "alarm_alert",
            "timestamp": datetime.now().isoformat(),
            "data": alarm_data
        }
    )


async def send_production_update(client_id: str, record_data: dict):
    """发送生产记录更新"""
    await manager.broadcast(
        client_id,
        {
            "type": "production_update",
            "timestamp": datetime.now().isoformat(),
            "data": record_data
        }
    )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点"""
    client_id = None

    try:
        # 接受连接
        await websocket.accept()

        # 等待客户端发送客户端ID
        try:
            data = await websocket.receive_json()
            client_id = data.get("client_id", "unknown")
        except Exception as e:
            logger.warning(f"无法解析客户端ID: {e}")
            client_id = "unknown"

        # 注册连接
        await manager.connect(websocket, client_id)

        # 持续接收客户端消息
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            logger.info(f"收到客户端消息: {message_type}, 客户端: {client_id}")

            # 处理不同的消息类型
            if message_type == "subscribe":
                # 订阅传感器更新
                device_id = data.get("device_id")
                await send_sensor_update(client_id, device_id, {})
            elif message_type == "subscribe_status":
                # 订阅设备状态更新
                device_id = data.get("device_id")
                await send_device_status_update(client_id, device_id, 0)
            elif message_type == "unsubscribe":
                # 取消订阅
                logger.info(f"客户端 {client_id} 取消订阅")

    except WebSocketDisconnect:
        logger.info(f"客户端 {client_id} 断开连接")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
    finally:
        if client_id:
            manager.disconnect(websocket, client_id)
