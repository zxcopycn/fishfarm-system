"""
MQTT客户端管理
用于接收传感器数据和发送控制指令
"""

import json
import asyncio
import threading
from typing import Optional, Callable
from paho.mqtt import client as mqtt_client
from loguru import logger

from app.config import settings


class MQTTClient:
    """
    MQTT客户端类
    """

    def __init__(
        self,
        broker: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
    ):
        """
        初始化MQTT客户端

        参数:
            broker: MQTT broker地址
            port: MQTT端口
            username: 用户名
            password: 密码
        """
        self.broker = broker or settings.MQTT_BROKER
        self.port = port or settings.MQTT_PORT
        self.username = username or settings.MQTT_USERNAME
        self.password = password or settings.MQTT_PASSWORD

        self.client = mqtt_client.Client("fishfarm_server")
        self.on_message_callback: Optional[Callable] = None
        self.connected = False
        self._connect_thread = None

    def on_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        if rc == 0:
            print(f"MQTT连接成功，broker: {self.broker}:{self.port}")
            self.connected = True
            # 订阅传感器数据主题
            client.subscribe(f"{settings.MQTT_TOPIC_PREFIX}/#")
        else:
            print(f"MQTT连接失败，错误代码: {rc}")

    def on_message(self, client, userdata, msg):
        """MQTT消息回调"""
        topic = msg.topic
        payload = msg.payload.decode("utf-8")

        print(f"收到MQTT消息 - Topic: {topic}, Payload: {payload}")

        # 调用自定义回调函数处理消息
        if self.on_message_callback:
            self.on_message_callback(topic, payload)

        # 尝试推送到WebSocket（异步执行）
        try:
            if _mqtt_websocket_callback:
                # 解析JSON数据
                data = json.loads(payload)
                data["device_id"] = self._extract_device_id(topic)

                # 在异步上下文中执行回调
                asyncio.run_coroutine_threadsafe(
                    _mqtt_websocket_callback(data),
                    asyncio.get_event_loop()
                ).result(timeout=2)
        except json.JSONDecodeError:
            logger.warning(f"MQTT消息不是有效的JSON: {payload}")
        except Exception as e:
            logger.error(f"MQTT WebSocket推送失败: {e}")

    def _extract_device_id(self, topic: str) -> int:
        """
        从主题中提取设备ID

        参数:
            topic: MQTT主题

        返回:
            设备ID
        """
        try:
            # 假设主题格式为: fishfarm/sensor/{device_id}
            parts = topic.split("/")
            if len(parts) >= 3:
                return int(parts[-1])
        except (ValueError, IndexError):
            pass
        return 0

    def on_disconnect(self, client, userdata, rc):
        """MQTT断开连接回调"""
        print(f"MQTT断开连接，错误代码: {rc}")
        self.connected = False

    def set_message_callback(self, callback: Callable):
        """
        设置消息回调函数

        参数:
            callback: 回调函数，接收(topic, payload)参数
        """
        self.on_message_callback = callback

    def connect(self):
        """
        连接MQTT服务器
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def disconnect(self):
        """
        断开MQTT连接
        """
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            print("MQTT已断开连接")

    def publish(self, topic: str, payload: str):
        """
        发布MQTT消息

        参数:
            topic: 主题
            payload: 消息内容
        """
        if not self.connected:
            print("MQTT未连接，无法发送消息")
            return

        self.client.publish(topic, payload)
        print(f"MQTT消息已发送 - Topic: {topic}, Payload: {payload}")

    def is_connected(self) -> bool:
        """
        检查MQTT是否已连接

        返回:
            是否已连接
        """
        return self.connected


# 全局MQTT客户端实例
_mqtt_client: Optional[MQTTClient] = None

# WebSocket回调函数（用于发送实时数据）
_mqtt_websocket_callback: Optional[Callable] = None


def set_mqtt_websocket_callback(callback: Callable):
    """
    设置MQTT WebSocket回调函数

    参数:
        callback: 回调函数，接收传感器数据字典
    """
    global _mqtt_websocket_callback
    _mqtt_websocket_callback = callback


def get_mqtt_client() -> MQTTClient:
    """
    获取全局MQTT客户端实例（单例模式）
    """
    global _mqtt_client
    if _mqtt_client is None:
        _mqtt_client = MQTTClient()
    return _mqtt_client


def init_mqtt_client():
    """
    初始化MQTT客户端
    """
    global _mqtt_client
    if _mqtt_client is None:
        _mqtt_client = MQTTClient()
        try:
            _mqtt_client.connect()
            print("MQTT客户端连接成功")
        except Exception as e:
            print(f"MQTT客户端连接失败: {e}")
            print("应用将在没有MQTT的情况下继续运行")
    return _mqtt_client
