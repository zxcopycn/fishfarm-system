#!/usr/bin/env python3
"""
直接使用SQLAlchemy创建数据库表
绕过alembic配置问题
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from app.models import DeviceType, Device, SensorData, AlarmRule, AlarmRecord, ControlDevice, ControlRecord, ProductionRecord, Reminder, User, Backup, UserPermission

def create_tables():
    """创建所有数据库表"""
    print("=" * 60)
    print("开始创建数据库表...")
    print("=" * 60)
    
    try:
        # 创建所有表，忽略已存在的对象
        from app.database import Base
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        print("\n✅ 数据库表创建成功！")
        print("=" * 60)
        print("\n已创建的表:")
        tables = [
            "device_types", "devices", "sensor_data",
            "alarm_rules", "alarm_records", "control_devices",
            "control_records", "production_records", "reminders",
            "users", "backups", "user_permissions"
        ]
        for i, table in enumerate(tables, 1):
            print(f"  {i:2d}. {table}")
        
        print(f"\n🎉 数据库位置: /home/node/.openclaw/workspace/fishfarm-system/backend/fishfarm.db")
        print("🚀 渔场系统已准备就绪！")
        return True
        
    except Exception as e:
        print(f"\n❌ 创建数据库表失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)