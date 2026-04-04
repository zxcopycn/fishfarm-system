"""初始数据库迁移 - SQLite版本 - 所有表结构

Revision ID: initial_001
Revises:
Create Date: 2026-04-03 10:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'initial_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建所有数据库表"""

    # 1. 设备类型表
    op.create_table(
        'device_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('status', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_device_types_id'), 'device_types', ['id'])
    op.create_index(op.f('ix_device_types_code'), 'device_types', ['code'], unique=True)
    op.create_index(op.f('ix_device_types_status'), 'device_types', ['status'])

    # 2. 设备表
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_name', sa.String(100), nullable=False),
        sa.Column('device_type_id', sa.Integer(), nullable=False),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('mqtt_topic', sa.String(200), nullable=True),
        sa.Column('status', sa.Integer(), server_default='1'),
        sa.Column('current_value', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['device_type_id'], ['device_types.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_devices_id'), 'devices', ['id'])
    op.create_index(op.f('ix_devices_device_type'), 'devices', ['device_type_id'])
    op.create_index(op.f('ix_devices_status'), 'devices', ['status'])

    # 3. 传感器数据表
    op.create_table(
        'sensor_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('ph', sa.Float(), nullable=True),
        sa.Column('ammonia', sa.Float(), nullable=True),
        sa.Column('nitrite', sa.Float(), nullable=True),
        sa.Column('oxygen', sa.Float(), nullable=True),
        sa.Column('raw_value', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensor_data_id'), 'sensor_data', ['id'])
    op.create_index(op.f('ix_sensor_data_device'), 'sensor_data', ['device_id'])
    op.create_index(op.f('ix_sensor_data_time'), 'sensor_data', ['created_at'])
    op.create_index(op.f('ix_sensor_data_temperature'), 'sensor_data', ['temperature'])
    op.create_index(op.f('ix_sensor_data_ph'), 'sensor_data', ['ph'])

    # 4. 预警规则表
    op.create_table(
        'alarm_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=True),
        sa.Column('rule_name', sa.String(100), nullable=False),
        sa.Column('sensor_type', sa.String(50), nullable=True),
        sa.Column('threshold_type', sa.String(20), nullable=False),
        sa.Column('threshold_value', sa.Float(), nullable=False),
        sa.Column('level', sa.String(20), server_default='提醒'),
        sa.Column('is_enabled', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alarm_rules_id'), 'alarm_rules', ['id'])
    op.create_index(op.f('ix_alarm_rules_device'), 'alarm_rules', ['device_id'])
    op.create_index(op.f('ix_alarm_rules_level'), 'alarm_rules', ['level'])
    op.create_index(op.f('ix_alarm_rules_enabled'), 'alarm_rules', ['is_enabled'])

    # 5. 预警记录表
    op.create_table(
        'alarm_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=True),
        sa.Column('rule_id', sa.Integer(), nullable=True),
        sa.Column('alarm_level', sa.String(20), nullable=False),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('message', sa.String(500), nullable=True),
        sa.Column('is_resolved', sa.Integer(), server_default='0'),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alarm_records_id'), 'alarm_records', ['id'])
    op.create_index(op.f('ix_alarm_records_device'), 'alarm_records', ['device_id'])
    op.create_index(op.f('ix_alarm_records_level'), 'alarm_records', ['alarm_level'])
    op.create_index(op.f('ix_alarm_records_resolved'), 'alarm_records', ['is_resolved'])
    op.create_index(op.f('ix_alarm_records_time'), 'alarm_records', ['created_at'])

    # 6. 控制设备表
    op.create_table(
        'control_devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_name', sa.String(100), nullable=False),
        sa.Column('device_type', sa.String(50), nullable=False),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('status', sa.Integer(), server_default='0'),
        sa.Column('mqtt_topic', sa.String(200), nullable=True),
        sa.Column('current_power', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_control_devices_id'), 'control_devices', ['id'])
    op.create_index(op.f('ix_control_devices_status'), 'control_devices', ['status'])

    # 7. 控制记录表
    op.create_table(
        'control_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=True),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('operator', sa.String(50), nullable=True),
        sa.Column('remark', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_control_records_id'), 'control_records', ['id'])
    op.create_index(op.f('ix_control_records_device'), 'control_records', ['device_id'])
    op.create_index(op.f('ix_control_records_time'), 'control_records', ['created_at'])

    # 8. 生产记录表
    op.create_table(
        'production_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fish_type', sa.String(100), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('spawn_date', sa.DateTime(), nullable=True),
        sa.Column('hatch_date', sa.DateTime(), nullable=True),
        sa.Column('growth_stage', sa.String(50), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('length', sa.Float(), nullable=True),
        sa.Column('feed_amount', sa.Float(), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_production_records_id'), 'production_records', ['id'])
    op.create_index(op.f('ix_production_records_fish_type'), 'production_records', ['fish_type'])
    op.create_index(op.f('ix_production_records_date'), 'production_records', ['spawn_date'])

    # 9. 备忘提醒表
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('reminder_time', sa.DateTime(), nullable=False),
        sa.Column('is_completed', sa.Integer(), server_default='0'),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reminders_id'), 'reminders', ['id'])
    op.create_index(op.f('ix_reminders_time'), 'reminders', ['reminder_time'])
    op.create_index(op.f('ix_reminders_completed'), 'reminders', ['is_completed'])

    # 10. 用户表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('real_name', sa.String(50), nullable=True),
        sa.Column('role', sa.String(20), server_default='operator'),
        sa.Column('is_active', sa.Integer(), server_default='1'),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'])
    op.create_index(op.f('ix_users_username'), 'users', ['username'])

    # 11. 备份记录表
    op.create_table(
        'backups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('backup_type', sa.String(50), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('backup_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_deleted', sa.Integer(), server_default='0'),
        sa.Column('remark', sa.String(200), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_backups_id'), 'backups', ['id'])
    op.create_index(op.f('ix_backups_time'), 'backups', ['backup_time'])

    # 12. 用户权限表
    op.create_table(
        'user_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('permission', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_permissions_id'), 'user_permissions', ['id'])
    op.create_index(op.f('ix_user_permissions_user'), 'user_permissions', ['user_id'])


# 导出target_metadata供Alembic使用
target_metadata = None


def downgrade() -> None:
    """删除所有数据库表"""
    # 删除表的顺序（反向创建的顺序）
    op.drop_table('user_permissions')
    op.drop_table('backups')
    op.drop_table('users')
    op.drop_table('reminders')
    op.drop_table('production_records')
    op.drop_table('control_records')
    op.drop_table('control_devices')
    op.drop_table('alarm_records')
    op.drop_table('alarm_rules')
    op.drop_table('sensor_data')
    op.drop_table('devices')
    op.drop_table('device_types')
