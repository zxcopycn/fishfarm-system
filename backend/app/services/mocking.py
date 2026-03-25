"""
模拟数据生成器
用于开发和测试，生成模拟的传感器数据
"""

from typing import Optional
from datetime import datetime, timedelta
import random
from app.models import Device, SensorData, ControlDevice
from app.database import get_db


class MockDataGenerator:
    """模拟数据生成器类"""

    # 水温范围（正常、警告、危险）
    TEMPERATURE_NORMAL = (22, 28)
    TEMPERATURE_WARNING = (21, 30)
    TEMPERATURE_DANGER = (18, 32)

    # PH值范围（正常、警告、危险）
    PH_NORMAL = (6.0, 6.8)
    PH_WARNING = (5.5, 7.5)
    PH_DANGER = (5.0, 8.0)

    # 溶氧量范围
    OXYGEN_NORMAL = (6, 10)
    OXYGEN_WARNING = (5, 12)
    OXYGEN_DANGER = (4, 12)

    @staticmethod
    def get_random_temperature() -> float:
        """生成随机水温"""
        level = random.choice(['normal', 'warning', 'danger'])
        if level == 'normal':
            return round(random.uniform(*MockDataGenerator.TEMPERATURE_NORMAL), 1)
        elif level == 'warning':
            return round(random.uniform(*MockDataGenerator.TEMPERATURE_WARNING), 1)
        else:
            return round(random.uniform(*MockDataGenerator.TEMPERATURE_DANGER), 1)

    @staticmethod
    def get_random_ph() -> float:
        """生成随机PH值"""
        level = random.choice(['normal', 'warning', 'danger'])
        if level == 'normal':
            return round(random.uniform(*MockDataGenerator.PH_NORMAL), 1)
        elif level == 'warning':
            return round(random.uniform(*MockDataGenerator.PH_WARNING), 1)
        else:
            return round(random.uniform(*MockDataGenerator.PH_DANGER), 1)

    @staticmethod
    def get_random_oxygen() -> float:
        """生成随机溶氧量"""
        level = random.choice(['normal', 'warning', 'danger'])
        if level == 'normal':
            return round(random.uniform(*MockDataGenerator.OXYGEN_NORMAL), 1)
        else:
            return round(random.uniform(*MockDataGenerator.OXYGEN_WARNING), 1)

    @staticmethod
    def generate_sensor_data(db: Session, device_id: int = None, hours: int = 1):
        """
        生成模拟的传感器数据并保存

        参数:
            db: 数据库会话
            device_id: 设备ID（可选，为None则生成所有设备的数据）
            hours: 生成的小时数，默认1小时

        返回:
            生成的数据数量
        """
        if device_id:
            devices = [db.query(Device).filter(Device.id == device_id).first()]
        else:
            devices = db.query(Device).filter(Device.status == 1).all()

        if not devices:
            return 0

        generated_count = 0
        start_time = datetime.now() - timedelta(hours=hours)

        for device in devices:
            # 生成每小时一次数据
            for hour_offset in range(hours):
                current_time = datetime.now() - timedelta(hours=hour_offset)

                data = SensorData(
                    device_id=device.id,
                    temperature=MockDataGenerator.get_random_temperature(),
                    ph=MockDataGenerator.get_random_ph(),
                    ammonia=round(random.uniform(0.1, 0.8), 3),
                    nitrite=round(random.uniform(0.05, 0.4), 3),
                    oxygen=MockDataGenerator.get_random_oxygen(),
                    created_at=current_time
                )
                db.add(data)
                generated_count += 1

            # 更新设备当前值
            if devices[0].id == device.id:  # 只更新第一个设备
                devices[0].current_value = float(random.uniform(20, 30))

        db.commit()
        return generated_count

    @staticmethod
    def generate_control_device_data(db: Session, hours: int = 1):
        """
        生成模拟的控制设备数据

        参数:
            db: 数据库会话
            hours: 生成的小时数，默认1小时

        返回:
            生成的数据数量
        """
        devices = db.query(ControlDevice).all()
        generated_count = 0
        start_time = datetime.now() - timedelta(hours=hours)

        for device in devices:
            for hour_offset in range(hours):
                current_time = datetime.now() - timedelta(hours=hour_offset)

                # 模拟功率波动
                power = round(random.uniform(0, device.current_power), 2)

                record = ControlRecord(
                    device_id=device.id,
                    action=random.choice(['开启', '关闭', '调节']),
                    target_value=random.uniform(0, device.current_power),
                    actual_value=power,
                    operator=random.choice(['admin', 'system', 'auto']),
                    remark="模拟数据",
                    created_at=current_time
                )
                db.add(record)
                generated_count += 1

        db.commit()
        return generated_count

    @staticmethod
    def generate_initial_devices(db: Session, count: int = 5):
        """
        初始化模拟设备数据

        参数:
            db: 数据库会话
            count: 生成设备数量，默认5个

        返回:
            生成的设备数量
        """
        device_types = ["温度传感器", "PH传感器", "氨氮传感器", "亚盐传感器", "溶氧传感器"]
        device_names = [f"鱼塘-{i+1}" for i in range(count)]

        generated_count = 0
        for name in device_names:
            device = Device(
                device_name=name,
                device_type_id=random.randint(1, 5),
                location=f"鱼塘{i+1}",
                ip_address=f"192.168.1.{100 + i}",
                mqtt_topic=f"fishfarm/sensor/{i+1}",
                status=1,
                current_value=0
            )
            db.add(device)
            generated_count += 1

        db.commit()
        return generated_count

    @staticmethod
    def generate_initial_control_devices(db: Session, count: int = 3):
        """
        初始化模拟控制设备数据

        参数:
            db: 数据库会话
            count: 生成设备数量，默认3个

        返回:
            生成的设备数量
        """
        device_types = ["水泵", "气泵", "空调", "排气扇"]
        device_names = [f"设备-{i+1}" for i in range(count)]

        generated_count = 0
        for name, dtype in zip(device_names, device_types[:count]):
            device = ControlDevice(
                device_name=name,
                device_type=device_type,
                location=f"鱼塘{i+1}",
                status=random.choice([0, 1]),
                mqtt_topic=f"fishfarm/control/{i+1}",
                current_power=random.uniform(0, 2.5)
            )
            db.add(device)
            generated_count += 1

        db.commit()
        return generated_count

    @staticmethod
    def generate_initial_production_records(db: Session, count: int = 10):
        """
        初始化模拟的生产记录数据

        参数:
            db: 数据库会话
            count: 生成记录数量，默认10条

        返回:
            生成的记录数量
        """
        fish_types = ["锦鲤", "草鱼", "鲫鱼", "罗非鱼", "鳜鱼"]
        stages = ["孵化", "育苗", "生长", "成鱼", "上市"]

        generated_count = 0
        for i in range(count):
            record = ProductionRecord(
                fish_type=random.choice(fish_types),
                quantity=round(random.uniform(1000, 50000), 1),
                spawn_date=datetime.now() - timedelta(days=random.randint(30, 365)),
                hatch_date=datetime.now() - timedelta(days=random.randint(15, 20)),
                growth_stage=random.choice(stages),
                weight=round(random.uniform(50, 2000), 1),
                length=round(random.uniform(10, 50), 1),
                feed_amount=round(random.uniform(100, 10000), 1),
                remark="模拟生产记录"
            )
            db.add(record)
            generated_count += 1

        db.commit()
        return generated_count
