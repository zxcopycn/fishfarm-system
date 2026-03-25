"""
传感器数据处理服务
"""

import asyncio
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from app.models import Device, SensorData, AlarmRule, AlarmRecord
from app.utils import validate_sensor_value
from app.utils.mqtt_client import set_mqtt_websocket_callback


# 设置MQTT WebSocket回调函数
def setup_sensor_websocket_callback():
    """
    设置传感器数据WebSocket回调函数
    """
    def callback(sensor_data: Dict):
        """
        回调函数，推送传感器数据到WebSocket

        参数:
            sensor_data: 传感器数据字典
        """
        try:
            from app.websocket import send_sensor_update
            asyncio.run_coroutine_threadsafe(
                send_sensor_update("dashboard", sensor_data["device_id"], {
                    "temperature": sensor_data.get("temperature"),
                    "ph": sensor_data.get("ph"),
                    "ammonia": sensor_data.get("ammonia"),
                    "nitrite": sensor_data.get("nitrite"),
                    "oxygen": sensor_data.get("oxygen"),
                }),
                asyncio.get_event_loop()
            ).result(timeout=1)
        except Exception as e:
            pass  # 静默失败，不影响主流程

    set_mqtt_websocket_callback(callback)


class SensorService:
    """传感器服务类"""

    @staticmethod
    def save_sensor_data(
        db: Session,
        device_id: int,
        temperature: Optional[float] = None,
        ph: Optional[float] = None,
        ammonia: Optional[float] = None,
        nitrite: Optional[float] = None,
        oxygen: Optional[float] = None,
        raw_value: str = ""
    ):
        """
        保存传感器数据并检查是否触发预警

        参数:
            db: 数据库会话
            device_id: 设备ID
            temperature: 温度
            ph: PH值
            ammonia: 氨氮
            nitrite: 亚盐
            oxygen: 溶氧
            raw_value: 原始数据

        返回:
            触发的预警列表
        """
        # 保存传感器数据
        sensor_data = SensorData(
            device_id=device_id,
            temperature=temperature,
            ph=ph,
            ammonia=ammonia,
            nitrite=nitrite,
            oxygen=oxygen,
            raw_value=raw_value
        )
        db.add(sensor_data)

        # 更新设备当前值
        device = db.query(Device).filter(Device.id == device_id).first()
        if device:
            device.current_value = float(temperature or 0)
            device.status = 1  # 设备在线

        db.commit()

        # 检查预警
        alarms = []
        sensors = [
            ("temperature", temperature),
            ("ph", ph),
            ("ammonia", ammonia),
            ("nitrite", nitrite),
            ("dissolved_oxygen", oxygen),
        ]

        for sensor_type, value in sensors:
            if value is not None:
                is_alarm, alarm_level, message = validate_sensor_value(sensor_type, value, device_id)
                if is_alarm:
                    alarms.append({
                        "level": alarm_level.value,
                        "message": message,
                        "value": value
                    })

                    # 保存预警记录
                    alarm_record = AlarmRecord(
                        device_id=device_id,
                        alarm_level=alarm_level,
                        threshold_value=0,
                        actual_value=value,
                        message=message,
                        is_resolved=0
                    )
                    db.add(alarm_record)

        db.commit()

        return alarms

    @staticmethod
    def get_latest_devices(db: Session, limit: int = 20):
        """
        获取最新传感器数据的设备列表

        参数:
            db: 数据库会话
            limit: 返回条数

        返回:
            设备列表及其最新数据
        """
        query = db.query(Device, SensorData).join(
            SensorData, Device.id == SensorData.device_id
        ).order_by(
            SensorData.created_at.desc()
        ).limit(limit * 2)  # 增加数量以确保每个设备都能取到

        results = []
        device_map = {}

        for device, sensor_data in query:
            if device.id not in device_map:
                device_map[device.id] = {
                    "device": device,
                    "data": sensor_data
                }

        for device_data in list(device_map.values())[:limit]:
            device = device_data["device"]
            sensor_data = device_data["data"]

            results.append({
                "id": device.id,
                "device_name": device.device_name,
                "device_type_id": device.device_type_id,
                "device_type_name": "未知类型",
                "temperature": sensor_data.temperature,
                "ph": sensor_data.ph,
                "ammonia": sensor_data.ammonia,
                "nitrite": sensor_data.nitrite,
                "oxygen": sensor_data.oxygen,
                "status": device.status,
                "created_at": sensor_data.created_at,
                "time_ago": str(sensor_data.created_at.strftime("%H:%M:%S"))
            })

        return results
