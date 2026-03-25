#!/bin/bash

BASE_URL="http://127.0.0.1:8003"

echo "添加测试数据..."

# 1. 添加提醒
echo "1. 添加提醒..."
curl -s -X POST "$BASE_URL/api/reminders" \
  -H "Content-Type: application/json" \
  -d '{"title": "水温检查", "content": "检查养殖区水温是否正常", "reminder_time": "2026-03-25T14:00:00"}' | jq -r '.title'

curl -s -X POST "$BASE_URL/api/reminders" \
  -H "Content-Type: application/json" \
  -d '{"title": "投喂时间", "content": "下午投喂鱼饲料", "reminder_time": "2026-03-25T16:00:00"}' | jq -r '.title'

# 2. 添加设备（通过SQL直接插入）
echo "2. 添加设备..."
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace/fishfarm-system/backend')
from app.database import SessionLocal
from app.models.device import Device, DeviceType

db = SessionLocal()
try:
    types = [
        DeviceType(id=1, name="温度传感器", code="temperature"),
        DeviceType(id=2, name="PH传感器", code="ph"),
        DeviceType(id=3, name="氨氮传感器", code="ammonia"),
        DeviceType(id=4, name="溶氧传感器", code="dissolved_oxygen"),
        DeviceType(id=5, name="增氧泵", code="air_pump"),
    ]
    for t in types:
        try:
            db.add(t)
        except:
            pass

    devices = [
        Device(id=1, device_name="养殖区1号温度计", device_type_id=1, location="1号养殖池", ip_address="192.168.1.101", mqtt_topic="fishfarm/sensor/1", status=1, current_value=25.5),
        Device(id=2, device_name="养殖区PH计", device_type_id=2, location="1号养殖池", ip_address="192.168.1.102", mqtt_topic="fishfarm/sensor/2", status=1, current_value=7.2),
        Device(id=3, device_name="氨氮检测仪", device_type_id=3, location="1号养殖池", ip_address="192.168.1.103", mqtt_topic="fishfarm/sensor/3", status=1, current_value=0.15),
        Device(id=4, device_name="溶氧仪", device_type_id=4, location="1号养殖池", ip_address="192.168.1.104", mqtt_topic="fishfarm/sensor/4", status=1, current_value=6.8),
        Device(id=5, device_name="增氧泵1号", device_type_id=5, location="1号养殖池", ip_address="192.168.1.201", mqtt_topic="fishfarm/control/1", status=1, current_value=100),
    ]
    for d in devices:
        try:
            db.add(d)
        except:
            pass

    db.commit()
    print("设备数据添加成功")
except Exception as e:
    print(f"错误: {e}")
    db.rollback()
finally:
    db.close()
EOF

# 3. 添加预警规则
echo "3. 添加预警规则..."
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace/fishfarm-system/backend')
from app.database import SessionLocal
from app.models.device import AlarmRule

db = SessionLocal()
try:
    rules = [
        AlarmRule(id=1, rule_name="高温预警", sensor_type="temperature", threshold_type="max", threshold_value=30.0, level="WARNING", is_enabled=1),
        AlarmRule(id=2, rule_name="低温预警", sensor_type="temperature", threshold_type="min", threshold_value=20.0, level="REMIND", is_enabled=1),
        AlarmRule(id=3, rule_name="PH过高预警", sensor_type="ph", threshold_type="max", threshold_value=8.5, level="WARNING", is_enabled=1),
        AlarmRule(id=4, rule_name="氨氮超标", sensor_type="ammonia", threshold_type="max", threshold_value=0.5, level="DANGER", is_enabled=1),
    ]
    for r in rules:
        try:
            db.add(r)
        except:
            pass
    db.commit()
    print("预警规则添加成功")
except Exception as e:
    print(f"错误: {e}")
    db.rollback()
finally:
    db.close()
EOF

# 4. 添加预警记录
echo "4. 添加预警记录..."
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace/fishfarm-system/backend')
from app.database import SessionLocal
from app.models.device import AlarmRecord
from datetime import datetime, timedelta

db = SessionLocal()
now = datetime.now()
try:
    records = [
        AlarmRecord(id=1, device_id=1, alarm_level="REMIND", threshold_value=20.0, actual_value=19.5, message="温度低于阈值", is_resolved=0, created_at=now - timedelta(hours=2)),
        AlarmRecord(id=2, device_id=3, alarm_level="WARNING", threshold_value=0.3, actual_value=0.45, message="氨氮含量偏高", is_resolved=1, resolved_at=now - timedelta(hours=1), created_at=now - timedelta(hours=5)),
        AlarmRecord(id=3, device_id=4, alarm_level="DANGER", threshold_value=4.0, actual_value=3.2, message="溶氧严重不足", is_resolved=0, created_at=now - timedelta(minutes=30)),
    ]
    for r in records:
        try:
            db.add(r)
        except:
            pass
    db.commit()
    print("预警记录添加成功")
except Exception as e:
    print(f"错误: {e}")
    db.rollback()
finally:
    db.close()
EOF

# 5. 添加生产记录
echo "5. 添加生产记录..."
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace/fishfarm-system/backend')
from app.database import SessionLocal
from app.models.device import ProductionRecord
from datetime import datetime, timedelta

db = SessionLocal()
now = datetime.now()
try:
    records = [
        ProductionRecord(id=1, fish_type="草鱼", quantity=500, spawn_date=datetime(2026, 1, 15), hatch_date=datetime(2026, 1, 20), growth_stage="成鱼期", weight=1.5, length=35.0, feed_amount=50.0, remark="养殖情况良好", created_at=now - timedelta(days=30)),
        ProductionRecord(id=2, fish_type="鲤鱼", quantity=300, spawn_date=datetime(2026, 2, 1), hatch_date=datetime(2026, 2, 7), growth_stage="幼鱼期", weight=0.3, length=15.0, feed_amount=20.0, remark="需要加强投喂", created_at=now - timedelta(days=20)),
        ProductionRecord(id=3, fish_type="鲫鱼", quantity=800, spawn_date=datetime(2026, 2, 20), hatch_date=datetime(2026, 2, 25), growth_stage="苗期", weight=0.05, length=5.0, feed_amount=10.0, remark="新投放鱼苗", created_at=now - timedelta(days=5)),
    ]
    for r in records:
        try:
            db.add(r)
        except:
            pass
    db.commit()
    print("生产记录添加成功")
except Exception as e:
    print(f"错误: {e}")
    db.rollback()
finally:
    db.close()
EOF

echo "✅ 测试数据添加完成！"
