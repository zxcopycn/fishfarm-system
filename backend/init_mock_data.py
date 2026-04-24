#!/usr/bin/env python3
"""
手动初始化模拟数据脚本
用于在没有venv环境的服务器上运行

用法:
    python3 init_mock_data.py
"""

import sys
import os

# 添加backend路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import random

# 尝试导入app模块
try:
    from app.database import SessionLocal
    from app.models import Device, SensorData, ProductionRecord, DeviceType
    print("✅ 数据库模块加载成功")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    print("请确保已安装所有依赖: pip install fastapi uvicorn sqlalchemy pydantic-settings")
    sys.exit(1)


def generate_random_temperature():
    """生成随机水温"""
    level = random.choice(['normal', 'warning', 'danger'])
    if level == 'normal':
        return round(random.uniform(22, 28), 1)
    elif level == 'warning':
        return round(random.uniform(21, 30), 1)
    else:
        return round(random.uniform(18, 32), 1)


def generate_random_ph():
    """生成随机PH值"""
    level = random.choice(['normal', 'warning', 'danger'])
    if level == 'normal':
        return round(random.uniform(6.0, 6.8), 1)
    elif level == 'warning':
        return round(random.uniform(5.5, 7.5), 1)
    else:
        return round(random.uniform(5.0, 8.0), 1)


def generate_random_oxygen():
    """生成随机溶氧量"""
    return round(random.uniform(5, 12), 1)


def init_device_types():
    """初始化设备类型"""
    db = SessionLocal()
    try:
        existing = db.query(DeviceType).count()
        if existing > 0:
            print(f"ℹ️  设备类型已存在 ({existing} 条)，跳过")
            return 0
        
        device_types = [
            (1, "温度传感器", "temperature"),
            (2, "PH传感器", "ph"),
            (3, "氨氮传感器", "ammonia"),
            (4, "亚盐传感器", "nitrite"),
            (5, "溶氧传感器", "dissolved_oxygen"),
        ]
        
        for id, name, code in device_types:
            dt = DeviceType(id=id, name=name, code=code, status=1)
            db.add(dt)
        
        db.commit()
        print(f"✅ 已生成 {len(device_types)} 个设备类型")
        return len(device_types)
    finally:
        db.close()


def init_devices():
    """初始化设备"""
    db = SessionLocal()
    try:
        existing = db.query(Device).count()
        if existing > 0:
            print(f"ℹ️  设备已存在 ({existing} 条)，跳过")
            return 0
        
        device_names = [f"鱼塘-{i+1}" for i in range(5)]
        
        for i, name in enumerate(device_names):
            device = Device(
                device_name=name,
                device_type_id=i + 1,
                location=f"鱼塘{i+1}",
                ip_address=f"192.168.1.{100 + i}",
                mqtt_topic=f"fishfarm/sensor/{i+1}",
                status=1,
                current_value=round(random.uniform(22, 28), 1)
            )
            db.add(device)
        
        db.commit()
        print(f"✅ 已生成 {len(device_names)} 个设备")
        return len(device_names)
    finally:
        db.close()


def init_sensor_data():
    """初始化传感器数据"""
    db = SessionLocal()
    try:
        devices = db.query(Device).filter(Device.status == 1).all()
        if not devices:
            print("⚠️  没有设备，跳过传感器数据生成")
            return 0
        
        # 检查是否已有数据
        existing = db.query(SensorData).count()
        if existing > 0:
            print(f"ℹ️  传感器数据已存在 ({existing} 条)，跳过")
            return 0
        
        count = 0
        for device in devices:
            # 生成24小时数据
            for hour_offset in range(24):
                current_time = datetime.now() - timedelta(hours=hour_offset)
                data = SensorData(
                    device_id=device.id,
                    temperature=generate_random_temperature(),
                    ph=generate_random_ph(),
                    ammonia=round(random.uniform(0.1, 0.8), 3),
                    nitrite=round(random.uniform(0.05, 0.4), 3),
                    oxygen=generate_random_oxygen(),
                    created_at=current_time
                )
                db.add(data)
                count += 1
        
        db.commit()
        print(f"✅ 已生成 {count} 条传感器数据 (5设备 × 24小时)")
        return count
    finally:
        db.close()


def init_production_records():
    """初始化生产记录"""
    db = SessionLocal()
    try:
        existing = db.query(ProductionRecord).count()
        if existing > 0:
            print(f"ℹ️  生产记录已存在 ({existing} 条)，跳过")
            return 0
        
        fish_types = ["锦鲤", "草鱼", "鲫鱼", "罗非鱼", "鳜鱼"]
        stages = ["孵化", "育苗", "生长", "成鱼", "上市"]
        
        records = []
        for i in range(10):
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
            records.append(record)
        
        db.commit()
        print(f"✅ 已生成 {len(records)} 条生产记录")
        return len(records)
    finally:
        db.close()


def main():
    print("=" * 50)
    print("渔场系统 - 模拟数据初始化")
    print("=" * 50)
    print()
    
    try:
        init_device_types()
        init_devices()
        init_sensor_data()
        init_production_records()
        
        print()
        print("=" * 50)
        print("✅ 初始化完成！")
        print("=" * 50)
        print()
        print("现在可以刷新APP查看数据了。")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
