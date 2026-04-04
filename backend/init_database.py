#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有数据库表和索引
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic.config import Config
from alembic import command

# Alembic配置
alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:////home/node/.openclaw/workspace/fishfarm-system/backend/fishfarm.db")

print("=" * 60)
print("开始初始化数据库...")
print("=" * 60)

# 检查数据库文件是否存在
db_path = "/home/node/.openclaw/workspace/fishfarm-system/backend/fishfarm.db"
if os.path.exists(db_path):
    print(f"⚠️  数据库文件已存在: {db_path}")
    print("🗑️  删除现有数据库文件...")
    os.remove(db_path)
    print("✓ 数据库已重新创建")
else:
    print(f"✓ 数据库文件不存在，将创建新数据库")

# 执行迁移
print("\n执行数据库迁移...")
try:
    command.upgrade(alembic_cfg, "head")
    print("\n" + "=" * 60)
    print("✅ 数据库初始化成功！")
    print("=" * 60)
    print(f"\n数据库位置: {db_path}")
    print("已创建的表:")
    print("  1. device_types      - 设备类型表")
    print("  2. devices          - 设备表")
    print("  3. sensor_data      - 传感器数据表")
    print("  4. alarm_rules      - 预警规则表")
    print("  5. alarm_records    - 预警记录表")
    print("  6. control_devices  - 控制设备表")
    print("  7. control_records  - 控制记录表")
    print("  8. production_records - 生产记录表")
    print("  9. reminders        - 备忘提醒表")
    print("  10. users           - 用户表")
    print("  11. backups         - 备份记录表")
    print("  12. user_permissions - 用户权限表")
    print("\n🎉 准备就绪，可以开始使用渔场系统！")
    sys.exit(0)
except Exception as e:
    print("\n" + "=" * 60)
    print(f"❌ 数据库初始化失败: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
