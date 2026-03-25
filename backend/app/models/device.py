"""
设备相关数据模型
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey, Index, Enum, Text, SmallInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional
import enum

Base = declarative_base()


class DeviceTypeEnum(str, enum.Enum):
    """设备类型枚举"""
    TEMPERATURE = "temperature"  # 温度传感器
    PH = "ph"  # PH传感器
    AMMONIA = "ammonia"  # 氨氮传感器
    NITRITE = "nitrite"  # 亚盐传感器
    DISSOLVED_OXYGEN = "dissolved_oxygen"  # 溶氧传感器
    WATER_PUMP = "water_pump"  # 水泵
    AIR_PUMP = "air_pump"  # 气泵
    AIR_CONDITIONER = "air_conditioner"  # 空调
    EXHAUST_FAN = "exhaust_fan"  # 排气扇


class DeviceStatus(str, enum.Enum):
    """设备状态枚举"""
    ONLINE = "online"  # 在线
    OFFLINE = "offline"  # 离线


class ControlStatus(str, enum.Enum):
    """控制设备状态枚举"""
    ON = 1  # 开启
    OFF = 0  # 关闭


class AlarmLevel(str, enum.Enum):
    """预警级别枚举"""
    REMIND = "提醒"
    WARNING = "警告"
    DANGER = "危险"


class DeviceType(Base):
    """
    设备类型表
    """

    __tablename__ = "device_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="设备类型名称")
    code = Column(String(50), nullable=False, unique=True, comment="设备类型代码")
    status = Column(SmallInteger, default=1, comment="状态：1-启用 0-禁用")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<DeviceType(id={self.id}, name={self.name}, code={self.code})>"


class Device(Base):
    """
    设备表
    存储所有传感器和控制设备的元信息
    """

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String(100), nullable=False, comment="设备名称")
    device_type_id = Column(Integer, ForeignKey("device_types.id", ondelete="RESTRICT"), nullable=False, comment="设备类型ID")
    location = Column(String(200), comment="安装位置")
    ip_address = Column(String(50), comment="IP地址")
    mqtt_topic = Column(String(200), comment="MQTT主题")
    status = Column(SmallInteger, default=1, comment="状态：1-在线 0-离线")
    current_value = Column(DECIMAL(10, 2), comment="当前值")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_device_type", "device_type_id"),
        Index("idx_status", "status"),
    )

    def __repr__(self):
        return f"<Device(id={self.id}, name={self.device_name}, type={self.device_type_id})>"


class SensorData(Base):
    """
    传感器数据表（实时数据）
    存储每秒采集的传感器数据
    """

    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, comment="设备ID")
    temperature = Column(DECIMAL(5, 2), comment="温度(℃)")
    ph = Column(DECIMAL(4, 2), comment="PH值")
    ammonia = Column(DECIMAL(6, 3), comment="氨氮(mg/L)")
    nitrite = Column(DECIMAL(6, 3), comment="亚盐(mg/L)")
    oxygen = Column(DECIMAL(5, 2), comment="溶氧量(mg/L)")
    raw_value = Column(Text, comment="原始数据")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_device", "device_id"),
        Index("idx_time", "created_at"),
        Index("idx_temperature", "temperature"),
        Index("idx_ph", "ph"),
    )

    def __repr__(self):
        return f"<SensorData(id={self.id}, device_id={self.device_id}, temperature={self.temperature})>"


class AlarmRule(Base):
    """
    预警规则表
    定义各种参数的预警阈值规则
    """

    __tablename__ = "alarm_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), comment="设备ID（NULL表示全局规则）")
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    sensor_type = Column(String(50), comment="传感器类型")
    threshold_type = Column(String(20), nullable=False, comment="阈值类型：min-最小值，max-最大值，range-范围")
    threshold_value = Column(DECIMAL(10, 2), nullable=False, comment="阈值数值")
    level = Column(String(20), default="提醒", comment="预警级别：提醒/警告/危险")
    is_enabled = Column(SmallInteger, default=1, comment="是否启用：1-启用 0-禁用")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_device", "device_id"),
        Index("idx_level", "level"),
        Index("idx_enabled", "is_enabled"),
    )

    def __repr__(self):
        return f"<AlarmRule(id={self.id}, name={self.rule_name}, level={self.level})>"


class AlarmRecord(Base):
    """
    预警记录表
    记录所有触发预警的历史记录
    """

    __tablename__ = "alarm_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, comment="设备ID")
    rule_id = Column(Integer, comment="规则ID")
    alarm_level = Column(Enum(AlarmLevel), nullable=False, comment="预警级别")
    threshold_value = Column(DECIMAL(10, 2), comment="阈值数值")
    actual_value = Column(DECIMAL(10, 2), comment="实际数值")
    message = Column(String(500), comment="预警消息")
    is_resolved = Column(SmallInteger, default=0, comment="是否已解决：1-已解决 0-未解决")
    resolved_at = Column(TIMESTAMP, comment="解决时间")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_device", "device_id"),
        Index("idx_level", "alarm_level"),
        Index("idx_resolved", "is_resolved"),
        Index("idx_time", "created_at"),
    )

    def __repr__(self):
        return f"<AlarmRecord(id={self.id}, level={self.alarm_level}, resolved={self.is_resolved})>"


class ControlDevice(Base):
    """
    控制设备表
    存储可远程控制的设备（水泵、气泵、空调等）
    """

    __tablename__ = "control_devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String(100), nullable=False, comment="设备名称")
    device_type = Column(String(50), nullable=False, comment="设备类型")
    location = Column(String(200), comment="安装位置")
    status = Column(SmallInteger, default=0, comment="状态：1-开启 0-关闭")
    mqtt_topic = Column(String(200), comment="MQTT主题")
    current_power = Column(DECIMAL(5, 2), comment="当前功率(kW)")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_status", "status"),
    )

    def __repr__(self):
        return f"<ControlDevice(id={self.id}, name={self.device_name}, status={self.status})>"


class ControlRecord(Base):
    """
    设备控制记录表
    记录所有设备控制操作的历史记录
    """

    __tablename__ = "control_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey("control_devices.id", ondelete="CASCADE"), nullable=False, comment="控制设备ID")
    action = Column(String(20), nullable=False, comment="操作类型：开启/关闭/调节")
    target_value = Column(DECIMAL(10, 2), comment="目标数值")
    actual_value = Column(DECIMAL(10, 2), comment="实际数值")
    operator = Column(String(50), comment="操作人")
    remark = Column(String(200), comment="备注")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_device", "device_id"),
        Index("idx_time", "created_at"),
    )

    def __repr__(self):
        return f"<ControlRecord(id={self.id}, device_id={self.device_id}, action={self.action})>"


class ProductionRecord(Base):
    """
    生产记录表
    记录鱼类繁育、养殖等生产数据
    """

    __tablename__ = "production_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fish_type = Column(String(100), comment="鱼类品种")
    quantity = Column(DECIMAL(10, 2), comment="数量")
    spawn_date = Column(TIMESTAMP, comment="产卵日期")
    hatch_date = Column(TIMESTAMP, comment="孵化日期")
    growth_stage = Column(String(50), comment="生长阶段")
    weight = Column(DECIMAL(10, 2), comment="体重(g)")
    length = Column(DECIMAL(10, 2), comment="体长(cm)")
    feed_amount = Column(DECIMAL(10, 2), comment="投喂量(kg)")
    remark = Column(Text, comment="备注")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_fish_type", "fish_type"),
        Index("idx_date", "spawn_date"),
    )

    def __repr__(self):
        return f"<ProductionRecord(id={self.id}, fish_type={self.fish_type}, quantity={self.quantity})>"


class Reminder(Base):
    """
    备忘提醒表
    存储用户的备忘提醒事项
    """

    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="提醒标题")
    content = Column(Text, comment="提醒内容")
    reminder_time = Column(TIMESTAMP, nullable=False, comment="提醒时间")
    is_completed = Column(SmallInteger, default=0, comment="是否完成：1-完成 0-未完成")
    completed_at = Column(TIMESTAMP, comment="完成时间")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_time", "reminder_time"),
        Index("idx_completed", "is_completed"),
    )

    def __repr__(self):
        return f"<Reminder(id={self.id}, title={self.title}, completed={self.is_completed})>"


class User(Base):
    """
    用户表
    存储系统用户信息
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), comment="真实姓名")
    role = Column(String(20), default="operator", comment="角色：admin-管理员，operator-操作员")
    is_active = Column(SmallInteger, default=1, comment="是否启用：1-启用 0-禁用")
    last_login = Column(TIMESTAMP, comment="最后登录时间")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_username", "username"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class Backup(Base):
    """
    备份记录表
    存储数据库备份信息
    """

    __tablename__ = "backups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    backup_type = Column(String(50), nullable=False, comment="备份类型：database/complete")
    file_name = Column(String(255), comment="文件名")
    file_path = Column(String(500), comment="文件路径")
    file_size = Column(Integer, comment="文件大小(字节)")
    backup_time = Column(TIMESTAMP, default=datetime.now, comment="备份时间")
    is_deleted = Column(SmallInteger, default=0, comment="是否已删除：1-已删除 0-未删除")
    remark = Column(String(200), comment="备注")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_time", "backup_time"),
    )

    def __repr__(self):
        return f"<Backup(id={self.id}, type={self.backup_type}, time={self.backup_time})>"


class UserPermission(Base):
    """
    用户权限表
    预留表，用于管理用户权限
    """

    __tablename__ = "user_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")
    permission = Column(String(100), comment="权限标识")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_user", "user_id"),
    )

    def __repr__(self):
        return f"<UserPermission(id={self.id}, user_id={self.user_id}, permission={self.permission})>"
