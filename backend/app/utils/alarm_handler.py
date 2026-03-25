"""
预警处理工具
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import AlarmRule, AlarmRecord
from app.utils.date_utils import format_datetime


class AlarmHandler:
    """预警处理器"""

    @staticmethod
    def check_sensor_values(device_id: int, sensor_data: list, db: Session):
        """
        检查传感器数据是否触发预警

        参数:
            device_id: 设备ID
            sensor_data: 传感器数据列表
            db: 数据库会话

        返回:
            生成的预警记录列表
        """
        new_records = []

        for data in sensor_data:
            sensor_type = data.get('sensor_type')
            value = data.get('value')
            threshold_type = data.get('threshold_type', 'gt')

            # 查找匹配的预警规则
            rules = db.query(AlarmRule).filter(
                AlarmRule.device_id == device_id,
                AlarmRule.sensor_type == sensor_type,
                AlarmRule.is_enabled == 1
            ).all()

            for rule in rules:
                if AlarmHandler._check_threshold(value, rule, threshold_type):
                    # 创建预警记录
                    record = AlarmRecord(
                        device_id=device_id,
                        alarm_level=rule.level,
                        threshold_value=rule.threshold_value,
                        actual_value=value,
                        message=f"{sensor_type}超出阈值: {value}",
                        is_resolved=0
                    )
                    new_records.append(record)

        return new_records

    @staticmethod
    def _check_threshold(value: float, rule: AlarmRule, threshold_type: str) -> bool:
        """
        检查阈值是否被触发

        参数:
            value: 当前值
            rule: 预警规则
            threshold_type: 阈值类型

        返回:
            是否触发预警
        """
        threshold = float(rule.threshold_value)

        if threshold_type == 'gt':
            return value > threshold
        elif threshold_type == 'lt':
            return value < threshold
        elif threshold_type == 'gte':
            return value >= threshold
        elif threshold_type == 'lte':
            return value <= threshold

        return False

    @staticmethod
    def create_alarm_record(
        db: Session,
        device_id: int,
        sensor_type: str,
        level: str,
        threshold_value: float,
        actual_value: float,
        message: str
    ):
        """
        创建预警记录

        参数:
            db: 数据库会话
            device_id: 设备ID
            sensor_type: 传感器类型
            level: 预警级别
            threshold_value: 阈值
            actual_value: 实际值
            message: 消息

        返回:
            创建的预警记录
        """
        from app.models import AlarmRecord

        record = AlarmRecord(
            device_id=device_id,
            alarm_level=level,
            threshold_value=threshold_value,
            actual_value=actual_value,
            message=message,
            is_resolved=0
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
