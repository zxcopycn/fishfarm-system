"""Alembic配置模块"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from app.config import settings

# 导入所有模型以便分析数据库结构
from app.models import (
    DeviceType, Device, SensorData, AlarmRule, AlarmRecord,
    ControlDevice, ControlRecord, ProductionRecord, Reminder,
    User, Backup, UserPermission
)

# 导入SQLite迁移脚本并获取target_metadata
migration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'versions')
sys.path.insert(0, migration_dir)
import initial_001_initial_schema_sqlite as migration_script
target_metadata = migration_script.target_metadata

# Alembic Config对象，可作为上下文使用
config = context.config

# 设置数据库URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 解析日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 补充metad数据，包括所有导入的模型
target_metadata = {
    'DeviceType': DeviceType.__table__,
    'Device': Device.__table__,
    'SensorData': SensorData.__table__,
    'AlarmRule': AlarmRule.__table__,
    'AlarmRecord': AlarmRecord.__table__,
    'ControlDevice': ControlDevice.__table__,
    'ControlRecord': ControlRecord.__table__,
    'ProductionRecord': ProductionRecord.__table__,
    'Reminder': Reminder.__table__,
    'User': User.__table__,
    'Backup': Backup.__table__,
    'UserPermission': UserPermission.__table__,
}


def run_migrations_offline() -> None:
    """运行离线迁移"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """运行在线迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
