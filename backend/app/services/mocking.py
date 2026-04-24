"""
模拟数据生成器
用于开发和测试，生成模拟的传感器数据
"""

from datetime import datetime, timedelta
import random
from app.models import Device, SensorData, ControlDevice, ProductionRecord, DeviceType
from app.database import SessionLocal


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
    def generate_sensor_data(device_id: int = None, hours: int = 24):
        """
        生成模拟的传感器数据并保存

        参数:
            device_id: 设备ID（可选，为None则生成所有设备的数据）
            hours: 生成的小时数，默认24小时

        返回:
            生成的数据数量
        """
        db = SessionLocal()
        try:
            if device_id:
                devices = [db.query(Device).filter(Device.id == device_id).first()]
            else:
                devices = db.query(Device).filter(Device.status == 1).all()

            if not devices:
                return 0

            generated_count = 0

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
                device.current_value = float(random.uniform(20, 30))

            db.commit()
            return generated_count
        finally:
            db.close()

    @staticmethod
    def generate_initial_device_types():
        """初始化设备类型数据"""
        db = SessionLocal()
        try:
            # 检查是否已有设备类型
            existing = db.query(DeviceType).count()
            if existing > 0:
                return 0

            device_types = [
                (1, "温度传感器", "temperature"),
                (2, "PH传感器", "ph"),
                (3, "氨氮传感器", "ammonia"),
                (4, "亚盐传感器", "nitrite"),
                (5, "溶氧传感器", "dissolved_oxygen"),
            ]

            for id, name, code in device_types:
                device_type = DeviceType(
                    id=id,
                    name=name,
                    code=code,
                    status=1
                )
                db.add(device_type)

            db.commit()
            return len(device_types)
        finally:
            db.close()

    @staticmethod
    def generate_initial_devices(count: int = 5):
        """
        初始化模拟设备数据

        参数:
            count: 生成设备数量，默认5个

        返回:
            生成的设备数量
        """
        db = SessionLocal()
        try:
            # 检查是否已有设备
            existing = db.query(Device).count()
            if existing > 0:
                return 0

            device_names = [f"鱼塘-{i+1}" for i in range(count)]

            generated_count = 0
            for i, name in enumerate(device_names):
                device = Device(
                    device_name=name,
                    device_type_id=i + 1,  # 1-5 对应5种传感器类型
                    location=f"鱼塘{i+1}",
                    ip_address=f"192.168.1.{100 + i}",
                    mqtt_topic=f"fishfarm/sensor/{i+1}",
                    status=1,
                    current_value=round(random.uniform(22, 28), 1)
                )
                db.add(device)
                generated_count += 1

            db.commit()
            return generated_count
        finally:
            db.close()

    @staticmethod
    def generate_initial_production_records(count: int = 10):
        """
        初始化模拟的生产记录数据

        参数:
            count: 生成记录数量，默认10条

        返回:
            生成的记录数量
        """
        db = SessionLocal()
        try:
            # 检查是否已有生产记录
            existing = db.query(ProductionRecord).count()
            if existing > 0:
                return 0

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
        finally:
            db.close()

    @staticmethod
    def init_all_mock_data():
        """初始化所有模拟数据"""
        print("正在检查并生成模拟数据...")
        
        # 先初始化设备类型
        type_count = MockDataGenerator.generate_initial_device_types()
        if type_count > 0:
            print(f"✅ 已生成 {type_count} 个设备类型")
        
        # 初始化设备
        device_count = MockDataGenerator.generate_initial_devices(5)
        if device_count > 0:
            print(f"✅ 已生成 {device_count} 个设备")
        
        # 初始化生产记录
        record_count = MockDataGenerator.generate_initial_production_records(10)
        if record_count > 0:
            print(f"✅ 已生成 {record_count} 条生产记录")
        
        # 生成传感器历史数据
        sensor_count = MockDataGenerator.generate_sensor_data(hours=24)
        if sensor_count > 0:
            print(f"✅ 已生成 {sensor_count} 条传感器历史数据")
        
        return type_count, device_count, record_count, sensor_count
