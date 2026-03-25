#!/usr/bin/env python3
"""添加测试数据脚本"""

import sys
sys.path.insert(0, '/home/node/.openclaw/workspace/fishfarm-system/backend')

from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.device import Device, DeviceType, SensorData, AlarmRule, AlarmRecord, ProductionRecord
import random

def add_test_data():
    # 先初始化数据库
    from app.database import init_database
    init_database()

    db = SessionLocal()

    try:
        # 1. 添加设备类型
        device_types = [
            DeviceType(id=1, name="温度传感器", code="temperature"),
            DeviceType(id=2, name="PH传感器", code="ph"),
            DeviceType(id=3, name="氨氮传感器", code="ammonia"),
            DeviceType(id=4, name="溶氧传感器", code="dissolved_oxygen"),
            DeviceType(id=5, name="增氧泵", code="air_pump"),
        ]

        for dt in device_types:
            existing = db.query(DeviceType).filter(DeviceType.code == dt.code).first()
            if not existing:
                db.add(dt)

        db.commit()

        # 2. 添加设备
        devices = [
            Device(id=1, device_name="养殖区1号温度计", device_type_id=1, location="1号养殖池", ip_address="192.168.1.101", mqtt_topic="fishfarm/sensor/1", status=1, current_value=25.5),
            Device(id=2, device_name="养殖区PH计", device_type_id=2, location="1号养殖池", ip_address="192.168.1.102", mqtt_topic="fishfarm/sensor/2", status=1, current_value=7.2),
            Device(id=3, device_name="氨氮检测仪", device_type_id=3, location="1号养殖池", ip_address="192.168.1.103", mqtt_topic="fishfarm/sensor/3", status=1, current_value=0.15),
            Device(id=4, device_name="溶氧仪", device_type_id=4, location="1号养殖池", ip_address="192.168.1.104", mqtt_topic="fishfarm/sensor/4", status=1, current_value=6.8),
            Device(id=5, device_name="增氧泵1号", device_type_id=5, location="1号养殖池", ip_address="192.168.1.201", mqtt_topic="fishfarm/control/1", status=1, current_value=100),
        ]

        for dev in devices:
            existing = db.query(Device).filter(Device.id == dev.id).first()
            if not existing:
                db.add(dev)

        db.commit()

        # 3. 添加传感器历史数据（最近24小时）
        now = datetime.now()
        for i in range(100):
            timestamp = now - timedelta(hours=i*0.24)
            sensor_data = SensorData(
                device_id=1,
                temperature=round(25 + random.uniform(-2, 2), 2),
                ph=round(7 + random.uniform(-0.5, 0.5), 2),
                ammonia=round(0.1 + random.uniform(0, 0.2), 3),
                nitrite=round(0.05 + random.uniform(0, 0.05), 3),
                oxygen=round(6 + random.uniform(-1, 2), 2),
                created_at=timestamp
            )
            db.add(sensor_data)

        db.commit()

        # 4. 添加预警规则
        alarm_rules = [
            AlarmRule(id=1, rule_name="高温预警", sensor_type="temperature", threshold_type="max", threshold_value=30.0, level="警告", is_enabled=1),
            AlarmRule(id=2, rule_name="低温预警", sensor_type="temperature", threshold_type="min", threshold_value=20.0, level="提醒", is_enabled=1),
            AlarmRule(id=3, rule_name="PH过高预警", sensor_type="ph", threshold_type="max", threshold_value=8.5, level="警告", is_enabled=1),
            AlarmRule(id=4, rule_name="氨氮超标", sensor_type="ammonia", threshold_type="max", threshold_value=0.5, level="危险", is_enabled=1),
        ]

        for rule in alarm_rules:
            existing = db.query(AlarmRule).filter(AlarmRule.id == rule.id).first()
            if not existing:
                db.add(rule)

        db.commit()

        # 5. 添加预警记录
        alarm_records = [
            AlarmRecord(id=1, device_id=1, alarm_level="提醒", threshold_value=20.0, actual_value=19.5, message="温度低于阈值", is_resolved=0, created_at=now - timedelta(hours=2)),
            AlarmRecord(id=2, device_id=3, alarm_level="警告", threshold_value=0.3, actual_value=0.45, message="氨氮含量偏高", is_resolved=1, resolved_at=now - timedelta(hours=1), created_at=now - timedelta(hours=5)),
            AlarmRecord(id=3, device_id=4, alarm_level="危险", threshold_value=4.0, actual_value=3.2, message="溶氧严重不足", is_resolved=0, created_at=now - timedelta(minutes=30)),
        ]

        for record in alarm_records:
            existing = db.query(AlarmRecord).filter(AlarmRecord.id == record.id).first()
            if not existing:
                db.add(record)

        db.commit()

        # 6. 添加生产记录
        production_records = [
            ProductionRecord(id=1, fish_type="草鱼", quantity=500, spawn_date=datetime(2026, 1, 15), hatch_date=datetime(2026, 1, 20), growth_stage="成鱼期", weight=1.5, length=35.0, feed_amount=50.0, remark="养殖情况良好", created_at=now - timedelta(days=30)),
            ProductionRecord(id=2, fish_type="鲤鱼", quantity=300, spawn_date=datetime(2026, 2, 1), hatch_date=datetime(2026, 2, 7), growth_stage="幼鱼期", weight=0.3, length=15.0, feed_amount=20.0, remark="需要加强投喂", created_at=now - timedelta(days=20)),
            ProductionRecord(id=3, fish_type="鲫鱼", quantity=800, spawn_date=datetime(2026, 2, 20), hatch_date=datetime(2026, 2, 25), growth_stage="苗期", weight=0.05, length=5.0, feed_amount=10.0, remark="新投放鱼苗", created_at=now - timedelta(days=5)),
        ]

        for prod in production_records:
            existing = db.query(ProductionRecord).filter(ProductionRecord.id == prod.id).first()
            if not existing:
                db.add(prod)

        db.commit()

        print("✅ 测试数据添加成功！")
        print(f"  - 设备类型: {len(device_types)}")
        print(f"  - 设备: {len(devices)}")
        print(f"  - 传感器数据: 100条")
        print(f"  - 预警规则: {len(alarm_rules)}")
        print(f"  - 预警记录: {len(alarm_records)}")
        print(f"  - 生产记录: {len(production_records)}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_test_data()
