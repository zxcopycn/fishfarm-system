"""
WebSocket实时推送服务
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
from datetime import datetime
import json
import uuid
from loguru import logger


class WebSocketConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储所有活跃的连接：{client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

        # 按用户ID存储连接：{user_id: [WebSocket, ...]}
        self.user_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, user_id: str = None):
        """
        建立WebSocket连接

        参数:
            websocket: WebSocket对象
            client_id: 客户端ID
            user_id: 用户ID
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)

        logger.info(f"WebSocket连接已建立：{client_id}, 用户ID: {user_id}")

    def disconnect(self, client_id: str, user_id: str = None):
        """
        断开WebSocket连接

        参数:
            client_id: 客户端ID
            user_id: 用户ID
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        if user_id and user_id in self.user_connections:
            if client_id in self.user_connections[user_id]:
                self.user_connections[user_id].remove(client_id)

            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info(f"WebSocket连接已断开：{client_id}")

    async def send_personal_message(self, message: dict, client_id: str):
        """
        发送个人消息

        参数:
            message: 消息字典
            client_id: 客户端ID
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败：{client_id}, {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict, user_id: str = None):
        """
        广播消息（给所有连接的客户端）

        参数:
            message: 消息字典
            user_id: 用户ID（可选，只发给该用户的客户端）
        """
        connections = (
            self.user_connections[user_id] if user_id else list(self.active_connections.values())
        )

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败：{e}")


class RealtimeService:
    """实时服务类"""

    def __init__(self):
        self.manager = WebSocketConnectionManager()
        self.client_counter = 0

    def create_client_id(self) -> str:
        """创建客户端ID"""
        self.client_counter += 1
        return f"client_{self.client_counter}_{uuid.uuid4().hex[:8]}"

    async def connect_client(self, websocket: WebSocket, user_id: str = None) -> str:
        """
        连接客户端

        参数:
            websocket: WebSocket对象
            user_id: 用户ID

        返回:
            客户端ID
        """
        client_id = self.create_client_id()
        await self.manager.connect(websocket, client_id, user_id)
        return client_id

    def disconnect_client(self, client_id: str, user_id: str = None):
        """
        断开客户端

        参数:
            client_id: 客户端ID
            user_id: 用户ID
        """
        self.manager.disconnect(client_id, user_id)

    async def send_sensor_update(self, data: dict, user_id: str = None):
        """
        发送传感器数据更新

        参数:
            data: 传感器数据
            user_id: 用户ID（可选）
        """
        message = {
            "type": "sensor_update",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        await self.manager.broadcast(message, user_id)

    async def send_alarm(self, alarm: dict, user_id: str = None):
        """
        发送预警消息

        参数:
            alarm: 预警数据
            user_id: 用户ID（可选）
        """
        message = {
            "type": "alarm",
            "timestamp": datetime.now().isoformat(),
            "data": alarm
        }

        await self.manager.broadcast(message, user_id)

    async def send_control_update(self, data: dict, user_id: str = None):
        """
        发送控制设备状态更新

        参数:
            data: 控制数据
            user_id: 用户ID（可选）
        """
        message = {
            "type": "control_update",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        await self.manager.broadcast(message, user_id)


# 全局实时服务实例
_realtime_service: RealtimeService = None


def get_realtime_service() -> RealtimeService:
    """获取实时服务实例"""
    global _realtime_service
    if _realtime_service is None:
        _realtime_service = RealtimeService()
    return _realtime_service
