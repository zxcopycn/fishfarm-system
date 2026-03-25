"""
数据验证工具函数
"""

from typing import Optional
from decimal import Decimal
from app.models.device import AlarmLevel
import enum


class SensorType(str, enum.Enum):
    """传感器类型枚举"""
    TEMPERATURE = "temperature"  # 温度传感器
    PH = "ph"  # PH传感器
    AMMONIA = "ammonia"  # 氨氮传感器
    NITRITE = "nitrite"  # 亚盐传感器
    DISSOLVED_OXYGEN = "dissolved_oxygen"  # 溶氧传感器
    OXYGEN = "oxygen"  # 溶氧传感器（新命名）


class DeviceStatus(str, enum.Enum):
    """设备状态枚举"""
    ONLINE = "online"  # 在线
    OFFLINE = "offline"  # 离线


class ControlStatus(str, enum.Enum):
    """控制设备状态枚举"""
    ON = 1  # 开启
    OFF = 0  # 关闭


class AlarmLevel(str, enum.Enum):
    """预警级别枚举"""
    REMIND = "提醒"
    WARNING = "警告"
    DANGER = "危险"


# 默认阈值配置（可根据实际情况调整）
DEFAULT_THRESHOLDS = {
    # 水温（℃）
    "temperature": {
        "提醒": {"min": 21, "max": 30},
        "警告": {"min": 18, "max": 32},
        "危险": {"min": 18, "max": 32},
    },
    # PH值
    "ph": {
        "提醒": {"min": 5.5, "max": 7.5},
        "警告": {"min": 5.5, "max": 8},
        "危险": {"min": 5, "max": 8},
    },
    # 氨氮（mg/L）- 示例阈值，可根据实际设备调整
    "ammonia": {
        "正常": {"min": 0, "max": 0.5},
        "提醒": {"min": 0.5, "max": 1},
        "警告": {"min": 1, "max": 1.5},
        "危险": {"min": 1.5, "max": 2},
    },
    # 亚盐（mg/L）- 示例阈值，可根据实际设备调整
    "nitrite": {
        "正常": {"min": 0, "max": 0.3},
        "提醒": {"min": 0.1, "max": 0.5},
        "警告": {"min": 0.3, "max": 0.5},
        "危险": {"min": 0.5, "max": 1},
    },
    # 溶氧量（mg/L）- 示例阈值，可根据实际设备调整
    "dissolved_oxygen": {
        "正常": {"min": 5, "max": 10},
        "提醒": {"min": 3, "max": 5},
        "警告": {"min": 4, "max": 12},
        "危险": {"min": 4, "max": 12},
    },
    # 氧含量（mg/L）- 新命名，与溶氧量对应
    "oxygen": {
        "正常": {"min": 5, "max": 10},
        "提醒": {"min": 3, "max": 5},
        "警告": {"min": 4, "max": 12},
        "危险": {"min": 4, "max": 12},
    },
}


def validate_sensor_value(
    sensor_type: str,
    value: Optional[float],
    device_id: int = None
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    验证传感器数值是否符合预警规则

    参数:
        sensor_type: 传感器类型
        value: 传感器数值
        device_id: 设备ID（可选，用于精确匹配规则）

    返回:
        (is_alarm: 是否触发预警, alarm_level: 预警级别, message: 预警消息)
    """
    if value is None:
        return False, None, None

    # 获取传感器类型的配置
    thresholds = DEFAULT_THRESHOLDS.get(sensor_type)
    if not thresholds:
        return False, None, f"未知传感器类型：{sensor_type}"

    # 检查是否触发各级别预警
    for level_str, limit in thresholds.items():
        level = AlarmLevel(level_str)

        # 检查是否低于最小值
        if "min" in limit and value < limit["min"]:
            message = (
                f"{sensor_type}数值为 {value:.2f}，低于{level_str}阈值 {limit['min']}，"
                f"当前级别为 {level_str}"
            )
            return True, level, message

        # 检查是否高于最大值
        if "max" in limit and value > limit["max"]:
            message = (
                f"{sensor_type}数值为 {value:.2f}，高于{level_str}阈值 {limit['max']}，"
                f"当前级别为 {level_str}"
            )
            return True, level, message

    # 未触发预警
    return False, None, None


def format_sensor_value(value: Optional[float], precision: int = 2) -> str:
    """
    格式化传感器数值

    参数:
        value: 传感器数值
        precision: 小数位数

    返回:
        格式化后的字符串
    """
    if value is None:
        return "N/A"
    return f"{value:.{precision}f}"


def get_threshold_by_type(sensor_type: str) -> dict:
    """
    根据传感器类型获取阈值配置

    参数:
        sensor_type: 传感器类型

    返回:
        阈值配置字典
    """
    return DEFAULT_THRESHOLDS.get(sensor_type, {})
